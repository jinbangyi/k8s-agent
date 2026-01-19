# Cloud Infrastructure Architecture (Jan 16, 2026)

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
| **VPC** | 1 | 10.20.0.0/16 |
| **Subnets** | 6 | DMZ, Apps, DevOps, Database, Audit, Dev |
| **ECS Instances** | 11 | 3 Kong + 1 App + 4 DevOps + 3 DB |
| **Load Balancers** | 2 | Kong LB, K8s API LB |
| **NAT Gateways** | 2 | DMZ (20Mbps), Apps (200Mbps) |
| **Total Resources** | - | 44 vCPU, 176GB RAM, 1.5TB storage |

### Subnet Allocation

| Subnet | CIDR | Instances | Purpose |
|--------|------|-----------|---------|
| **DMZ** | 10.20.1.0/24 | 3x Kong | API Gateway |
| **Apps** | 10.20.2.0/24 | 1x App | Application Server |
| **DevOps** | 10.20.3.0/24 | 3x K8s + 1x CI/CD | K8s control plane |
| **Database** | 10.20.4.0/24 | 3x DB | PostgreSQL/MySQL |
| **Audit** | 10.20.5.0/24 | 0 (reserved) | Audit logging |
| **Development** | 10.20.6.0/24 | 1x Dev | Dev/Test server |

### Public Access Points

| Service | Public EIP | Internal VIP | Ports |
|---------|-----------|--------------|-------|
| Kong API Gateway | 1.2.3.4 | 10.20.1.20 | 8000, 8443 |
| K8s API | 1.2.3.5 | 10.20.3.20 | 6443 |
| Dev Server | 1.2.3.8 | 10.20.6.10 | 22, 8080 |

## Related Documentation

- Original consolidated document: [../26-01-09/cloud-infrastructure-architecture.md](../26-01-09/cloud-infrastructure-architecture.md)
