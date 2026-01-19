# Cloud Infrastructure Architecture (Jan 19, 2026)

This directory contains the reorganized cloud infrastructure architecture documentation for the k8s-agent project on Huawei Cloud.

## Documentation Files

### 1. [Infrastructure Overview](./01-infrastructure-overview.md)
High-level architecture overview, deployment workflows, and verification procedures.

**Contents:**
- Complete infrastructure view (Mermaid diagram)
- Terraform module dependency graph
- Security flow and IAM setup
- Deployment workflow
- Post-deployment verification steps

### 2. [Network Architecture Design](./02-network-architecture.md)
Detailed network topology, NAT gateway configuration, and security rules.

**Contents:**
- Network architecture diagram
- NAT Gateway and Public IP architecture
- Subnet configuration and allocation
- Security group rules hierarchy
- Traffic flow summary
- EIP allocation

### 3. [Component Specifications](./03-component-specifications.md)
Detailed specifications for ECS instances, storage, load balancers, and resource allocation.

**Contents:**
- ECS instance details
- Storage architecture (EVS and OBS)
- Load balancer configuration
- Instance allocation by subnet
- Environment comparison (dev vs prod)
- Complete resource summary

## Quick Reference

### Production Environment Summary

| Resource | Quantity | Specifications |
|----------|----------|----------------|
| **VPC** | 1 | 10.x.0.0/16 |
| **Subnets** | 8 | DMZ (/22), External-Access (/24), Internal-Shared (/22), DevOps-Only (/22), Development-Only (/22), Business-Only (/22), Database-Private (/22), Security-Private (/24) |
| **Route Tables** | 2 | Public (DMZ, External-Access), Private-Egress (all others) |
| **ECS Instances** | 25 | See component specifications |
| **Load Balancers** | 7 | Kong LB (DMZ), Proxy LBs (External-Access), K8s API LB, Internal Services LB |
| **NAT Gateways** | 1 | Single NAT in Internal-Shared, Medium instance type, 200Mbps |
| **Total Resources** | - | 68 vCPU, 272GB RAM, 2.5TB storage |

### Subnet Allocation

| Subnet | CIDR | Instances | Purpose |
|--------|------|-----------|---------|
| **DMZ** | 10.x.0.0/22 | 3 | Kong API Gateway (public-facing) |
| **External-Access** | 10.x.4.0/24 | 5 | Partner services + DB Proxies (Kafka, MongoDB, PG, ES) |
| **Internal-Shared** | 10.x.8.0/22 | 6 | K8s Masters + Loki, Prometheus, GitLab + NAT Gateway |
| **DevOps-Only** | 10.x.12.0/22 | 2 | CI/CD + Build Agents |
| **Development-Only** | 10.x.16.0/22 | 2 | Test Environments + Dev Servers |
| **Business-Only** | 10.x.20.0/22 | 2 | ERP Systems + Business Applications |
| **Database-Private** | 10.x.24.0/22 | 3 | PostgreSQL + Caches (limited egress) |
| **Security-Private** | 10.x.28.0/24 | 2 | Vault + IDS (limited egress) |

### Public Access Points

| Service | Subnet | Public EIP | Ports |
|---------|--------|-----------|-------|
| Kong API Gateway | DMZ | Yes | 8000, 8443 |
| Kafka Proxy | External-Access | Yes | 9092 |
| MongoDB Proxy | External-Access | Yes | 27017 |
| PostgreSQL Proxy | External-Access | Yes | 5432 |
| Elasticsearch Proxy | External-Access | Yes | 9200 |
| K8s API | Internal-Shared | Yes | 6443 |

## Related Documentation

- Original consolidated document: [../26-01-09/cloud-infrastructure-architecture.md](../26-01-09/cloud-infrastructure-architecture.md)
