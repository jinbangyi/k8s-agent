# Cloud Infrastructure Architecture

## Overview

This document provides a visual overview of the Huawei Cloud infrastructure that will be provisioned in Phase 1 of the k8s-agent project.

---

## Complete Infrastructure View

```mermaid
graph TB
    subgraph "Local Machine - Terraform Control"
        Admin[Admin Credentials<br/>AK/SK]
        CLI[huaweicloud CLI]

        subgraph "Step 1: IAM Security Setup"
            CreatePolicy[Create Custom Policy<br/>k8s-agent-infra-policy]
            CreateUser[Create IAM User<br/>k8s-agent-terraform]
            AttachPolicy[Attach Policy to User]
            CreateAK[Create Access Key<br/>Save Credentials!]
            UnsetAdmin[Unset Admin Credentials]
        end

        subgraph "Step 2: Terraform Deploy"
            TFVars[terraform.tfvars<br/>Environment Config]
            TFInit[terraform init]
            TFPlan[terraform plan]
            TFApply[terraform apply]
        end
    end

    subgraph "Huawei Cloud - cn-north-4"
        subgraph "Network Layer"
            VPC[VPC<br/>Name: k8s-agent-cluster-vpc<br/>CIDR: 10.20.0.0/16]

            subgraph "Subnets"
                SubnetDMZ[DMZ Subnet<br/>10.20.1.0/24<br/>Public-facing + NAT]
                SubnetApps[Apps Subnet<br/>10.20.2.0/24<br/>Applications + NAT]
                SubnetDevOps[DevOps Subnet<br/>10.20.3.0/24<br/>CI/CD + Public IPs]
                SubnetDB[Database Subnet<br/>10.20.4.0/24<br/>Databases & Caches]
                SubnetAudit[Audit Subnet<br/>10.20.5.0/24<br/>Audit Resources]
                SubnetDev[Dev Subnet<br/>10.20.6.0/24<br/>Dev/Test + Public IPs]
            end

            subgraph "NAT Gateways"
                NATDMZ[NAT Gateway DMZ<br/>20Mbps EIP]
                NATApps[NAT Gateway Apps<br/>200Mbps EIP]
            end

            subgraph "Security Group Rules"
                SG[Security Groups<br/>k8s-agent-cluster-sg]
                SG_SSH[SSH:22<br/>From: Configurable CIDR]
                SG_API[K8s API:6443<br/>From: VPC CIDR]
                SG_NodePort[NodePort:30000-32767<br/>From: 0.0.0.0/0]
                SG_Linkerd[Linkerd:4143<br/>From: VPC CIDR]
                SG_DevOps[DevOps Services<br/>MongoDB, Kafka, GitLab]
            end
        end

        subgraph "Compute Layer - ECS Instances"
            ECS1[ECS Master-1<br/>s6.xlarge.4<br/>4 vCPU, 16GB RAM<br/>100GB System Disk<br/>100GB Data Disk]
            ECS2[ECS Master-2<br/>s6.xlarge.4<br/>4 vCPU, 16GB RAM<br/>100GB System Disk<br/>100GB Data Disk]
            ECS3[ECS Master-3<br/>s6.xlarge.4<br/>4 vCPU, 16GB RAM<br/>100GB System Disk<br/>100GB Data Disk]

            UserData[cloud-init<br/>Install: curl, wget]
        end

        subgraph "Storage Layer"
            EVS1[(EVS Volume<br/>Attached to Master-1<br/>100GB SAS)]
            EVS2[(EVS Volume<br/>Attached to Master-2<br/>100GB SAS)]
            EVS3[(EVS Volume<br/>Attached to Master-3<br/>100GB SAS)]

            OBS[(OBS Bucket<br/>k8s-agent-prod-xxxx<br/>Lifecycle: 30d expiration)]
        end

        subgraph "Load Balancer"
            ELB[ELB Load Balancer<br/>k8s-agent-cluster-elb<br/>Flavor: L4]
            EIP[Public IP / EIP<br/>100Mbps Bandwidth]
            Listener[Listener<br/>Protocol: TCP<br/>Port: 6443]
            Pool[Backend Pool<br/>Algorithm: Round Robin]
            Members[Backend Members<br/>Master-1: 10.20.2.X<br/>Master-2: 10.20.2.Y<br/>Master-3: 10.20.2.Z]
        end
    end

    subgraph "Terraform State Management"
        TFState[(Terraform State<br/>Stored in OBS)]
        TFOutput[terraform output<br/>outputs.json]
    end

    Admin --> CreatePolicy
    CreatePolicy --> CreateUser
    CreateUser --> AttachPolicy
    AttachPolicy --> CreateAK
    CreateAK --> UnsetAdmin

    UnsetAdmin --> TFVars
    TFVars --> TFInit
    TFInit --> TFPlan
    TFPlan --> TFApply

    TFApply --> VPC
    TFApply --> SubnetDMZ
    TFApply --> SubnetApps
    TFApply --> SubnetDevOps
    TFApply --> SubnetDB
    TFApply --> SubnetAudit
    TFApply --> SubnetDev
    TFApply --> SG
    TFApply --> NATDMZ
    TFApply --> NATApps
    TFApply --> ECS1
    TFApply --> ECS2
    TFApply --> ECS3
    TFApply --> EVS1
    TFApply --> EVS2
    TFApply --> EVS3
    TFApply --> OBS
    TFApply --> ELB

    VPC --> SubnetDMZ
    VPC --> SubnetApps
    VPC --> SubnetDevOps
    VPC --> SubnetDB
    VPC --> SubnetAudit
    VPC --> SubnetDev

    SubnetDMZ --> NATDMZ
    SubnetApps --> NATApps

    SubnetDMZ --> SG
    SubnetApps --> SG
    SubnetDevOps --> SG
    SubnetDB --> SG
    SubnetAudit --> SG
    SubnetDev --> SG

    SG --> SG_SSH
    SG --> SG_API
    SG --> SG_NodePort
    SG --> SG_Linkerd
    SG --> SG_DevOps

    SG --> ECS1
    SG --> ECS2
    SG --> ECS3

    ECS1 --> EVS1
    ECS2 --> EVS2
    ECS3 --> EVS3

    ECS1 --> UserData
    ECS2 --> UserData
    ECS3 --> UserData

    SubnetDMZ --> ELB
    ECS1 --> Members
    ECS2 --> Members
    ECS3 --> Members

    ELB --> EIP
    ELB --> Listener
    Listener --> Pool
    Pool --> Members

    TFApply --> TFState
    TFApply --> TFOutput

    style Admin fill:#ffccbc
    style CreatePolicy fill:#fff9c4
    style VPC fill:#e3f2fd
    style SubnetDMZ fill:#ffebee
    style SubnetApps fill:#c8e6c9
    style SubnetDevOps fill:#fff3e0
    style SubnetDB fill:#e1f5fe
    style SubnetAudit fill:#f3e5f5
    style SubnetDev fill:#fff9c4
    style SG fill:#ffebee
    style NATDMZ fill:#e1f5fe
    style NATApps fill:#c8e6c9
    style ECS1 fill:#c8e6c9
    style ECS2 fill:#c8e6c9
    style ECS3 fill:#c8e6c9
    style EVS1 fill:#e1f5fe
    style EVS2 fill:#e1f5fe
    style EVS3 fill:#e1f5fe
    style OBS fill:#f3e5f5
    style ELB fill:#fff3e0
```

---

## Module Dependency Graph

```mermaid
graph LR
    subgraph "Terraform Modules"
        VPCModule[VPC Module]
        SubnetModule[Subnet Module]
        SGModule[Security Group Module]
        NATModule[NAT Gateway Module]
        EIPModule[EIP Module]
        SNATModule[SNAT Rule Module]
        ECSModule[ECS Module]
        StorageModule[Storage Module]
        ELBModule[ELB Module]
    end

    subgraph "Dependencies"
        VPCModule -->|vpc_id| SubnetModule
        VPCModule -->|vpc_id| SGModule
        VPCModule -->|vpc_id| NATModule
        VPCModule -->|vpc_id| ECSModule
        VPCModule -->|vpc_id| ELBModule

        SubnetModule -->|subnet_id| NATModule
        SubnetModule -->|subnet_id| ECSModule
        SubnetModule -->|subnet_id| ELBModule

        SGModule -->|sg_id| ECSModule

        NATModule -->|nat_id| EIPModule
        NATModule -->|nat_id| SNATModule

        EIPModule -->|eip_id| SNATModule

        ECSModule -->|private_ips| ELBModule
    end

    style VPCModule fill:#e3f2fd
    style SubnetModule fill:#e8f5e9
    style SGModule fill:#ffebee
    style NATModule fill:#fff3e0
    style EIPModule fill:#e1f5fe
    style SNATModule fill:#c8e6c9
    style ECSModule fill:#c8e6c9
    style StorageModule fill:#e1f5fe
    style ELBModule fill:#fff3e0
```

---

## Security Flow Diagram

```mermaid
sequenceDiagram
    participant Admin as Admin User
    participant CLI as huaweicloud CLI
    participant IAM as Huawei Cloud IAM
    participant Terraform as Terraform
    participant Cloud as Huawei Cloud Resources

    Note over Admin,Cloud: Phase 1: Create Restricted IAM User
    Admin->>CLI: Set Admin Credentials
    Admin->>CLI: Create Custom Policy
    CLI->>IAM: POST /policies
    IAM-->>CLI: Policy Created

    Admin->>CLI: Create IAM User
    CLI->>IAM: POST /users
    IAM-->>CLI: User Created

    Admin->>CLI: Attach Policy to User
    CLI->>IAM: PUT /users/policies
    IAM-->>CLI: Policy Attached

    Admin->>CLI: Create Access Key
    CLI->>IAM: POST /access-keys
    IAM-->>Admin: Access Key & Secret<br/>(SAVE THESE!)

    Admin->>Admin: Unset Admin Credentials

    Note over Admin,Cloud: Phase 2: Deploy with Restricted Token
    Admin->>Terraform: Set Restricted Token Env Vars
    Terraform->>Cloud: Deploy Resources
    Cloud-->>Terraform: Resource IDs & IPs
    Terraform-->>Admin: outputs.json
```

---

## Network Architecture

```mermaid
graph TB
    subgraph "Internet"
        Internet2[Internet / Public Network]
        EIP[Public IP / EIP<br/>100Mbps]
    end

    subgraph "VPC: 10.20.0.0/16"
        subgraph "DMZ Subnet: 10.20.1.0/24"
            GatewayDMZ[Gateway<br/>10.20.1.1]
            LB[Load Balancer<br/>10.20.1.20]
            NATDMZ[NAT Gateway<br/>20Mbps EIP]
        end

        subgraph "Apps Subnet: 10.20.2.0/24"
            GatewayApps[Gateway<br/>10.20.2.1]
            NATApps[NAT Gateway<br/>200Mbps EIP]

            subgraph "Security Group: k8s-agent-cluster-sg"
                IngressRules[Ingress Rules]

                subgraph "ECS Instances"
                    M1[Master-1<br/>10.20.2.10]
                    M2[Master-2<br/>10.20.2.11]
                    M3[Master-3<br/>10.20.2.12]
                end
            end
        end

        subgraph "DevOps Subnet: 10.20.3.0/24"
            GatewayDevOps[Gateway<br/>10.20.3.1]
            DevOpsPublic[Public IPs Direct<br/>Security Groups]

            subgraph "DevOps Services"
                GitLab[GitLab<br/>Public IP]
                MongoDB[MongoDB<br/>Public IP]
                Kafka[Kafka<br/>Public IP]
            end
        end

        subgraph "Database Subnet: 10.20.4.0/24"
            GatewayDB[Gateway<br/>10.20.4.1]
            DBResources[Databases & Caches]
        end

        subgraph "Audit Subnet: 10.20.5.0/24"
            GatewayAudit[Gateway<br/>10.20.5.1]
            AuditResources[Audit Log Collectors]
        end

        subgraph "Development Subnet: 10.20.6.0/24"
            GatewayDev[Gateway<br/>10.20.6.1]
            DevPublic[Public IPs Direct<br/>Flexible Security]
            DevResources[Dev/Test Servers]
        end
    end

    subgraph "Security Rules"
        SSH[Port 22<br/>SSH Access]
        API[Port 6443<br/>K8s API]
        NP[Port 30000-32767<br/>NodePort]
        LM[Port 4143<br/>Linkerd Mesh]
        DevOpsSG[DevOps Services<br/>MongoDB:27017<br/>Kafka:9092<br/>GitLab:22,80,443]
    end

    Internet --> EIP
    EIP --> LB

    GatewayApps --> M1
    GatewayApps --> M2
    GatewayApps --> M3

    LB --> M1
    LB --> M2
    LB --> M3

    NATApps --> M1
    NATApps --> M2
    NATApps --> M3

    IngressRules --> SSH
    IngressRules --> API
    IngressRules --> NP
    IngressRules --> LM

    SSH --> M1
    SSH --> M2
    SSH --> M3

    API --> M1
    API --> M2
    API --> M3

    NP --> M1
    NP --> M2
    NP --> M3

    LM --> M1
    LM --> M2
    LM --> M3

    GatewayDevOps --> GitLab
    GatewayDevOps --> MongoDB
    GatewayDevOps --> Kafka
    DevOpsPublic --> DevOpsSG

    GatewayDB --> DBResources
    GatewayAudit --> AuditResources
    GatewayDev --> DevResources
    DevPublic --> DevResources

    style Internet fill:#e3f2fd
    style VPC fill:#f3e5f5
    style LB fill:#fff3e0
    style NATDMZ fill:#e1f5fe
    style NATApps fill:#c8e6c9
    style M1 fill:#c8e6c9
    style M2 fill:#c8e6c9
    style M3 fill:#c8e6c9
    style IngressRules fill:#ffebee
    style GitLab fill:#fff3e0
    style MongoDB fill:#fff3e0
    style Kafka fill:#fff3e0
```

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
            VPCNet[VPC Network<br/>10.0.0.0/16]
            SubnetNet[Subnet Network<br/>10.0.1.0/24]
            PrivateIP[Private IP<br/>10.0.1.X]
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
            M1[Master-1<br/>10.0.1.10:6443]
            M2[Master-2<br/>10.0.1.11:6443]
            M3[Master-3<br/>10.0.1.12:6443]
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

## Deployment Workflow

```mermaid
flowchart TD
    Start([Start Deployment]) --> CheckAdmin{Admin<br/>Credentials<br/>Set?}
    CheckAdmin -->|No| SetAdmin[Set HUAWEI_ADMIN_AK<br/>Set HUAWEI_ADMIN_SK]
    SetAdmin --> CreatePolicy

    CheckAdmin -->|Yes| CreatePolicy[Create IAM Policy:<br/>k8s-agent-infra-policy]

    CreatePolicy --> CreateUser[Create IAM User:<br/>k8s-agent-terraform]
    CreateUser --> AttachPolicy[Attach Policy to User]
    AttachPolicy --> CreateAK[Create Access Key]
    CreateAK --> SaveCreds[SAVE CREDENTIALS!<br/>Access Key ID<br/>Secret Access Key]
    SaveCreds --> UnsetAdmin[Unset Admin Credentials]

    UnsetAdmin --> CheckRestricted{Restricted<br/>Credentials<br/>Set?}
    CheckRestricted -->|No| SetRestricted[Set HUAWEICLOUD_ACCESS_KEY_ID<br/>Set HUAWEICLOUD_SECRET_ACCESS_KEY]
    SetRestricted --> TFInit

    CheckRestricted -->|Yes| TFInit[terraform init]
    TFInit --> TFValidate[terraform validate]
    TFValidate --> TFPlan[terraform plan]

    TFPlan --> Review{Review Plan}
    Review -->|Cancel| End([End])
    Review -->|Approve| TFApply[terraform apply]

    TFApply --> SaveOutput[Save outputs.json]
    SaveOutput --> Verify{Verify<br/>Deployment}

    Verify -->|Failed| Rollback[terraform destroy]
    Rollback --> End

    Verify -->|Success| TestConnect[Test Connectivity:<br/>SSH to Masters<br/>Ping ELB]
    TestConnect --> End

    style Start fill:#c8e6c9
    style End fill:#ffebee
    style SaveCreds fill:#ffccbc
    style TFApply fill:#c8e6c9
    style Rollback fill:#ffebee
```

---

## Verification Steps

```mermaid
graph TB
    subgraph "Post-Deployment Verification"
        V1[1. Verify ECS Instances]
        V2[2. Verify VPC Configuration]
        V3[3. Verify Storage Provisioning]
        V4[4. Verify Load Balancer]
        V5[5. Test Connectivity]
    end

    subgraph "ECS Checks"
        ECS1A[ssh ubuntu@<public-ip>]
        ECS1B[Check: Instances Running]
        ECS1C[Check: cloud-init Complete]
    end

    subgraph "VPC Checks"
        VPC2A[huaweicloud vpc show <vpc-id>]
        VPC2B[Check: CIDR Correct]
        VPC2C[Check: Subnet Attached]
    end

    subgraph "Storage Checks"
        ST3A[huaweicloud evs volume show <volume-id>]
        ST3B[huaweicloud obs bucket list]
        ST3C[Check: EVS Attached]
        ST3D[Check: OBS Created]
    end

    subgraph "ELB Checks"
        ELB4A[huaweicloud elb show <elb-id>]
        ELB4B[Check: Backend Members]
        ELB4C[Check: Listener Active]
    end

    subgraph "Connectivity Tests"
        CONN5A[ping <master-ip>]
        CONN5B[curl -k https://<elb-address>:6443]
        CONN5C[Check: SSH Access]
        CONN5D[Check: API Reachable]
    end

    V1 --> ECS1A
    V1 --> ECS1B
    V1 --> ECS1C

    V2 --> VPC2A
    V2 --> VPC2B
    V2 --> VPC2C

    V3 --> ST3A
    V3 --> ST3B
    V3 --> ST3C
    V3 --> ST3D

    V4 --> ELB4A
    V4 --> ELB4B
    V4 --> ELB4C

    V5 --> CONN5A
    V5 --> CONN5B
    V5 --> CONN5C
    V5 --> CONN5D

    style V1 fill:#c8e6c9
    style V2 fill:#c8e6c9
    style V3 fill:#c8e6c9
    style V4 fill:#c8e6c9
    style V5 fill:#c8e6c9
```

---

## Resource Summary

### Development Environment

| Resource Type | Quantity | Specifications |
|---------------|----------|----------------|
| **VPC** | 1 | 10.10.0.0/16 |
| **Subnets** | 6 | DMZ, Apps, DevOps, Database, Audit, Dev (each /24) |
| **Security Group** | 1 | SSH, K8s API, NodePort |
| **ECS Instances** | 1 | s6.large.4 (2 vCPU, 8GB RAM) |
| **System Disk** | 1 | 100GB SAS per instance |
| **Data Disk** | 1 | 50GB SAS |
| **OBS Bucket** | 1 | Globally unique name |
| **ELB** | 1 | L4 load balancer (in DMZ subnet) |

**Subnet Breakdown:**
- DMZ: 10.10.1.0/24 (public-facing resources)
- Apps: 10.10.2.0/24 (application servers)
- DevOps: 10.10.3.0/24 (CI/CD and config management)
- Database: 10.10.4.0/24 (databases and caches)
- Audit: 10.10.5.0/24 (audit resources)
- Dev: 10.10.6.0/24 (dev/test resources)

**Total Resources**: 2 vCPU, 8GB RAM, 250GB storage

### Production Environment

| Resource Type | Quantity | Specifications |
|---------------|----------|----------------|
| **VPC** | 1 | 10.20.0.0/16 |
| **Subnets** | 6 | DMZ, Apps, DevOps, Database, Audit, Dev (each /24) |
| **Security Group** | 1 | SSH, K8s API, NodePort, Linkerd |
| **ECS Instances** | 3 | s6.xlarge.4 (4 vCPU, 16GB RAM) |
| **System Disk** | 3 | 100GB SAS per instance |
| **Data Disk** | 3 | 200GB SAS |
| **OBS Bucket** | 1 | Globally unique name |
| **ELB** | 1 | L4 load balancer, 2 AZs (in DMZ subnet) |

**Subnet Breakdown:**
- DMZ: 10.20.1.0/24 (public-facing resources - load balancers, web servers)
- Apps: 10.20.2.0/24 (application servers and microservices)
- DevOps: 10.20.3.0/24 (CI/CD servers and configuration management)
- Database: 10.20.4.0/24 (database servers and caches)
- Audit: 10.20.5.0/24 (audit log collectors and processors)
- Dev: 10.20.6.0/24 (development and test servers)

**Total Resources**: 12 vCPU, 48GB RAM, 900GB storage

---

## Related Documentation

- [Cloud Infrastructure Plan](./01-cloud-infrastructure-plan.md) - Detailed implementation guide
- [K8s Platform Plan](./02-k8s-platform-plan.md) - Phase 2: Kubernetes setup
- [Architecture Overview](./00-architecture-overview.md) - Complete system architecture
