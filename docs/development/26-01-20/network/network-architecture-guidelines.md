# Network Architecture Guidelines

## Overview

This document provides comprehensive guidelines for the network architecture of the k8s-agent project. It covers VPC design, subnet allocation, security groups, and connectivity patterns to ensure a secure, scalable, and maintainable infrastructure.

## VPC Architecture

### Primary VPC
- **Name**: `k8s-agent-cluster-vpc`
- **CIDR Block**: `10.x.0.0/16`
- **Region**: `ap-southeast-3` (Jakarta)
- **Availability Zones**: `ap-southeast-3a`, `ap-southeast-3b` (for production)

### Design Principles
1. **Isolation**: Separate subnets for different resource types
2. **Security**: Public-facing resources in DMZ, private resources in isolated subnets
3. **Scalability**: Sufficient IP address space for future growth
4. **High Availability**: Multi-AZ deployment for critical resources

## Subnet Design

### Subnet Categorization

The VPC is divided into 8 distinct subnets, each with specific purposes and security controls:

| Subnet Name | CIDR Block | Purpose | Access Type |
|-------------|------------|---------|-------------|
| **DMZ Subnet** | `10.x.0.0/22` | Public-facing resources (Kong API Gateway, load balancers, proxies) | Public + NAT Gateway |
| **External-Access Subnet** | `10.x.4.0/22` | Partner-facing services | Public IP |
| **Internal-Shared Subnet** | `10.x.8.0/22` | Shared resources (Kubernetes masters, Loki, Prometheus, GitLab) | NAT Gateway |
| **DevOps-Only Subnet** | `10.x.12.0/22` | DevOps team exclusive resources (CI/CD, build agents) | NAT Gateway |
| **Development-Only Subnet** | `10.x.16.0/22` | Development team exclusive resources (test environments, dev servers) | NAT Gateway |
| **Business-Only Subnet** | `10.x.20.0/22` | Business/Operations team exclusive resources (ERP systems, business applications) | NAT Gateway |
| **Database-Private Subnet** | `10.x.24.0/22` | Database resources (PostgreSQL/RDS, caches) | Private (no direct internet) |
| **Security-Private Subnet** | `10.x.28.0/22` | Security-critical resources (Vault, intrusion detection) | Private (no direct internet) |

### Subnet Details

#### 1. DMZ Subnet (10.x.0.0/22)
- **Purpose**: Public-facing API gateway and ingress routing
- **Resources**: 3x Kong API Gateway instances (s6.large.4) + 4x proxies (Kafka, MongoDB, PostgreSQL, Elasticsearch)
- **Load Balancer**: Kong LB (Ports: 8000, 8443), Proxy LBs (Ports: 9092, 27017, 5432, 9200)
- **Internet Access**: Public Network Gateway for inbound, NAT Gateway for outbound
- **Security**: Restricted inbound access, public IP via load balancers

#### 2. External-Access Subnet (10.x.4.0/22)
- **Purpose**: Partner-facing services
- **Resources**: 1x Partner Service instance (s6.large.4)
- **Internet Access**: Public Network Gateway
- **Security**: Public IP with security group controls

#### 3. Internal-Shared Subnet (10.x.8.0/22)
- **Purpose**: Kubernetes control plane and shared services
- **Resources**:
  - 3x Kubernetes Masters (s6.xlarge.4)
  - 1x Loki Logging (s6.large.4)
  - 1x Prometheus Monitoring (s6.large.4)
  - 1x GitLab (s6.large.4)
- **Load Balancer**: K8s API LB (Port: 6443), Internal Services LB (Ports: 80, 443)
- **Internet Access**: NAT Gateway
- **Security**: Private subnet, internal load balancer access

#### 4. DevOps-Only Subnet (10.x.12.0/22)
- **Purpose**: DevOps team exclusive resources
- **Resources**: 1x CI/CD Server (s6.large.4) + 1x Build Agents (s6.large.4)
- **Internet Access**: NAT Gateway
- **Security**: Isolated subnet, restricted to DevOps team only

#### 5. Development-Only Subnet (10.x.16.0/22)
- **Purpose**: Development team exclusive resources
- **Resources**: 1x Test Environments (s6.large.4) + 1x Dev Servers (s6.large.4)
- **Internet Access**: NAT Gateway
- **Security**: Isolated subnet, restricted to Development team only

#### 6. Business-Only Subnet (10.x.20.0/22)
- **Purpose**: Business/Operations team exclusive resources
- **Resources**: 1x ERP Systems (s6.large.4) + 1x Business Applications (s6.large.4)
- **Internet Access**: NAT Gateway
- **Security**: Isolated subnet, restricted to Business team only

#### 7. Database-Private Subnet (10.x.24.0/22)
- **Purpose**: Database clusters with replication
- **Resources**: 1x Self-Hosted PostgreSQL (s6.xlarge.4) + 1x Cloud PostgreSQL/RDS (s6.xlarge.4) + 1x Caches (s6.large.4)
- **Internet Access**: Private subnet, no direct internet access
- **Security**: Isolated from public internet, restricted access

#### 8. Security-Private Subnet (10.x.28.0/22)
- **Purpose**: Security-critical resources
- **Resources**: 1x Vault (s6.large.4) + 1x Intrusion Detection (s6.large.4)
- **Internet Access**: Private subnet, no direct internet access
- **Security**: Isolated subnet with minimal access

## Internet Access Strategy

### Hybrid Approach
The infrastructure uses a hybrid internet access strategy to balance security and flexibility:

| Subnet | Access Method | Bandwidth | Use Case |
|--------|---------------|-----------|----------|
| **DMZ** | Public Network Gateway | - | Public-facing resources with direct internet access |
| **External-Access** | Public Network Gateway | - | Partner-facing services with direct internet access |
| **Internal-Shared** | NAT Gateway (Medium) | 200Mbps | Shared resources requiring outbound internet access |
| **DevOps-Only** | NAT Gateway (Medium) | 200Mbps | DevOps resources requiring outbound internet access |
| **Development-Only** | NAT Gateway (Medium) | 200Mbps | Development resources requiring outbound internet access |
| **Business-Only** | NAT Gateway (Medium) | 200Mbps | Business/Operations resources requiring outbound internet access |
| **Database-Private** | Private | None | Isolated, no direct internet access |
| **Security-Private** | Private | None | Isolated, no direct internet access |

### NAT Gateway Benefits
- **Static Public IPs**: Easy whitelisting in external services
- **Cost Control**: Pay-by-traffic billing
- **Security**: Private subnets remain isolated
- **Simplified Management**: Single EIP per NAT gateway for all associated subnets

### Public IP Benefits
- **Direct Access**: Public-facing services accessible without DNAT
- **Flexibility**: Custom security rules per service
- **Development**: Easy testing and debugging
- **Security**: Fine-grained security group control

## Load Balancer Configuration

### Kong API Gateway LB
- **Name**: `k8s-agent-kong-elb`
- **Subnet**: DMZ (10.x.0.0/22)
- **VIP**: -
- **Public EIP**: -
- **Ports**: 8000 (HTTP), 8443 (HTTPS)
- **Backend Pool**: 3x Kong Gateway instances
- **Algorithm**: Round Robin

### Kafka Proxy LB
- **Name**: `k8s-agent-kafka-elb`
- **Subnet**: DMZ (10.x.0.0/22)
- **VIP**: -
- **Public EIP**: -
- **Port**: 9092
- **Backend Pool**: 1x Kafka Proxy
- **Algorithm**: Round Robin

### MongoDB Proxy LB
- **Name**: `k8s-agent-mongo-elb`
- **Subnet**: DMZ (10.x.0.0/22)
- **VIP**: -
- **Public EIP**: -
- **Port**: 27017
- **Backend Pool**: 1x MongoDB Proxy
- **Algorithm**: Round Robin

### PostgreSQL Proxy LB
- **Name**: `k8s-agent-pg-elb`
- **Subnet**: DMZ (10.x.0.0/22)
- **VIP**: -
- **Public EIP**: -
- **Port**: 5432
- **Backend Pool**: 1x PostgreSQL Proxy
- **Algorithm**: Round Robin

### Elasticsearch Proxy LB
- **Name**: `k8s-agent-es-elb`
- **Subnet**: DMZ (10.x.0.0/22)
- **VIP**: -
- **Public EIP**: -
- **Port**: 9200
- **Backend Pool**: 1x Elasticsearch Proxy
- **Algorithm**: Round Robin

### Kubernetes API LB
- **Name**: `k8s-agent-k8s-elb`
- **Subnet**: Internal-Shared (10.x.8.0/22)
- **VIP**: -
- **Public EIP**: -
- **Port**: 6443
- **Backend Pool**: 3x Kubernetes Masters
- **Algorithm**: Round Robin

### Internal Services LB
- **Name**: `k8s-agent-internal-elb`
- **Subnet**: Internal-Shared (10.x.8.0/22)
- **VIP**: -
- **Public EIP**: -
- **Ports**: 80 (HTTP), 443 (HTTPS)
- **Backend Pool**: Internal applications
- **Algorithm**: Round Robin

## Security Group Rules

### VPC-Level Security Group (`k8s-agent-cluster-sg`)
Applies to all instances in the cluster:

| Rule | Protocol | Port Range | Source | Purpose |
|------|----------|------------|--------|---------|
| SSH | TCP | 22 | Configurable CIDR | Secure shell access |
| ICMP | ICMP | All | VPC CIDR (10.x.0.0/16) | Ping and network diagnostics |

### Subnet-Level Security Groups

#### DMZ Subnet Security Group
Additional rules for DMZ subnet resources:

| Rule | Protocol | Port Range | Source | Purpose |
|------|----------|------------|--------|---------|
| HTTP/HTTPS | TCP | 80, 443 | 0.0.0.0/0 | Public web traffic |
| API Gateway | TCP | 8000, 8443 | 0.0.0.0/0 | Kong API access |

#### Internal-Shared Subnet Security Group
Additional rules for internal-shared subnet resources:

| Rule | Protocol | Port Range | Source | Purpose |
|------|----------|------------|--------|---------|
| K8s API | TCP | 6443 | VPC CIDR (10.x.0.0/16) | Kubernetes API access |
| Loki | TCP | 3100 | VPC CIDR (10.x.0.0/16) | Logging access |
| Prometheus | TCP | 9090 | VPC CIDR (10.x.0.0/16) | Monitoring access |

#### Database-Private Subnet Security Group
Additional rules for database-private subnet resources:

| Rule | Protocol | Port Range | Source | Purpose |
|------|----------|------------|--------|---------|
| PostgreSQL | TCP | 5432 | VPC CIDR (10.x.0.0/16) | Database access |

#### Security-Private Subnet Security Group
Additional rules for security-private subnet resources:

| Rule | Protocol | Port Range | Source | Purpose |
|------|----------|------------|--------|---------|
| Vault | TCP | 8200 | Restricted CIDR | Secret management |

### Instance-Level Security Groups
Each ECS instance will have its own security group with additional service-specific rules.

## IP Address Allocation

IP addresses are dynamically assigned by the cloud service and managed by Kubernetes internal DNS for service discovery. Predefined IP ranges are not specified.

## Traffic Flow

### Inbound Traffic
```
Internet → Public Network Gateway → Load Balancer → Target Instance
```

- **API Traffic**: Internet → DMZ Subnet → Kong LB → Kong Gateways
- **Proxy Traffic**: Internet → DMZ Subnet → Proxy LBs → Internal Services
- **Partner Traffic**: Internet → External-Access Subnet → Partner Services
- **K8s API Traffic**: Internet → Internal-Shared Subnet → K8s API LB → K8s Masters

### Outbound Traffic
```
Instance → [NAT Gateway or Direct EIP] → Internet
```

- **DMZ Outbound**: Kong Gateways → Public Network Gateway → Internet
- **External-Access Outbound**: Partner Services → Public Network Gateway → Internet
- **Internal Outbound**: Internal Resources → NAT Gateway → Internet
- **Database Outbound**: No direct internet access
- **Security Outbound**: No direct internet access

### Internal Traffic
All internal traffic remains within the VPC CIDR range (10.x.0.0/16) using private IP addresses.

## Network Security Guidelines

### 1. Subnet Isolation
- Keep public-facing resources in DMZ subnet
- Keep databases and sensitive resources in private subnets
- Use security groups to restrict cross-subnet traffic

### 2. Access Control
- Restrict SSH access to known IP addresses
- Use IAM policies for fine-grained access control
- Implement network ACLs for additional security layers

### 3. Whitelisting
- Whitelist NAT Gateway public IPs in external services
- Use security groups to whitelist allowed source IPs
- Regularly review and update whitelists

### 4. Logging and Monitoring
- Enable VPC flow logs
- Monitor network traffic patterns
- Set up alerts for unusual traffic

## Best Practices

### 1. Network Design
- Use private subnets for sensitive resources
- Implement multi-AZ deployment for high availability
- Design for scalability with sufficient IP address space

### 2. Security
- Follow least privilege principle for security groups
- Regularly audit security group rules
- Use encryption for data in transit and at rest

### 3. Management
- Document all network changes
- Use infrastructure as code (Terraform)
- Implement change management processes

### 4. Performance
- Use appropriate instance types for network-intensive workloads
- Monitor bandwidth usage
- Optimize traffic routing

## Related Documentation

- [Cloud Infrastructure Architecture](./cloud-infrastructure-architecture.md) - Comprehensive diagrams and architecture
- [Cloud Infrastructure Plan](./01-cloud-infrastructure-plan.md) - Terraform implementation details
- [K8s Platform Plan](./02-k8s-platform-plan.md) - Kubernetes setup and configuration
