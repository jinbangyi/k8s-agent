## Network Rules and Guidelines
- region should use `ap-southeast-3`
- vpc rules:
  - vpc cidr should use `10.x.0.0/16` format, where x is unique per environment
- nat gateway rules:
  - use single NAT gateway (medium instance) in Internal-Shared subnet
  - SNAT rules for different subnet groups:
    - Internal-Shared: 10.x.8.0/22
    - Team Subnets: 10.x.12.0/22, 10.x.16.0/22, 10.x.20.0/22
    - Private Limited: 10.x.24.0/22, 10.x.28.0/24 (package updates, NTP only)
  - multi EIP binded for different SNAT rules to NAT gateway for outbound internet access
- subnet rules:
  - /22 for high-density subnets: DMZ, Internal-Shared, DevOps, Development, Business, Database-Private
  - /24 for low-density subnets: External-Access, Security-Private
- security group rules:
  - use workload-based security groups (sg-web-servers, sg-api-gateway, sg-databases, etc.)
  - all ecs has common default security group
  - each vpc has its own security group
- eip rules:
  - NAT gateway uses EIP for outbound internet
  - Private subnets egress via NAT Gateway with SNAT rules
  - public network gateway should use eip
- lb rules:
  - each public lb should use unique eip
  - Public Load Balancer: in DMZ subnet(api gateway,web servers etc.)
  - external Load Balancer: in External-Access subnet(partner-facing services,db proxies,proxy for internal kafka,mongodb etc.)
  - Internal Load Balancer: in Internal-Shared subnet(k8s master api,squid proxy etc.)

### Route Table Grouping (Simplified)

- Simplified route table grouping (3 route tables):
  - **Public Route Table**: for internet-facing subnets (DMZ, External-Access)
  - **Private-Egress Route Table**: for all subnets requiring NAT egress (Internal-Shared, DevOps-Only, Development-Only, Business-Only, Database-Private, Security-Private)
  - Note: Private-Isolated route table removed - Database-Private and Security-Private now have limited egress via NAT with security group restrictions

### Subnet (Categorized by User Access Patterns)

- the subnet should split into multi categories based on user access patterns:
  - DMZ subnet: for public-facing resources accessible from internet (web servers, load balancers, etc.)
  - external-access subnet: for resources accessible from external partners or vendors
  - internal-shared subnet: for resources shared across all internal teams (logging servers, monitoring servers, configuration management, etc.)
  - devops-only subnet: for DevOps team exclusive resources (CI/CD servers, build agents, etc.)
  - development-only subnet: for Development team exclusive resources (dev servers, test environments, etc.)
  - business-only subnet: for Business/Operations team exclusive resources (ERP systems, business applications, etc.)
  - database-private subnet: for database resources with restricted access (self-hosted PostgreSQL, cloud-based PostgreSQL/RDS, caches, etc.)
  - security-private subnet: for security-critical resources with minimal access (vault, intrusion detection systems, etc.)

- resources in shared subnets should expose services via internal load balancers with appropriate ACL restrictions
- exclusive subnets should have strict security group rules limiting access to their respective teams
