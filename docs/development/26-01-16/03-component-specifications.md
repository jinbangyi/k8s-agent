# Component Specifications

## Overview

This document provides detailed specifications for all infrastructure components including ECS instances, storage, load balancers, and resource allocation.

---

## ECS Instance Detail

```mermaid
graph TB
    subgraph "ECS Master Instance"
        subgraph "Hardware"
            Flavor[Flavor: s6.xlarge.4<br/>4 vCPU / 16GB RAM]
            AZ[Availability Zone<br/>cn-north-4a]
        end

        subgraph "Storage"
            SystemDisk[System Disk<br/>100GB SAS<br/>Debian 13 Image]
            DataDisk[Data Disk<br/>100GB SAS<br/>EVS Volume]
        end

        subgraph "Network"
            VPCNet[VPC Network<br/>10.20.0.0/16]
            SubnetNet[Subnet Network<br/>10.20.3.0/24]
            PrivateIP[Private IP<br/>10.20.3.X]
            PublicIP[Public IP<br/>EIP]
        end

        subgraph "Security"
            SecGroup[Security Group<br/>k8s-agent-cluster-sg]
            Rules[Ingress Rules:<br/>SSH:22, API:6443,<br/>NodePort:30000-32767]
        end

        subgraph "Initialization"
            CloudInit[cloud-init User Data]
            Packages[Install Packages:<br/>curl, wget]
        end

        subgraph "Tags"
            NameTag[Name: k8s-agent-cluster-master-N]
            EnvTag[Environment: production]
            ManagedTag[ManagedBy: terraform]
        end
    end

    Flavor --> SystemDisk
    Flavor --> DataDisk

    VPCNet --> SubnetNet
    SubnetNet --> PrivateIP

    SecGroup --> Rules
    SecGroup --> PrivateIP

    CloudInit --> Packages
    SystemDisk --> CloudInit

    style Flavor fill:#e1f5fe
    style SystemDisk fill:#c8e6c9
    style DataDisk fill:#c8e6c9
    style VPCNet fill:#f3e5f5
    style SecGroup fill:#ffebee
    style CloudInit fill:#fff3e0
```

---

## Storage Architecture

```mermaid
graph TB
    subgraph "EVS Block Storage"
        EVS1[(EVS Volume 1<br/>100GB SAS<br/>AZ: cn-north-4a<br/>Attached: Master-1)]
        EVS2[(EVS Volume 2<br/>100GB SAS<br/>AZ: cn-north-4a<br/>Attached: Master-2)]
        EVS3[(EVS Volume 3<br/>100GB SAS<br/>AZ: cn-north-4a<br/>Attached: Master-3)]
    end

    subgraph "OBS Object Storage"
        OBSBucket[OBS Bucket<br/>k8s-agent-prod-xxxx]

        subgraph "Lifecycle Rules"
            Expiration[Object Expiration<br/>30 days]
            NonCurrent[Non-Current Versions<br/>90 days]
        end

        subgraph "Stored Objects"
            TFState[Terraform State<br/>terraform.tfstate]
            Backup[Infrastructure Backups]
            Logs[Deployment Logs]
        end
    end

    subgraph "ECS System Disks"
        Sys1[Master-1 System<br/>100GB SAS]
        Sys2[Master-2 System<br/>100GB SAS]
        Sys3[Master-3 System<br/>100GB SAS]
    end

    EVS1 -->|Attached| Sys1
    EVS2 -->|Attached| Sys2
    EVS3 -->|Attached| Sys3

    OBSBucket --> Expiration
    OBSBucket --> NonCurrent
    OBSBucket --> TFState
    OBSBucket --> Backup
    OBSBucket --> Logs

    style EVS1 fill:#e1f5fe
    style EVS2 fill:#e1f5fe
    style EVS3 fill:#e1f5fe
    style OBSBucket fill:#f3e5f5
    style Sys1 fill:#c8e6c9
    style Sys2 fill:#c8e6c9
    style Sys3 fill:#c8e6c9
```

---

## Load Balancer Configuration

```mermaid
graph TB
    subgraph "External Access"
        Client[Clients / Users]
        Internet[Internet]
        EIP[Public IP<br/>Elastic IP]
    end

    subgraph "ELB Load Balancer"
        ELB[L4 Load Balancer<br/>k8s-agent-cluster-elb]

        subgraph "Frontend"
            Listener[Listener<br/>Protocol: TCP<br/>Port: 6443]
        end

        subgraph "Backend Configuration"
            Pool[Backend Pool<br/>Algorithm: ROUND_ROBIN<br/>Protocol: TCP]
        end

        subgraph "Backend Members"
            M1[Master-1<br/>10.20.3.10:6443]
            M2[Master-2<br/>10.20.3.11:6443]
            M3[Master-3<br/>10.20.3.12:6443]
        end
    end

    subgraph "Kubernetes API"
        K8sAPI[K8s API Server<br/>Port 6443]
    end

    Client --> Internet
    Internet --> EIP
    EIP --> ELB

    ELB --> Listener
    Listener --> Pool
    Pool --> M1
    Pool --> M2
    Pool --> M3

    M1 --> K8sAPI
    M2 --> K8sAPI
    M3 --> K8sAPI

    style Client fill:#e3f2fd
    style EIP fill:#fff3e0
    style ELB fill:#fff3e0
    style Pool fill:#e8f5e9
    style K8sAPI fill:#c8e6c9
```

---

## ECS Instance Allocation by Subnet

### Overview

The infrastructure allocates ECS instances across subnets based on their purpose and availability requirements:

| Subnet | Purpose | Instance Count | Instance Type | Network Access |
|--------|---------|----------------|---------------|----------------|
| **DMZ** | Kong API Gateway | 3 | s6.large.4 | Public IP + NAT Gateway + Dedicated LB |
| **Apps** | Application Server | 1 | s6.large.4 (dev) / s6.xlarge.4 (prod) | NAT Gateway |
| **DevOps** | K8s Masters + CI/CD | 4 | 3x s6.xlarge.4 (K8s) + 1x s6.large.4 (CI/CD) | Public IP (direct) + Dedicated LB for K8s |
| **Database** | Database Clusters | 3 | s6.large.4 (dev) / s6.xlarge.4 (prod) | Private (no internet) |
| **Development** | Dev/Test Server | 1 | s6.large.4 | Public IP (direct) |
| **Audit** | Audit Logging | 0 | - | Reserved for future |

### DMZ Subnet (3x Kong API Gateway + Dedicated LB)

```
Purpose: API Gateway and ingress routing
Instances: 3x s6.large.4 (2 vCPU, 8GB RAM, 100GB SAS)
Network: 10.20.1.0/24
Load Balancer: Kong LB (Port 8000, 8443)
Access: Public IP with security group controls
```

**Why 3 instances?**
- High availability for API gateway
- Dedicated load balancer distributes traffic across all 3
- Can handle failures without service disruption
- Kong provides API management, authentication, and rate limiting

### Apps Subnet (1x Application Server)

```
Purpose: Application workloads
Instances: 1x s6.large.4 (2 vCPU, 8GB RAM, 100GB SAS)
Network: 10.20.2.0/24
Access: NAT Gateway for outbound internet
```

**Why 1 instance?**
- Application server for business workloads
- Can scale horizontally by adding more instances
- NAT Gateway provides secure outbound access
- Isolated from K8s control plane

### DevOps Subnet (4x: 3 K8s Masters + 1 CI/CD Server + K8s LB)

```
Purpose: Kubernetes control plane + CI/CD tools
Instances:
  - 3x K8s Masters: s6.xlarge.4 (4 vCPU, 16GB RAM, 100GB SAS each)
  - 1x CI/CD Server: s6.large.4 (2 vCPU, 8GB RAM, 100GB SAS)
Network: 10.20.3.0/24
Load Balancer: K8s API LB (Port 6443)
Access: Public IP (direct) with security group controls
```

**Why 4 instances?**
- **3 K8s Masters**: High availability control plane (quorum-based etcd)
  - Automatic failover if master fails
  - Distributed API server load
  - etcd clustering for data redundancy
- **1 CI/CD Server**: Consolidates DevOps tools (GitLab, Jenkins)
  - Public IP allows external Git access
  - Security groups restrict access to specific ports

### Database Subnet (3x Database Replicas)

```
Purpose: PostgreSQL/MySQL with replication
Instances: 3x s6.xlarge.4 (4 vCPU, 16GB RAM, 200GB SAS each)
Network: 10.20.4.0/24
Access: Private (no direct internet access)
```

**Why 3 instances?**
- Database replication for high availability
- Automatic failover if primary fails
- Distributed read operations
- Isolated subnet for security (no internet access)

### Development Subnet (1x Dev Server)

```
Purpose: Development and testing
Instances: 1x s6.large.4 (2 vCPU, 8GB RAM, 100GB SAS)
Network: 10.20.6.0/24
Access: Public IP with flexible security
```

**Why 1 instance?**
- Dedicated server for development/testing
- Public IP for easy remote access
- Flexible security rules for experimentation
- Isolated from production resources

### Audit Subnet (0 instances - Reserved)

```
Purpose: Audit logging and monitoring (future)
Instances: 0 (reserved for future)
Network: 10.20.5.0/24
Access: TBD
```

---

## IP Address Allocation

| Subnet | Gateway | Instance IPs | Load Balancer |
|--------|---------|--------------|---------------|
| DMZ (10.20.1.0/24) | 10.20.1.1 | 10.20.1.10, 10.20.1.11, 10.20.1.12 (Kong) | 10.20.1.20 (Kong LB) |
| Apps (10.20.2.0/24) | 10.20.2.1 | 10.20.2.10 (App Server) | - |
| DevOps (10.20.3.0/24) | 10.20.3.1 | 10.20.3.10-12 (K8s Masters), 10.20.3.30 (CI/CD) | 10.20.3.20 (K8s API LB) |
| Database (10.20.4.0/24) | 10.20.4.1 | 10.20.4.10, 10.20.4.11, 10.20.4.12 (DB) | - |
| Audit (10.20.5.0/24) | 10.20.5.1 | (reserved) | - |
| Development (10.20.6.0/24) | 10.20.6.1 | 10.20.6.10 (Dev Server) | - |

---

## Load Balancer Configuration

| Load Balancer | Subnet | VIP IP | Public EIP | Backend Port | Backend Instances |
|---------------|--------|--------|-----------|--------------|-------------------|
| **Kong LB** | DMZ (10.20.1.0/24) | 10.20.1.20 | 1.2.3.4 (100Mbps) | 8000, 8443 | Kong Gateway-1,2,3 (10.20.1.10-12) |
| **K8s API LB** | DevOps (10.20.3.0/24) | 10.20.3.20 | 1.2.3.5 (100Mbps) | 6443 | K8s Master-1,2,3 (10.20.3.10-12) |

---

## NAT Gateway Configuration

| NAT Gateway | Subnet | Internal IP | Public EIP | Bandwidth | Serves Subnets |
|-------------|--------|-------------|-----------|-----------|----------------|
| **NAT DMZ** | DMZ (10.20.1.0/24) | 10.20.1.2 | 1.2.3.6 (20Mbps) | 20Mbps | DMZ (Kong Gateways) |
| **NAT Apps** | Apps (10.20.2.0/24) | 10.20.2.2 | 1.2.3.7 (200Mbps) | 200Mbps | Apps (Application Server) |

---

## Environment Configuration Comparison

```mermaid
graph TB
    subgraph "Development Environment"
        DevName[Cluster: k8s-agent-dev]
        DevRegion[Region: cn-north-4]
        DevAZ[AZ: cn-north-4a]
        DevNodes[Nodes: 1x s6.large.4<br/>2 vCPU, 8GB RAM]
        DevStorage[Storage: 50GB]
        DevVPC[VPC: 10.10.0.0/16]
        DevSubnets[Subnets: 6x /24<br/>10.10.1.0-10.10.6.0]
        DevSSH[SSH: 0.0.0.0/0]
    end

    subgraph "Production Environment"
        ProdName[Cluster: k8s-agent-prod]
        ProdRegion[Region: cn-north-4]
        ProdAZ[AZ: cn-north-4a, cn-north-4b]
        ProdNodes[Nodes: 3x s6.xlarge.4<br/>4 vCPU, 16GB RAM]
        ProdStorage[Storage: 200GB]
        ProdVPC[VPC: 10.20.0.0/16]
        ProdSubnets[Subnets: 6x /24<br/>10.20.1.0-10.20.6.0]
        ProdSSH[SSH: Office IP/32]
    end

    style DevName fill:#fff9c4
    style DevNodes fill:#fff9c4
    style DevStorage fill:#fff9c4
    style ProdName fill:#c8e6c9
    style ProdNodes fill:#c8e6c9
    style ProdStorage fill:#c8e6c9
```

| Parameter | Development | Production |
|-----------|-------------|------------|
| **Cluster Name** | k8s-agent-dev | k8s-agent-prod |
| **Region** | cn-north-4 | cn-north-4 |
| **Availability Zones** | cn-north-4a | cn-north-4a, cn-north-4b |
| **Instance Count** | 1 | 3 |
| **Instance Type** | s6.large.4 (2 vCPU, 8GB) | s6.xlarge.4 (4 vCPU, 16GB) |
| **System Disk** | 100GB SAS | 100GB SAS |
| **Data Disk** | 50GB SAS | 200GB SAS |
| **VPC CIDR** | 10.10.0.0/16 | 10.20.0.0/16 |
| **DMZ Subnet** | 10.10.1.0/24 (public-facing) | 10.20.1.0/24 (public-facing) |
| **Apps Subnet** | 10.10.2.0/24 (applications) | 10.20.2.0/24 (applications) |
| **DevOps Subnet** | 10.10.3.0/24 (CI/CD) | 10.20.3.0/24 (CI/CD) |
| **Database Subnet** | 10.10.4.0/24 (databases) | 10.20.4.0/24 (databases) |
| **Audit Subnet** | 10.10.5.0/24 (audit) | 10.20.5.0/24 (audit) |
| **Dev Subnet** | 10.10.6.0/24 (dev/test) | 10.20.6.0/24 (dev/test) |
| **SSH Access** | 0.0.0.0/0 | Office IP/32 |

---

## Resource Summary

### Development Environment

| Resource Type | Quantity | Specifications |
|---------------|----------|----------------|
| **VPC** | 1 | 10.10.0.0/16 |
| **Subnets** | 6 | DMZ, Apps, DevOps, Database, Audit, Dev (each /24) |
| **NAT Gateways** | 2 | DMZ (300Mbps), Apps (300Mbps) |
| **Security Groups** | 2 | Cluster SG, DevOps SG (MongoDB, Kafka, GitLab) |
| **ECS Instances** | 11 | Total across all subnets (see breakdown) |
| **ELB** | 2 | Kong LB (DMZ), K8s API LB (DevOps) |
| **OBS Bucket** | 1 | Globally unique name |

**ECS Instance Allocation by Subnet:**

| Subnet | Instance Count | Type | Specifications | Purpose |
|--------|----------------|------|----------------|---------|
| **DMZ** | 3 | s6.large.4 | 2 vCPU, 8GB RAM, 100GB SAS each | Kong API Gateway (3x HA) |
| **Apps** | 2 | s6.large.4 | 2 vCPU, 8GB RAM, 50GB SAS | Application Server |
| **DevOps** | 4 | 3x s6.xlarge.4 + 1x s6.large.4 | K8s: 4 vCPU, 16GB RAM; CI/CD: 2 vCPU, 8GB RAM | 3x K8s Masters + 1x CI/CD |
| **Database** | 3 | s6.large.4 | 2 vCPU, 8GB RAM, 100GB SAS each | PostgreSQL/MySQL (3x replication) |
| **Development** | 2 | s6.large.4 | 2 vCPU, 8GB RAM, 50GB SAS | Development/testing server |
| **Audit** | 0 | - | - | (No instances, reserved for future) |

**Total Resources**: 26 vCPU, 104GB RAM, 1.05TB storage

### Production Environment

| Resource Type | Quantity | Specifications |
|---------------|----------|----------------|
| **VPC** | 1 | 10.20.0.0/16 |
| **Subnets** | 6 | DMZ, Apps, DevOps, Database, Audit, Dev (each /24) |
| **NAT Gateways** | 2 | DMZ (20Mbps), Apps (200Mbps) |
| **Security Groups** | 2 | Cluster SG, DevOps SG (MongoDB, Kafka, GitLab) |
| **ECS Instances** | 11 | Total across all subnets (see breakdown) |
| **ELB** | 2 | Kong LB (DMZ), K8s API LB (DevOps) |
| **OBS Bucket** | 1 | Globally unique name |

**ECS Instance Allocation by Subnet:**

| Subnet | Instance Count | Type | Specifications | Purpose |
|--------|----------------|------|----------------|---------|
| **DMZ** | 3 | s6.large.4 | 2 vCPU, 8GB RAM, 100GB SAS each | Kong API Gateway (3x HA) |
| **Apps** | 1 | s6.xlarge.4 | 4 vCPU, 16GB RAM, 100GB SAS | Application Server (production grade) |
| **DevOps** | 4 | 3x s6.xlarge.4 + 1x s6.large.4 | K8s: 4 vCPU, 16GB RAM; CI/CD: 2 vCPU, 8GB RAM | 3x K8s Masters + 1x CI/CD |
| **Database** | 3 | s6.xlarge.4 | 4 vCPU, 16GB RAM, 200GB SAS each | PostgreSQL/MySQL (3x replication) |
| **Development** | 1 | s6.large.4 | 2 vCPU, 8GB RAM, 100GB SAS | Development/testing server |
| **Audit** | 0 | - | - | (No instances, reserved for future) |

**Total Resources**: 44 vCPU, 176GB RAM, 1.5TB storage

---

## Related Documentation

- [Infrastructure Overview](./01-infrastructure-overview.md) - High-level architecture and deployment
- [Network Architecture Design](./02-network-architecture.md) - Network topology, NAT gateways, and security rules
