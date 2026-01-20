# Network Flows

## Overview

This document describes the golden traffic flows for the k8s-agent network infrastructure.

---

## Golden Flows

### Flow 1: Internet to Application (Public Ingress)

```
Internet
    ↓ (HTTPS :443)
Public Network Gateway
    ↓ (DMZ subnet - 10.x.0.0/22)
Public Load Balancer (EIP)
    ↓ (HTTP :8080, target: app servers)
App Servers (Business-Only - 10.x.20.0/22)
    ↓ (PostgreSQL :5432)
PostgreSQL (Database-Private - 10.x.24.0/22)
```

**Key points:**
- Public LB SG allows: `0.0.0.0/0:443`
- App SG allows: `Public LB SG:8080`
- DB SG allows: `App SG:5432`
- No NAT involved (ingress traffic path)

**Use cases:**
- User API requests
- Web application access
- Public service endpoints

---

### Flow 2: Private Egress (Package Updates)

```
App Server (Business-Only - 10.x.20.0/22)
    ↓ (default route 0.0.0.0/0)
NAT Gateway (Internal-Shared - 10.x.8.0/22)
    ↓ (via EIP, SNAT rule for 10.x.20.0/22)
Internet
    ↓ (repository.example.com)
Package Repository (apt/yum/pip)
```

**Key points:**
- App server has no public IP
- Uses single NAT Gateway for outbound internet access
- SNAT rule maps source CIDR to NAT EIP
- Return traffic follows reverse path via NAT

**Use cases:**
- System package updates (apt, yum)
- Python package installation (pip)
- Security updates and patches

---

### Flow 3: Cross-VPC Access (Dev to Prod Peering)

```
Debug Instance (dev VPC - 10.21.0.0/16)
    ↓ (route: 10.20.0.0/16 via peering)
VPC Peering Connection
    ↓ (prod Database-Private subnet)
PostgreSQL (prod VPC - 10.20.0.0/16)
```

**Configuration requirements:**
- dev team route table: `10.20.0.0/16 → peering`
- prod private route table: `10.21.0.0/16 → peering`
- prod DB SG: allow `10.21.0.0/16:5432`
- dev App SG: allow outbound to `10.20.0.0/16:5432`

**Use cases:**
- Development accessing production databases for debugging
- Cross-environment data replication
- Testing against production-like data

---

## Additional Flow Patterns

### Internal Service to Service

```
App Server (Business-Only - 10.x.20.0/22)
    ↓
Internal Load Balancer (Internal-Shared - 10.x.8.0/22)
    ↓
Loki/Prometheus/GitLab (Internal-Shared - 10.x.8.0/22)
```

**Use cases:**
- Application logging to Loki
- Metrics export to Prometheus
- CI/CD operations with GitLab

### Partner Access

```
Partner Network
    ↓ (HTTPS :443, whitelisted IP)
Public Network Gateway
    ↓ (External-Access subnet - 10.x.4.0/24)
DB Proxies (Kafka/Mongo/PG/ES)
    ↓
Internal Databases (Database-Private - 10.x.24.0/22)
```

**Use cases:**
- Partner Kafka access via proxy
- Partner MongoDB queries via proxy
- Partner PostgreSQL queries via proxy
- Partner Elasticsearch queries via proxy

### Kubernetes API Access

```
DevOps Workstation (Internet/VPN)
    ↓
Internal Load Balancer (Internal-Shared - 10.x.8.0/22)
    ↓ (HTTPS :6443)
Kubernetes Master Nodes (Internal-Shared - 10.x.8.0/22)
```

**Use cases:**
- kubectl commands from dev workstations
- Kubernetes API access for deployments
- Cluster management operations

---

## Traffic Flow Summary

| Source | Destination | Path | EIP Used |
|--------|-------------|------|----------|
| Internet | Public Services | Internet → PGW → DMZ → Public LB → Services | Per LB EIP |
| Internet | Partner Services | Internet → PGW → External-Access → Partner Services | Per service EIP |
| Internal Services | Internet | Internal → NAT Gateway → EIP → Internet | NAT Gateway EIP |
| DMZ Services | Internal Services | DMZ → Internal-Shared → Internal Services | - |
| Team Resources | Shared Resources | Team Subnets → Internal-Shared → Shared Resources | - |
| All Resources | Database | Any Subnet → Database-Private → Databases | - |
| Dev VPC | Prod DB | Dev → Peering → Prod Database-Private | - |

---

## Security Group Flow Reference

| Flow | Source SG | Destination SG | Allowed Ports |
|------|-----------|----------------|---------------|
| Internet → Public LB | 0.0.0.0/0 | sg-public-lb | 443 |
| Public LB → App | sg-public-lb | sg-app | 8080 |
| App → Database | sg-app | sg-database | 5432 |
| App → NAT | sg-app | sg-nat | All (egress) |
| Dev → Prod DB | sg-dev-app | sg-prod-db | 5432 |

---

## Related Documentation

- [Architecture](./network-architecture.md) - Visual architecture diagrams
- [Specifications](./network-specifications.md) - Detailed technical specifications
- [Guidelines](./network-guidelines.md) - Design rules and best practices
- [User Rules](../user.md) - High-level network rules
