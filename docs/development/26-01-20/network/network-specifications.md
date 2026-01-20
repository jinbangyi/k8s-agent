## Subnet Specifications

**Environment:** Development | **VPC CIDR:** `10.21.0.0/16` | **Region:** `ap-southeast-3`

> **Note:** This VPC is for development environment. Production will use a separate VPC (`10.20.0.0/16`).

### Public-Facing Subnets

| Category | CIDR | AZ | Route Table | Default Route | Inbound Sources | Example Workloads |
|----------|------|----|-------------|---------------|-----------------|-------------------|
| DMZ | 10.21.0.0/22 | 3a, 3b | Public | PGW | Internet (0.0.0.0/0) | Public LBs, API Gateway, Web Servers |
| External-Access | 10.21.4.0/24 | 3a | Public | PGW | Partner VPNs, Whitelisted IPs | Partner-facing services, DB Proxies (Kafka/Mongo/PG/ES) |

### Internal Shared Subnets

| Category | CIDR | AZ | Route Table | Default Route | Inbound Sources | Example Workloads |
|----------|------|----|-------------|---------------|-----------------|-------------------|
| Internal-Shared | 10.21.8.0/22 | 3a, 3b | Internal-Shared | NAT1 | All internal subnets via SG | Internal LBs, Loki, Prometheus, GitLab |

### Team-Exclusive Subnets

| Category | CIDR | AZ | Route Table | Default Route | Inbound Sources | Example Workloads |
|----------|------|----|-------------|---------------|-----------------|-------------------|
| DevOps-Only | 10.21.12.0/22 | 3a | Team | NAT2 | DevOps team SGs | CI/CD servers, Build agents |
| Development-Only | 10.21.16.0/22 | 3a | Team | NAT2 | Dev team SGs | Debug instances, Test pods, Developer workstations |
| Business-Only | 10.21.20.0/22 | 3a, 3b | Team | NAT2 | Business team SGs, Internal LB | Application servers, ERP systems, Business apps |

### Private Restricted Subnets

| Category | CIDR | AZ | Route Table | Default Route | Inbound Sources | Example Workloads |
|----------|------|----|-------------|---------------|-----------------|-------------------|
| Database-Private | 10.21.24.0/22 | 3a, 3b | Private-Egress | NAT (limited) | App subnets via SG, Peered VPCs | PostgreSQL (self-hosted/RDS), Redis |
| Security-Private | 10.21.28.0/24 | 3a | Private-Egress | NAT (limited) | Security team SGs only | Vault, Intrusion Detection, HSM |

**Limited Egress** for Database-Private and Security-Private:
- Allowed: Package repositories (apt, pypi), NTP servers, Cloud API endpoints
- Security group outbound rules restrict to specific destinations only

### Route Table Summary

| Route Table | Associated Subnets | Default Route (0.0.0.0/0) |
|-------------|-------------------|---------------------------|
| Public | DMZ, External-Access | Public Network Gateway |
| Private-Egress | Internal-Shared, DevOps-Only, Development-Only, Business-Only, Database-Private, Security-Private | NAT Gateway (in Internal-Shared subnet) |

### SNAT Rules Configuration

| SNAT Rule | Source CIDR | EIP | Purpose |
|-----------|-------------|-----|---------|
| Internal-Shared | 10.x.8.0/22 | EIP-NAT | Shared services egress |
| Team Subnets | 10.x.12.0/22, 10.x.16.0/22, 10.x.20.0/22 | EIP-NAT | Team resources egress |
| Private Limited | 10.x.24.0/22, 10.x.28.0/24 | EIP-NAT | Package updates, NTP only |