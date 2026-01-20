# Network Specifications

## Overview

This document contains detailed technical specifications for the k8s-agent network infrastructure.

---

## VPC Configuration

| Parameter | Value |
|-----------|-------|
| **VPC Name** | k8s-agent-cluster-vpc |
| **Region** | ap-southeast-3 |
| **Availability Zones** | ap-southeast-3a, ap-southeast-3b |

### VPC CIDR Allocation

| Environment | VPC CIDR |
|-------------|----------|
| Production | 10.20.0.0/16 |
| Development | 10.21.0.0/16 |

---

## Subnet Specifications

### Subnet Allocation Pattern

| Subnet Category | CIDR Pattern | Size | AZ Distribution |
|-----------------|--------------|------|-----------------|
| DMZ | 10.x.0.0/22 | /22 (1022 hosts) | 3a, 3b |
| External-Access | 10.x.4.0/24 | /24 (250 hosts) | 3a |
| Internal-Shared | 10.x.8.0/22 | /22 (1022 hosts) | 3a, 3b |
| DevOps-Only | 10.x.12.0/22 | /22 (1022 hosts) | 3a |
| Development-Only | 10.x.16.0/22 | /22 (1022 hosts) | 3a |
| Business-Only | 10.x.20.0/22 | /22 (1022 hosts) | 3a, 3b |
| Database-Private | 10.x.24.0/22 | /22 (1022 hosts) | 3a, 3b |
| Security-Private | 10.x.28.0/24 | /24 (250 hosts) | 3a |

### Development Environment Subnets (10.21.0.0/16)

| Category | CIDR | Gateway | Route Table | Default Route | Internet Access |
|----------|------|---------|-------------|---------------|-----------------|
| DMZ | 10.21.0.0/22 | 10.21.0.1 | Public | Public Network Gateway | Direct (Public IP) |
| External-Access | 10.21.4.0/24 | 10.21.4.1 | Public | Public Network Gateway | Direct (Public IP) |
| Internal-Shared | 10.21.8.0/22 | 10.21.8.1 | Private-Egress | NAT Gateway | NAT (SNAT) |
| DevOps-Only | 10.21.12.0/22 | 10.21.12.1 | Private-Egress | NAT Gateway | NAT (SNAT) |
| Development-Only | 10.21.16.0/22 | 10.21.16.1 | Private-Egress | NAT Gateway | NAT (SNAT) |
| Business-Only | 10.21.20.0/22 | 10.21.20.1 | Private-Egress | NAT Gateway | NAT (SNAT) |
| Database-Private | 10.21.24.0/22 | 10.21.24.1 | Private-Egress | NAT Gateway | NAT (limited) |
| Security-Private | 10.21.28.0/24 | 10.21.28.1 | Private-Egress | NAT Gateway | NAT (limited) |

### Production Environment Subnets (10.20.0.0/16)

| Category | CIDR | Gateway | Route Table | Default Route | Internet Access |
|----------|------|---------|-------------|---------------|-----------------|
| DMZ | 10.20.0.0/22 | 10.20.0.1 | Public | Public Network Gateway | Direct (Public IP) |
| External-Access | 10.20.4.0/24 | 10.20.4.1 | Public | Public Network Gateway | Direct (Public IP) |
| Internal-Shared | 10.20.8.0/22 | 10.20.8.1 | Private-Egress | NAT Gateway | NAT (SNAT) |
| DevOps-Only | 10.20.12.0/22 | 10.20.12.1 | Private-Egress | NAT Gateway | NAT (SNAT) |
| Development-Only | 10.20.16.0/22 | 10.20.16.1 | Private-Egress | NAT Gateway | NAT (SNAT) |
| Business-Only | 10.20.20.0/22 | 10.20.20.1 | Private-Egress | NAT Gateway | NAT (SNAT) |
| Database-Private | 10.20.24.0/22 | 10.20.24.1 | Private-Egress | NAT Gateway | NAT (limited) |
| Security-Private | 10.20.28.0/24 | 10.20.28.1 | Private-Egress | NAT Gateway | NAT (limited) |

---

## Route Table Configuration

### Route Table Association

| Route Table | Associated Subnets | Default Route (0.0.0.0/0) |
|-------------|-------------------|---------------------------|
| **Public** | DMZ, External-Access | Public Network Gateway |
| **Private-Egress** | Internal-Shared, DevOps-Only, Development-Only, Business-Only, Database-Private, Security-Private | NAT Gateway |

### SNAT Rules

| SNAT Rule | Source CIDR | EIP | Purpose |
|-----------|-------------|-----|---------|
| Internal-Shared | 10.x.8.0/22 | EIP-NAT | Shared services egress |
| Team Subnets | 10.x.12.0/22, 10.x.16.0/22, 10.x.20.0/22 | EIP-NAT | Team resources egress |
| Private Limited | 10.x.24.0/22, 10.x.28.0/24 | EIP-NAT | Package updates, NTP only |

### Limited Egress (Database-Private, Security-Private)

| Destination | Port | Purpose |
|-------------|------|---------|
| Package repositories (apt, pypi) | 80, 443 | System updates |
| NTP servers | 123 | Time synchronization |
| Cloud API endpoints | 443 | Cloud service access |
| **All other 0.0.0.0/0** | **Deny** | No unrestricted egress |

---

## Load Balancer Specifications

### Public Load Balancers (DMZ Subnet)

| Load Balancer | Type | Backend | Ports | Protocol |
|---------------|------|---------|-------|----------|
| Kong API Gateway | TCP | Kong Gateway instances | 8000, 8443 | HTTP, HTTPS |
| Kafka Proxy | TCP | Kafka Proxy | 9092 | Kafka Protocol |
| MongoDB Proxy | TCP | MongoDB Proxy | 27017 | MongoDB Protocol |
| PostgreSQL Proxy | TCP | PostgreSQL Proxy | 5432 | PostgreSQL Protocol |
| Elasticsearch Proxy | TCP | Elasticsearch Proxy | 9200 | HTTP |

### Internal Load Balancers (Internal-Shared Subnet)

| Load Balancer | Type | Backend | Ports | Protocol |
|---------------|------|---------|-------|----------|
| Kubernetes API | TCP | K8s Master nodes | 6443 | HTTPS |
| Internal Services | HTTP/HTTPS | Internal applications | 80, 443 | HTTP, HTTPS |

### Load Balancer Naming Convention

```
k8s-agent-{service}-elb
```

Examples:
- `k8s-agent-kong-elb` - Kong API Gateway load balancer
- `k8s-agent-k8s-elb` - Kubernetes API load balancer
- `k8s-agent-internal-elb` - Internal services load balancer

---

## NAT Gateway Configuration

| Parameter | Value |
|-----------|-------|
| **Location** | Internal-Shared Subnet (10.x.8.0/22) |
| **Type** | Medium (200Mbps) |
| **EIP** | Single EIP with multiple SNAT rules |
| **Bandwidth** | 200Mbps |

---

## IP Address Planning

### Gateway IP Assignment

Each subnet uses the first usable IP address as its gateway:

| Subnet | Gateway IP |
|--------|------------|
| 10.x.0.0/22 | 10.x.0.1 |
| 10.x.4.0/24 | 10.x.4.1 |
| 10.x.8.0/22 | 10.x.8.1 |
| 10.x.12.0/22 | 10.x.12.1 |
| 10.x.16.0/22 | 10.x.16.1 |
| 10.x.20.0/22 | 10.x.20.1 |
| 10.x.24.0/22 | 10.x.24.1 |
| 10.x.28.0/24 | 10.x.28.1 |

### Reserved IP Ranges

| Range | Purpose |
|-------|---------|
| First IP (.1) | Subnet Gateway |
| Last IP (.broadcast) | Network Broadcast |

---

## Related Documentation

- [Architecture](./network-architecture.md) - Visual architecture diagrams
- [Guidelines](./network-guidelines.md) - Design rules and best practices
- [Flows](./network-flows.md) - Traffic flow examples
- [User Rules](../user.md) - High-level network rules
