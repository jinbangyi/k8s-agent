# Network Guidelines

## Overview

This document provides the design rules, principles, and best practices for the k8s-agent network infrastructure.

---

## Design Principles

### 1. Isolation
- Separate subnets for different resource types and access patterns
- Public-facing resources isolated from private resources
- Sensitive resources (databases, security tools) in isolated subnets

### 2. Security
- Least privilege access for all security groups
- Defense in depth with multiple security layers
- Minimal internet exposure for private subnets

### 3. Scalability
- Sufficient IP address space for growth (/16 VPC CIDR)
- Consistent subnet sizing patterns
- Multi-AZ deployment for high availability

### 4. Simplicity
- Single NAT gateway for cost efficiency
- Workload-based security groups
- Clear, predictable routing patterns

---

## VPC Rules

### CIDR Format
- Use `10.x.0.0/16` format where `x` is unique per environment
- Production: `10.20.0.0/16`
- Development: `10.21.0.0/16`

### Region
- Always use `ap-southeast-3` (Jakarta)

### Multi-VPC Pattern
- Use separate VPCs for production and development
- Enable VPC peering for cross-environment access when needed

---

## Subnet Rules

### Subnet Size Selection

| Subnet Type | CIDR Size | Use Case |
|-------------|-----------|----------|
| High-density | /22 (1022 hosts) | DMZ, Internal-Shared, DevOps, Development, Business, Database |
| Low-density | /24 (250 hosts) | External-Access, Security-Private |

### Subnet Categories by Access Pattern

| Category | Purpose | Example Workloads |
|----------|---------|-------------------|
| **DMZ** | Public-facing resources accessible from internet | Public LBs, API Gateway, Web Servers |
| **External-Access** | Resources accessible from external partners | Partner-facing services, DB proxies |
| **Internal-Shared** | Resources shared across all internal teams | Internal LBs, Loki, Prometheus, GitLab |
| **DevOps-Only** | DevOps team exclusive resources | CI/CD servers, Build agents |
| **Development-Only** | Development team exclusive resources | Dev servers, Test environments |
| **Business-Only** | Business/Operations team exclusive resources | Business applications, ERP systems |
| **Database-Private** | Database resources with restricted access | PostgreSQL (self-hosted/RDS), Redis |
| **Security-Private** | Security-critical resources with minimal access | Vault, Intrusion Detection, HSM |

### Subnet Placement Guidelines

1. **Public-Facing Services** → DMZ subnet
2. **Partner Services** → External-Access subnet
3. **Shared Infrastructure** → Internal-Shared subnet
4. **Team-Specific Resources** → Respective team-only subnet
5. **Databases** → Database-Private subnet
6. **Secrets/Security Tools** → Security-Private subnet

---

## NAT Gateway Rules

### Configuration
- Use **single NAT gateway** (medium instance) in Internal-Shared subnet
- Location: Internal-Shared subnet (10.x.8.0/22)
- Type: Medium (200Mbps)
- EIP: Single EIP with multiple SNAT rules

### SNAT Rules

| Source CIDR | Purpose |
|-------------|---------|
| 10.x.8.0/22 (Internal-Shared) | Shared services egress |
| 10.x.12.0/22, 10.x.16.0/22, 10.x.20.0/22 (Team Subnets) | Team resources egress |
| 10.x.24.0/22, 10.x.28.0/24 (Private Limited) | Package updates, NTP only |

### Limited Egress (Database-Private, Security-Private)
- Security group outbound rules restrict to specific destinations only
- Allowed: Package repositories (apt, pypi), NTP servers, Cloud API endpoints
- Denied: All other 0.0.0.0/0 traffic

---

## EIP Rules

### EIP Allocation
- **NAT Gateway**: Uses EIP for outbound internet access
- **Public Load Balancers**: Each public LB should use unique EIP
- **Public Network Gateway**: Public-facing resources use EIP

### EIP Usage Pattern
- Single NAT Gateway EIP for all private subnet egress
- Unique EIP per public load balancer
- Direct EIP for services requiring public IP (partner services, dev servers)

---

## Load Balancer Rules

### Load Balancer Placement

| LB Type | Subnet | Use Case |
|---------|--------|----------|
| Public Load Balancer | DMZ | API Gateway, Web Servers |
| External Load Balancer | External-Access | Partner-facing services, DB proxies |
| Internal Load Balancer | Internal-Shared | K8s master API, Internal services |

### Load Balancer Naming
```
k8s-agent-{service}-elb
```

### Load Balancer Backend Selection
- Public LB → Resources in DMZ subnet
- External LB → Resources in External-Access subnet
- Internal LB → Resources in internal subnets

---

## Route Table Rules

### Route Table Types

| Route Table | Associated Subnets | Default Route |
|-------------|-------------------|---------------|
| Public | DMZ, External-Access | Public Network Gateway |
| Private-Egress | Internal-Shared, DevOps-Only, Development-Only, Business-Only, Database-Private, Security-Private | NAT Gateway |

### Route Table Assignment
- Public-facing subnets → Public Route Table
- Internal subnets with internet access → Private-Egress Route Table
- Isolated subnets (no internet) → Private-Egress Route Table (with limited SG rules)

---

## Security Group Rules

### Security Group Hierarchy

1. **VPC-Level Security Group** (Common base rules)
2. **Subnet-Level Security Groups** (Additional subnet-specific rules)
3. **Instance-Level Security Groups** (Service-specific rules)

### Base Rules (All Security Groups)

| Rule | Port | Source | Purpose |
|------|------|--------|---------|
| SSH | 22 | Configurable CIDR | Administrative access |
| ICMP | All | VPC CIDR | Network connectivity testing |

### Workload-Based Security Groups

| Security Group | Purpose | Inbound Rules |
|----------------|---------|---------------|
| sg-web-servers | Public-facing web servers | 80, 443 from 0.0.0.0/0 |
| sg-api-gateway | Kong/API services | 8000, 8443 from 0.0.0.0/0 |
| sg-db-proxies | Database proxy services | 9092, 27017, 5432, 9200 from whitelisted IPs |
| sg-databases | Database instances | 5432, 6379 from app security groups |
| sg-monitoring | Loki, Prometheus | 3100, 9090 from VPC CIDR |
| sg-devops | CI/CD, Build agents | 22 from bastion, 8080 internal |
| sg-security | Vault, IDS | 8200 from restricted CIDR |

### Security Group Rules

1. Each VPC has its own security group
2. All ECS instances have common default security group
3. Use workload-based security groups (sg-web-servers, sg-api-gateway, sg-databases, etc.)
4. Follow least privilege principle
5. Regularly audit and update rules

---

## VPC Peering Rules

### When to Use VPC Peering
- Development environment needs access to production databases
- Cross-environment resource sharing is required
- Separate environments need controlled communication

### Peering Configuration
1. Create VPC peering connection between VPCs
2. Update route tables in both VPCs
3. Configure security group rules for cross-VPC traffic
4. Use specific CIDR ranges in security group rules

### Example: Dev to Prod Peering
- dev route table: `10.20.0.0/16 → peering`
- prod route table: `10.21.0.0/16 → peering`
- prod DB SG: allow `10.21.0.0/16:5432`
- dev App SG: allow outbound to `10.20.0.0/16:5432`

---

## Best Practices

### Network Design
1. Use private subnets for sensitive resources
2. Implement multi-AZ deployment for high availability
3. Design for scalability with sufficient IP address space
4. Use consistent subnet sizing patterns

### Security
1. Follow least privilege principle for security groups
2. Regularly audit security group rules
3. Use encryption for data in transit and at rest
4. Enable VPC flow logs for monitoring

### Management
1. Document all network changes
2. Use infrastructure as code (Terraform)
3. Implement change management processes
4. Monitor bandwidth usage and optimize routing

### Performance
1. Use appropriate instance types for network-intensive workloads
2. Monitor bandwidth usage
3. Optimize traffic routing
4. Use load balancers for distribution

---

## Related Documentation

- [Architecture](./network-architecture.md) - Visual architecture diagrams
- [Specifications](./network-specifications.md) - Detailed technical specifications
- [Flows](./network-flows.md) - Traffic flow examples
- [User Rules](../user.md) - High-level network rules
