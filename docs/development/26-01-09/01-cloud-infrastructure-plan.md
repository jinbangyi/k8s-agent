# Phase 1: Cloud Infrastructure Setup

## Overview
Initialize the base cloud infrastructure on Huawei Cloud including ECS instances, networking, storage, and load balancers.

---

## 1.1 Huawei Cloud Infrastructure

### Prerequisites
- Huawei Cloud account with appropriate permissions
- Admin access key (AK/SK) for initial IAM setup
- Region selection (e.g., cn-north-4)
- Terraform 1.6+ installed locally
- huaweicloud CLI tool installed

### Security: Token Setup (IMPORTANT - Do This First!)

**Step 1: Create Restricted IAM Token**

Before running any Terraform, create a restricted token with only necessary permissions:

```bash
# Save your admin token temporarily
export HUAWEI_ADMIN_AK="<your-admin-access-key>"
export HUAWEI_ADMIN_SK="<your-admin-secret-key>"

# Create IAM policy for k8s-agent infrastructure
cat > k8s-agent-infra-policy.json << 'EOF'
{
  "Version": "1.1",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecs:instances:*",
        "ecs:cloudservers:*",
        "vpc:*",
        "vpc:securityGroups:*",
        "vpc:securityGroupRules:*",
        "evs:volumes:*",
        "evs:volumeAttachments:*",
        "obs:bucket:*",
        "obs:object:*",
        "elb:*",
        "iam:users:*",
        "iam:accessKeys:*"
      ],
      "Resource": [
        "*"
      ]
    }
  ]
}
EOF

# Create custom policy using admin credentials
huaweicloud iam create-policy \
  --policy-name k8s-agent-infra-policy \
  --policy-document file://k8s-agent-infra-policy.json

# Create a dedicated user for infrastructure automation
huaweicloud iam create-user \
  --user-name k8s-agent-terraform \
  --password-change-required false

# Attach policy to user
huaweicloud iam attach-user-policy \
  --user-name k8s-agent-terraform \
  --policy-name k8s-agent-infra-policy

# Create access key for the terraform user (SAVE THESE!)
huaweicloud iam create-access-key \
  --user-name k8s-agent-terraform

# Clean up admin credentials from environment
unset HUAWEI_ADMIN_AK
unset HUAWEI_ADMIN_SK

echo "========================================="
echo "IMPORTANT: Save these credentials!"
echo "========================================="
echo "Access Key ID: <displayed-above>"
echo "Secret Access Key: <displayed-above>"
echo "========================================="
```

**Step 2: Configure Terraform with Restricted Token**

```bash
# Export the restricted token (from Step 1)
export HUAWEICLOUD_ACCESS_KEY_ID="<terraform-user-access-key>"
export HUAWEICLOUD_SECRET_ACCESS_KEY="<terraform-user-secret-key>"
export HUAWEICLOUD_REGION="cn-north-4"
```

### Terraform Configuration

#### `infrastructure/terraform/main.tf`
```hcl
terraform {
  required_version = ">= 1.6"
  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = "~> 1.56"
    }
  }
}

provider "huaweicloud" {
  region = var.region
  # Use environment variables for credentials (from restricted token)
  # HUAWEICLOUD_ACCESS_KEY_ID
  # HUAWEICLOUD_SECRET_ACCESS_KEY
}

# Create VPC first (explicitly, not as module)
module "vpc" {
  source = "./modules/vpc"

  vpc_name   = "${var.cluster_name}-vpc"
  vpc_cidr   = var.vpc_cidr
}

# Create multiple subnets within VPC for different purposes
module "subnet_dmz" {
  source = "./modules/subnet"

  subnet_name = "${var.cluster_name}-subnet-dmz"
  subnet_cidr = var.subnet_dmz_cidr
  vpc_id      = module.vpc.vpc_id
  gateway_ip  = cidrhost(var.subnet_dmz_cidr, 1)
}

module "subnet_apps" {
  source = "./modules/subnet"

  subnet_name = "${var.cluster_name}-subnet-apps"
  subnet_cidr = var.subnet_apps_cidr
  vpc_id      = module.vpc.vpc_id
  gateway_ip  = cidrhost(var.subnet_apps_cidr, 1)
}

module "subnet_devops" {
  source = "./modules/subnet"

  subnet_name = "${var.cluster_name}-subnet-devops"
  subnet_cidr = var.subnet_devops_cidr
  vpc_id      = module.vpc.vpc_id
  gateway_ip  = cidrhost(var.subnet_devops_cidr, 1)
}

module "subnet_database" {
  source = "./modules/subnet"

  subnet_name = "${var.cluster_name}-subnet-database"
  subnet_cidr = var.subnet_database_cidr
  vpc_id      = module.vpc.vpc_id
  gateway_ip  = cidrhost(var.subnet_database_cidr, 1)
}

module "subnet_audit" {
  source = "./modules/subnet"

  subnet_name = "${var.cluster_name}-subnet-audit"
  subnet_cidr = var.subnet_audit_cidr
  vpc_id      = module.vpc.vpc_id
  gateway_ip  = cidrhost(var.subnet_audit_cidr, 1)
}

module "subnet_dev" {
  source = "./modules/subnet"

  subnet_name = "${var.cluster_name}-subnet-dev"
  subnet_cidr = var.subnet_dev_cidr
  vpc_id      = module.vpc.vpc_id
  gateway_ip  = cidrhost(var.subnet_dev_cidr, 1)
}

# Create security groups
module "security_group" {
  source = "./modules/security"

  security_group_name = "${var.cluster_name}-sg"
  security_group_desc = "Security group for k8s cluster"
  vpc_id               = module.vpc.vpc_id
  vpc_cidr             = var.vpc_cidr
  ssh_allowed_ips      = var.ssh_allowed_ips
  enable_linkerd       = var.enable_linkerd
}

# Create NAT Gateway for outbound internet access with static public IP
# This allows resources in private subnets to access external services
# ============================================================================
# Multi-Subnet NAT Gateway and Public Gateway Architecture
# - DMZ & Apps: Use NAT Gateway for controlled outbound access
# - DevOps & Development: Use public gateway with security groups for flexibility
# ============================================================================

# ----------------------------------------------------------------------------
# DMZ Subnet NAT Gateway - Controlled outbound access for public-facing resources
# ----------------------------------------------------------------------------
module "nat_gateway_dmz" {
  source = "./modules/nat"

  nat_name     = "${var.cluster_name}-nat-dmz"
  vpc_id       = module.vpc.vpc_id
  subnet_id    = module.subnet_dmz.subnet_id
  nat_spec     = var.nat_dmz_spec
  enable_nat   = var.enable_nat_dmz
}

module "nat_eip_dmz" {
  source = "./modules/eip"

  eip_name       = "${var.cluster_name}-nat-dmz-eip"
  eip_bandwidth  = var.nat_dmz_eip_bandwidth
  eip_charge_mode = "traffic"
  enable_eip     = var.enable_nat_dmz

  depends_on = [module.nat_gateway_dmz]
}

module "nat_snat_rule_dmz" {
  source = "./modules/nat_snat_rule"

  nat_id       = module.nat_gateway_dmz.nat_id
  vpc_id       = module.vpc.vpc_id
  cidr         = var.subnet_dmz_cidr
  enable_snat  = var.enable_nat_dmz
}

# ----------------------------------------------------------------------------
# Apps Biz Subnet NAT Gateway - High bandwidth for production quality
# ----------------------------------------------------------------------------
module "nat_gateway_apps" {
  source = "./modules/nat"

  nat_name     = "${var.cluster_name}-nat-apps"
  vpc_id       = module.vpc.vpc_id
  subnet_id    = module.subnet_apps.subnet_id
  nat_spec     = var.nat_apps_spec
  enable_nat   = var.enable_nat_apps
}

module "nat_eip_apps" {
  source = "./modules/eip"

  eip_name       = "${var.cluster_name}-nat-apps-eip"
  eip_bandwidth  = var.nat_apps_eip_bandwidth
  eip_charge_mode = "traffic"
  enable_eip     = var.enable_nat_apps

  depends_on = [module.nat_gateway_apps]
}

module "nat_snat_rule_apps" {
  source = "./modules/nat_snat_rule"

  nat_id       = module.nat_gateway_apps.nat_id
  vpc_id       = module.vpc.vpc_id
  cidr         = var.subnet_apps_cidr
  enable_snat  = var.enable_nat_apps
}

# ----------------------------------------------------------------------------
# DevOps and Development Subnets - Public Gateway Access
# These subnets use public IPs directly with security group controls
# No NAT Gateway needed - resources get public IPs for flexibility
# ----------------------------------------------------------------------------
# DevOps subnet resources will have public EIPs assigned directly
# Development subnet resources will have public EIPs assigned directly
# Security groups (defined below) control access to these resources

# Create ECS instances (placed in Apps subnet by default)
module "ecs_cluster" {
  source = "./modules/ecs"

  cluster_name        = var.cluster_name
  instance_count      = var.master_instance_count
  instance_type       = var.master_instance_type
  image_id            = var.image_id
  availability_zone   = var.availability_zone

  network_id          = module.vpc.vpc_id
  subnet_id           = module.subnet_apps.subnet_id
  security_group_ids  = [module.security_group.sg_id]
}

# Create storage (EVS + OBS)
module "storage" {
  source = "./modules/storage"

  cluster_name      = var.cluster_name
  evs_size          = var.evs_size
  availability_zone = var.availability_zone
  obs_bucket_name   = var.obs_bucket_name
}

# Create load balancer (in DMZ subnet)
module "load_balancer" {
  source = "./modules/elb"

  cluster_name    = var.cluster_name
  vpc_id          = module.vpc.vpc_id
  subnet_id       = module.subnet_dmz.subnet_id
  az_list         = var.az_list
  ecs_private_ips = module.ecs_cluster.private_ips
}
```

#### `infrastructure/terraform/variables.tf`
```hcl
variable "region" {
  description = "Huawei Cloud region"
  type        = string
  default     = "cn-north-4"
}

variable "cluster_name" {
  description = "Name of the k3s cluster"
  type        = string
  default     = "k8s-agent-cluster"
}

variable "master_instance_count" {
  description = "Number of master nodes"
  type        = number
  default     = 3
}

variable "master_instance_type" {
  description = "ECS instance type for masters"
  type        = string
  default     = "s6.xlarge.4"
}

variable "image_id" {
  description = "Debian 13 image ID"
  type        = string
}

variable "availability_zone" {
  description = "Primary availability zone"
  type        = string
  default     = "cn-north-4a"
}

variable "az_list" {
  description = "List of availability zones for load balancer"
  type        = list(string)
  default     = ["cn-north-4a"]
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

# Subnet CIDR blocks for different purposes
variable "subnet_dmz_cidr" {
  description = "DMZ subnet CIDR for public-facing resources (load balancers, web servers)"
  type        = string
  default     = "10.0.1.0/24"
}

variable "subnet_apps_cidr" {
  description = "Applications subnet CIDR for application servers and microservices"
  type        = string
  default     = "10.0.2.0/24"
}

variable "subnet_devops_cidr" {
  description = "DevOps subnet CIDR for CI/CD servers and configuration management"
  type        = string
  default     = "10.0.3.0/24"
}

variable "subnet_database_cidr" {
  description = "Database subnet CIDR for database servers and caches"
  type        = string
  default     = "10.0.4.0/24"
}

variable "subnet_audit_cidr" {
  description = "Audit subnet CIDR for audit log collectors and processors"
  type        = string
  default     = "10.0.5.0/24"
}

variable "subnet_dev_cidr" {
  description = "Development subnet CIDR for dev and test servers"
  type        = string
  default     = "10.0.6.0/24"
}

variable "evs_size" {
  description = "EVS disk size in GB"
  type        = number
  default     = 100
}

variable "obs_bucket_name" {
  description = "OBS bucket name (must be globally unique)"
  type        = string
}

variable "ssh_allowed_ips" {
  description = "CIDR blocks allowed for SSH access"
  type        = string
  default     = "0.0.0.0/0"
}

variable "enable_linkerd" {
  description = "Enable Linkerd service mesh security rules"
  type        = bool
  default     = true
}

# ============================================================================
# NAT Gateway Variables
# DMZ & Apps subnets use NAT Gateway for controlled outbound access
# DevOps & Development subnets use public IPs directly with security groups
# ============================================================================

# ----------------------------------------------------------------------------
# DMZ Subnet NAT Gateway - Controlled outbound access
# ----------------------------------------------------------------------------
variable "enable_nat_dmz" {
  description = "Enable NAT Gateway for DMZ subnet"
  type        = bool
  default     = true
}

variable "nat_dmz_spec" {
  description = "DMZ NAT Gateway specification (1: small, 2: medium, 3: large)"
  type        = number
  default     = 1  # Small spec for DMZ
}

variable "nat_dmz_eip_bandwidth" {
  description = "DMZ EIP bandwidth size (Mbps)"
  type        = number
  default     = 20  # 20Mbps for DMZ traffic
}

# ----------------------------------------------------------------------------
# Apps Biz Subnet NAT Gateway - High bandwidth for production quality
# ----------------------------------------------------------------------------
variable "enable_nat_apps" {
  description = "Enable NAT Gateway for Apps subnet"
  type        = bool
  default     = true
}

variable "nat_apps_spec" {
  description = "Apps NAT Gateway specification (1: small, 2: medium, 3: large)"
  type        = number
  default     = 3  # Large spec for production workloads
}

variable "nat_apps_eip_bandwidth" {
  description = "Apps EIP bandwidth size (Mbps) - high bandwidth for production"
  type        = number
  default     = 200  # 200Mbps for production quality
}
```

#### `infrastructure/terraform/outputs.tf`
```hcl
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "subnet_dmz_id" {
  description = "DMZ subnet ID"
  value       = module.subnet_dmz.subnet_id
}

output "subnet_apps_id" {
  description = "Applications subnet ID"
  value       = module.subnet_apps.subnet_id
}

output "subnet_devops_id" {
  description = "DevOps subnet ID"
  value       = module.subnet_devops.subnet_id
}

output "subnet_database_id" {
  description = "Database subnet ID"
  value       = module.subnet_database.subnet_id
}

output "subnet_audit_id" {
  description = "Audit subnet ID"
  value       = module.subnet_audit.subnet_id
}

output "subnet_dev_id" {
  description = "Development subnet ID"
  value       = module.subnet_dev.subnet_id
}

output "security_group_id" {
  description = "Security group ID"
  value       = module.security_group.sg_id
}

# ============================================================================
# NAT Gateway Outputs
# DMZ & Apps subnets use NAT Gateway
# DevOps & Development subnets use public IPs directly
# ============================================================================

# DMZ Subnet NAT Gateway Outputs
output "nat_gateway_dmz_id" {
  description = "DMZ NAT Gateway ID"
  value       = module.nat_gateway_dmz.nat_id
}

output "nat_eip_dmz_address" {
  description = "DMZ NAT Gateway public IP address"
  value       = module.nat_eip_dmz.eip_public_ip
}

# Apps Subnet NAT Gateway Outputs
output "nat_gateway_apps_id" {
  description = "Apps NAT Gateway ID"
  value       = module.nat_gateway_apps.nat_id
}

output "nat_eip_apps_address" {
  description = "Apps NAT Gateway public IP address (high bandwidth for production)"
  value       = module.nat_eip_apps.eip_public_ip
}

output "master_instance_ids" {
  description = "Master node instance IDs"
  value       = module.ecs_cluster.instance_ids
}

output "master_private_ips" {
  description = "Master node private IPs"
  value       = module.ecs_cluster.private_ips
}

output "evs_volume_id" {
  description = "EVS data volume ID"
  value       = module.storage.evs_volume_id
}

output "obs_bucket_name" {
  description = "OBS bucket name"
  value       = module.storage.obs_bucket_name
}

output "elb_id" {
  description = "Load balancer ID"
  value       = module.load_balancer.elb_id
}

output "elb_address" {
  description = "Load balancer public IP"
  value       = module.load_balancer.elb_address
}
```

---

## 1.2 VPC Module

#### `infrastructure/terraform/modules/vpc/main.tf`
```hcl
resource "huaweicloud_vpc" "main" {
  name = var.vpc_name
  cidr = var.vpc_cidr

  tags = {
    Name        = var.vpc_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

output "vpc_id" {
  value       = huaweicloud_vpc.main.id
  description = "VPC ID"
}

output "vpc_cidr" {
  value       = huaweicloud_vpc.main.cidr
  description = "VPC CIDR block"
}
```

#### `infrastructure/terraform/modules/vpc/variables.tf`
```hcl
variable "vpc_name" {
  description = "Name of the VPC"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
}

variable "environment" {
  description = "Environment tag"
  type        = string
  default     = "production"
}
```

---

## 1.3 Subnet Module

#### `infrastructure/terraform/modules/subnet/main.tf`
```hcl
resource "huaweicloud_vpc_subnet" "main" {
  name       = var.subnet_name
  vpc_id     = var.vpc_id
  cidr       = var.subnet_cidr
  gateway_ip = var.gateway_ip

  tags = {
    Name        = var.subnet_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

output "subnet_id" {
  value       = huaweicloud_vpc_subnet.main.id
  description = "Subnet ID"
}

output "subnet_cidr" {
  value       = huaweicloud_vpc_subnet.main.cidr
  description = "Subnet CIDR block"
}
```

#### `infrastructure/terraform/modules/subnet/variables.tf`
```hcl
variable "subnet_name" {
  description = "Name of the subnet"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where subnet will be created"
  type        = string
}

variable "subnet_cidr" {
  description = "CIDR block for subnet"
  type        = string
}

variable "gateway_ip" {
  description = "Gateway IP for the subnet"
  type        = string
}

variable "environment" {
  description = "Environment tag"
  type        = string
  default     = "production"
}
```

---

## 1.4 Security Group Module

#### `infrastructure/terraform/modules/security/main.tf`
```hcl
resource "huaweicloud_networking_secgroup" "main" {
  name        = var.security_group_name
  description = var.security_group_desc
  vpc_id      = var.vpc_id

  tags = {
    Name        = var.security_group_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# SSH access
resource "huaweicloud_networking_secgroup_rule" "ssh" {
  direction       = "ingress"
  ethertype       = "IPv4"
  protocol        = "tcp"
  port_range_min  = 22
  port_range_max  = 22
  remote_ip_prefix = var.ssh_allowed_ips
  security_group_id = huaweicloud_networking_secgroup.main.id
}

# Kubernetes API server
resource "huaweicloud_networking_secgroup_rule" "k8s_api" {
  direction       = "ingress"
  ethertype       = "IPv4"
  protocol        = "tcp"
  port_range_min  = 6443
  port_range_max  = 6443
  remote_ip_prefix = var.vpc_cidr
  security_group_id = huaweicloud_networking_secgroup.main.id
}

# NodePort services
resource "huaweicloud_networking_secgroup_rule" "k8s_nodeport" {
  direction       = "ingress"
  ethertype       = "IPv4"
  protocol        = "tcp"
  port_range_min  = 30000
  port_range_max  = 32767
  remote_ip_prefix = "0.0.0.0/0"
  security_group_id = huaweicloud_networking_secgroup.main.id
}

# Linkerd mesh
resource "huaweicloud_networking_secgroup_rule" "linkerd_mesh" {
  count       = var.enable_linkerd ? 1 : 0
  direction   = "ingress"
  ethertype   = "IPv4"
  protocol    = "tcp"
  port_range_min = 4143
  port_range_max = 4143
  remote_ip_prefix = var.vpc_cidr
  security_group_id = huaweicloud_networking_secgroup.main.id
}

output "sg_id" {
  value       = huaweicloud_networking_secgroup.main.id
  description = "Security group ID"
}
```

#### `infrastructure/terraform/modules/security/variables.tf`
```hcl
variable "security_group_name" {
  description = "Name of the security group"
  type        = string
}

variable "security_group_desc" {
  description = "Description of the security group"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR for internal access"
  type        = string
}

variable "ssh_allowed_ips" {
  description = "CIDR blocks allowed for SSH access"
  type        = string
  default     = "0.0.0.0/0"
}

variable "enable_linkerd" {
  description = "Enable Linkerd service mesh rules"
  type        = bool
  default     = true
}

variable "environment" {
  description = "Environment tag"
  type        = string
  default     = "production"
}
```

---

## 1.5 ECS Module

#### `infrastructure/terraform/modules/ecs/main.tf`
```hcl
resource "huaweicloud_compute_instance" "masters" {
  count = var.instance_count

  name              = "${var.cluster_name}-master-${count.index}"
  image_id          = var.image_id
  flavor_id         = var.instance_type
  availability_zone = var.availability_zone

  network {
    uuid = var.vpc_id
  }

  security_group_ids = var.security_group_ids

  system_disk_type = "SAS"
  system_disk_size = 100
  data_disks {
    type = "SAS"
    size = var.data_disk_size
  }

  user_data = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y curl wget
              EOF
}

output "instance_ids" {
  value       = huaweicloud_compute_instance.masters[*].id
  description = "ECS instance IDs"
}

output "private_ips" {
  value       = huaweicloud_compute_instance.masters[*].access_ip_v4
  description = "Private IP addresses"
}
```

#### `infrastructure/terraform/modules/ecs/variables.tf`
```hcl
variable "cluster_name" {
  description = "Name prefix for instances"
  type        = string
}

variable "instance_count" {
  description = "Number of instances to create"
  type        = number
}

variable "instance_type" {
  description = "ECS instance flavor"
  type        = string
}

variable "image_id" {
  description = "Image ID to use"
  type        = string
}

variable "availability_zone" {
  description = "Availability zone"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID"
  type        = string
}

variable "security_group_ids" {
  description = "Security group IDs"
  type        = list(string)
}

variable "data_disk_size" {
  description = "Data disk size in GB"
  type        = number
  default     = 100
}
```

---

## 1.6 Storage Module

#### `infrastructure/terraform/modules/storage/main.tf`
```hcl
resource "huaweicloud_evs_volume" "main" {
  name              = "${var.cluster_name}-data"
  volume_type       = "SAS"
  size              = var.evs_size
  availability_zone = var.availability_zone
}

resource "huaweicloud_obs_bucket" "main" {
  bucket        = var.obs_bucket_name
  storage_class = "STANDARD"
  acl           = "private"

  lifecycle_rule {
    id      = "log-expiration"
    enabled = true
    expiration = 30
    noncurrent_version_expiration = 90
  }
}

output "evs_volume_id" {
  value       = huaweicloud_evs_volume.main.id
  description = "EVS volume ID"
}

output "obs_bucket_name" {
  value       = huaweicloud_obs_bucket.main.bucket
  description = "OBS bucket name"
}
```

#### `infrastructure/terraform/modules/storage/variables.tf`
```hcl
variable "cluster_name" {
  description = "Name prefix for storage"
  type        = string
}

variable "evs_size" {
  description = "EVS disk size in GB"
  type        = number
}

variable "availability_zone" {
  description = "Availability zone"
  type        = string
}

variable "obs_bucket_name" {
  description = "OBS bucket name (globally unique)"
  type        = string
}
```

---

## 1.7 ELB Module

#### `infrastructure/terraform/modules/elb/main.tf`
```hcl
resource "huaweicloud_lb_loadbalancer" "main" {
  name              = "${var.cluster_name}-elb"
  description       = "Load balancer for k8s cluster"
  vpc_id            = var.vpc_id
  l4_flavor_id      = var.elb_flavor
  availability_zone = var.az_list[0]

  ipv4_bandwidth {
    name   = "c1-e2-e3-bandwidth"
    size   = 100
    share_type = "PER"
  }
}

resource "huaweicloud_lb_listener" "k8s_api" {
  name           = "k8s-api"
  protocol       = "TCP"
  protocol_port  = 6443
  loadbalancer_id = huaweicloud_lb_loadbalancer.main.id

  pool {
    protocol = "TCP"
    lb_method = "ROUND_ROBIN"
  }
}

resource "huaweicloud_lb_member" "masters" {
  count        = length(var.ecs_private_ips)
  pool_id      = huaweicloud_lb_listener.k8s_api.pool[0].id
  address      = var.ecs_private_ips[count.index]
  protocol_port = 6443
}

output "elb_id" {
  value       = huaweicloud_lb_loadbalancer.main.id
  description = "Load balancer ID"
}

output "elb_address" {
  value       = huaweicloud_lb_loadbalancer.main.public_ip
  description = "Load balancer public IP"
}
```

#### `infrastructure/terraform/modules/elb/variables.tf`
```hcl
variable "cluster_name" {
  description = "Name prefix for load balancer"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID"
  type        = string
}

variable "elb_flavor" {
  description = "ELB flavor ID"
  type        = string
  default     = "L4_flavor.elb.share.ip"
}

variable "az_list" {
  description = "List of availability zones"
  type        = list(string)
}

variable "ecs_private_ips" {
  description = "List of ECS private IP addresses"
  type        = list(string)
}
```

---

## 1.8 NAT Gateway Module

The NAT Gateway provides outbound internet access for resources in private subnets with a static public IP address, making it easy to whitelist your infrastructure in external services.

#### `infrastructure/terraform/modules/nat/main.tf`
```hcl
resource "huaweicloud_nat_gateway" "main" {
  count = var.enable_nat ? 1 : 0

  name        = var.nat_name
  description = "NAT Gateway for outbound internet access with static public IP"
  spec        = var.nat_spec
  vpc_id      = var.vpc_id
  subnet_id   = var.subnet_id

  tags = {
    Name        = var.nat_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

output "nat_id" {
  value       = var.enable_nat ? huaweicloud_nat_gateway.main[0].id : null
  description = "NAT Gateway ID"
}
```

#### `infrastructure/terraform/modules/nat/variables.tf`
```hcl
variable "nat_name" {
  description = "Name of the NAT Gateway"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where NAT Gateway will be created"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID (DMZ subnet) where NAT Gateway will be placed"
  type        = string
}

variable "nat_spec" {
  description = "NAT Gateway specification (1: small, 2: medium, 3: large)"
  type        = number
  default     = 2
}

variable "enable_nat" {
  description = "Enable NAT Gateway creation"
  type        = bool
  default     = true
}

variable "environment" {
  description = "Environment tag"
  type        = string
  default     = "production"
}
```

---

## 1.9 EIP Module for NAT Gateway

#### `infrastructure/terraform/modules/eip/main.tf`
```hcl
resource "huaweicloud_vpc_eip" "nat_eip" {
  count = var.enable_eip ? 1 : 0

  publicip {
    type = "5_bgp"
  }

  bandwidth {
    name        = var.eip_name
    size        = var.eip_bandwidth
    share_type  = "PER"
    charge_mode = "traffic"
  }

  tags = {
    Name        = var.eip_name
    Purpose     = "NAT Gateway"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

output "eip_id" {
  value       = var.enable_eip ? huaweicloud_vpc_eip.nat_eip[0].id : null
  description = "EIP ID"
}

output "eip_public_ip" {
  value       = var.enable_eip ? huaweicloud_vpc_eip.nat_eip[0].publicip : null
  description = "EIP public IP address (for whitelisting)"
}
```

#### `infrastructure/terraform/modules/eip/variables.tf`
```hcl
variable "eip_name" {
  description = "Name of the EIP"
  type        = string
}

variable "eip_bandwidth" {
  description = "EIP bandwidth size in Mbps"
  type        = number
  default     = 100
}

variable "enable_eip" {
  description = "Enable EIP creation"
  type        = bool
  default     = true
}

variable "environment" {
  description = "Environment tag"
  type        = string
  default     = "production"
}
```

---

## 1.10 SNAT Rule Module

The SNAT rule allows all resources in the VPC to use the NAT Gateway for outbound internet access.

#### `infrastructure/terraform/modules/nat_snat_rule/main.tf`
```hcl
resource "huaweicloud_nat_snat_rule" "main" {
  count = var.enable_snat ? 1 : 0

  nat_gateway_id = var.nat_id
  network_id     = var.vpc_id
  cidr           = var.cidr

  # Source CIDR for SNAT rule (entire VPC)
  source_cidr = var.cidr
}

output "snat_rule_id" {
  value       = var.enable_snat ? huaweicloud_nat_snat_rule.main[0].id : null
  description = "SNAT rule ID"
}
```

#### `infrastructure/terraform/modules/nat_snat_rule/variables.tf`
```hcl
variable "nat_id" {
  description = "NAT Gateway ID"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID for SNAT rule"
  type        = string
}

variable "cidr" {
  description = "CIDR block for SNAT rule (entire VPC CIDR)"
  type        = string
}

variable "enable_snat" {
  description = "Enable SNAT rule creation"
  type        = bool
  default     = true
}
```

---

## 1.11 Public IPs and Security Groups

DevOps and Development subnets use public EIPs assigned directly to resources, with security groups controlling access. This provides maximum flexibility for these environments.

### Public IP Assignment

Resources in DevOps and Development subnets are assigned public EIPs directly:

```hcl
# Example: DevOps ECS with public IP
resource "huaweicloud_compute_instance" "devops_server" {
  # ... instance configuration ...

  # Assign public EIP
  public_ip = var.assign_public_ip ? true : false
}

# Separate EIP resource for more control
resource "huaweicloud_vpc_eip" "devops_eip" {
  publicip {
    type = "5_bgp"
  }

  bandwidth {
    name        = "${var.cluster_name}-devops-eip"
    size        = var.devops_eip_bandwidth
    share_type  = "PER"
    charge_mode = "traffic"
  }
}

# Associate EIP with the instance
resource "huaweicloud_vpc_eip_associate" "devops_eip_assoc" {
  public_ip = huaweicloud_vpc_eip.devops_eip.publicip
  instance_id = huaweicloud_compute_instance.devops_server.id
}
```

### Security Group Rules

Security groups control access to resources with public IPs:

```hcl
# DevOps Security Group - Allows specific services
resource "huaweicloud_networking_secgroup_rule" "devops_mongodb" {
  direction       = "ingress"
  ethertype       = "IPv4"
  protocol        = "tcp"
  port_range_min  = 27017
  port_range_max  = 27017
  remote_ip_prefix = var.allowed_mongodb_ips  # Restrict access
  security_group_id = huaweicloud_networking_secgroup.devops.id
}

resource "huaweicloud_networking_secgroup_rule" "devops_kafka" {
  direction       = "ingress"
  ethertype       = "IPv4"
  protocol        = "tcp"
  port_range_min  = 9092
  port_range_max  = 9094
  remote_ip_prefix = var.allowed_kafka_ips  # Restrict access
  security_group_id = huaweicloud_networking_secgroup.devops.id
}

resource "huaweicloud_networking_secgroup_rule" "devops_gitlab_http" {
  direction       = "ingress"
  ethertype       = "IPv4"
  protocol        = "tcp"
  port_range_min  = 80
  port_range_max  = 80
  remote_ip_prefix = "0.0.0.0/0"  # GitLab web UI accessible from anywhere
  security_group_id = huaweicloud_networking_secgroup.devops.id
}

resource "huaweicloud_networking_secgroup_rule" "devops_gitlab_https" {
  direction       = "ingress"
  ethertype       = "IPv4"
  protocol        = "tcp"
  port_range_min  = 443
  port_range_max  = 443
  remote_ip_prefix = "0.0.0.0/0"  # GitLab web UI accessible from anywhere
  security_group_id = huaweicloud_networking_secgroup.devops.id
}
```

### Common DevOps Service Ports

| Service | Port | Protocol | Access Control |
|---------|------|----------|----------------|
| MongoDB | 27017 | TCP | Restrict to known IPs |
| Kafka | 9092-9094 | TCP | Restrict to known IPs |
| GitLab SSH | 22 | TCP | Restrict to known IPs or key-based |
| GitLab HTTP | 80 | TCP | Open (with authentication) |
| GitLab HTTPS | 443 | TCP | Open (with authentication) |
| Docker Registry | 5000 | TCP | Restrict to known IPs |
| Jenkins | 8080 | TCP | Open (with authentication) |
| Grafana | 3000 | TCP | Open (with authentication) |

### Development Subnet Security

Development subnet resources have more flexible security rules:

```hcl
# Development Security Group - More permissive for flexibility
resource "huaweicloud_networking_secgroup_rule" "dev_allow_all" {
  direction       = "ingress"
  ethertype       = "IPv4"
  protocol        = "tcp"
  port_range_min  = 1
  port_range_max  = 65535
  remote_ip_prefix = var.dev_allowed_ips  # Developer office IPs or VPN
  security_group_id = huaweicloud_networking_secgroup.dev.id
}
```

---

## 1.12 Deployment Scripts

#### `scripts/infrastructure/terraform-init.sh`
```bash
#!/bin/bash
set -e

# Check for required environment variables (from restricted token)
if [[ -z "$HUAWEICLOUD_ACCESS_KEY_ID" ]] || [[ -z "$HUAWEICLOUD_SECRET_ACCESS_KEY" ]]; then
  echo "Error: HUAWEICLOUD_ACCESS_KEY_ID and HUAWEICLOUD_SECRET_ACCESS_KEY must be set"
  echo "These should be from the restricted k8s-agent-terraform user, not admin credentials"
  exit 1
fi

PLAN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PLAN_DIR/../terraform"

echo "Initializing Terraform..."
terraform init

echo "Validating configuration..."
terraform validate

echo "Planning infrastructure..."
terraform plan -out=tfplan

echo "Apply infrastructure? (yes/no)"
read -r response
if [[ "$response" == "yes" ]]; then
  terraform apply tfplan
  terraform output -json > outputs.json
  echo "Infrastructure deployed successfully!"
  echo "Outputs saved to outputs.json"
else
  echo "Deployment cancelled."
fi
```

#### `scripts/infrastructure/terraform-destroy.sh`
```bash
#!/bin/bash
set -e

PLAN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PLAN_DIR/../terraform"

echo "This will destroy all infrastructure. Are you sure? (yes/no)"
read -r response
if [[ "$response" == "yes" ]]; then
  terraform destroy
  echo "Infrastructure destroyed."
else
  echo "Operation cancelled."
fi
```

---

## 1.9 Environment Configuration

#### `infrastructure/terraform/environments/dev.tfvars`
```hcl
cluster_name           = "k8s-agent-dev"
region                = "cn-north-4"
availability_zone     = "cn-north-4a"
az_list               = ["cn-north-4a"]
master_instance_count = 1
master_instance_type  = "s6.large.4"
image_id              = "<debian-13-image-id>"  # Update with actual image ID
evs_size              = 50
vpc_cidr              = "10.10.0.0/16"

# Multi-subnet configuration for development
subnet_dmz_cidr       = "10.10.1.0/24"  # Public-facing resources
subnet_apps_cidr      = "10.10.2.0/24"  # Application servers
subnet_devops_cidr    = "10.10.3.0/24"  # CI/CD and config management
subnet_database_cidr  = "10.10.4.0/24"  # Databases and caches
subnet_audit_cidr     = "10.10.5.0/24"  # Audit resources
subnet_dev_cidr       = "10.10.6.0/24"  # Dev/test servers

obs_bucket_name       = "k8s-agent-dev-<unique-id>"  # Must be globally unique
ssh_allowed_ips       = "0.0.0.0/0"  # Restrict in production
enable_linkerd        = true

# ============================================================================
# NAT Gateway Configuration for Development
# DMZ & Apps use NAT Gateway | DevOps & Development use public IPs directly
# ============================================================================

# DMZ Subnet NAT - Controlled outbound access
enable_nat_dmz        = true
nat_dmz_spec          = 1  # Small spec
nat_dmz_eip_bandwidth = 10  # 10Mbps

# Apps Subnet NAT - Standard bandwidth for development
enable_nat_apps       = true
nat_apps_spec         = 2  # Medium spec
nat_apps_eip_bandwidth = 50  # 50Mbps

# DevOps and Development subnets use public IPs directly
# Security groups control access to these resources
```

#### `infrastructure/terraform/environments/production.tfvars`
```hcl
cluster_name           = "k8s-agent-prod"
region                = "cn-north-4"
availability_zone     = "cn-north-4a"
az_list               = ["cn-north-4a", "cn-north-4b"]
master_instance_count = 3
master_instance_type  = "s6.xlarge.4"
image_id              = "<debian-13-image-id>"  # Update with actual image ID
evs_size              = 200
vpc_cidr              = "10.20.0.0/16"

# Multi-subnet configuration for production
subnet_dmz_cidr       = "10.20.1.0/24"  # Public-facing resources (load balancers, web servers)
subnet_apps_cidr      = "10.20.2.0/24"  # Application servers and microservices
subnet_devops_cidr    = "10.20.3.0/24"  # CI/CD servers and configuration management
subnet_database_cidr  = "10.20.4.0/24"  # Database servers and caches
subnet_audit_cidr     = "10.20.5.0/24"  # Audit log collectors and processors
subnet_dev_cidr       = "10.20.6.0/24"  # Development and test servers

obs_bucket_name       = "k8s-agent-prod-<unique-id>"  # Must be globally unique
ssh_allowed_ips       = "<your-office-ip>/32"  # Restrict to specific IPs
enable_linkerd        = true

# ============================================================================
# NAT Gateway Configuration for Production
# DMZ & Apps use NAT Gateway | DevOps & Development use public IPs directly
# ============================================================================

# DMZ Subnet NAT - Controlled outbound access
enable_nat_dmz        = true
nat_dmz_spec          = 1  # Small spec - DMZ has limited traffic
nat_dmz_eip_bandwidth = 20  # 20Mbps

# Apps Subnet NAT - High bandwidth for production quality
enable_nat_apps       = true
nat_apps_spec         = 3  # Large spec for production workloads
nat_apps_eip_bandwidth = 200  # 200Mbps - high bandwidth for production

# DevOps and Development subnets use public IPs directly
# Security groups control access to these resources
```

---

## Verification Steps

After completing this phase:

1. [ ] Verify ECS instances are running
   ```bash
   ssh ubuntu@<public-ip>
   ```

2. [ ] Verify VPC and subnet configuration
   ```bash
   huaweicloud vpc show <vpc-id>
   ```

3. [ ] Verify storage provisioning
   ```bash
   huaweicloud evs volume show <volume-id>
   huaweicloud obs bucket list
   ```

4. [ ] Verify NAT Gateways (DMZ and Apps subnets only)
   ```bash
   # DMZ Subnet NAT Gateway
   huaweicloud nat gateway show <nat-gateway-dmz-id>
   huaweicloud vpc eip show <nat-eip-dmz-id>
   echo "DMZ NAT Gateway public IP: <nat-eip-dmz-address>"

   # Apps Subnet NAT Gateway
   huaweicloud nat gateway show <nat-gateway-apps-id>
   huaweicloud vpc eip show <nat-eip-apps-id>
   echo "Apps NAT Gateway public IP: <nat-eip-apps-address>"

   # Use these IPs for whitelisting in external services
   echo "Whitelist these IPs in external services:"
   echo "  - Apps (high bandwidth): <nat-eip-apps-address>"
   echo "  - DMZ: <nat-eip-dmz-address>"
   ```

5. [ ] Test outbound internet access through NAT Gateways
   ```bash
   # From Apps subnet ECS instance (uses NAT Gateway)
   curl https://ifconfig.me
   # Should return the Apps NAT Gateway public IP

   # From DMZ subnet ECS instance (uses NAT Gateway)
   curl https://ifconfig.me
   # Should return the DMZ NAT Gateway public IP
   ```

6. [ ] Verify DevOps and Development public IPs and security groups
   ```bash
   # Verify DevOps resources have public IPs
   huaweicloud ecs server list --name devops-*
   # Check the public_ip field

   # Verify Development resources have public IPs
   huaweicloud ecs server list --name dev-*
   # Check the public_ip field

   # Verify security group rules
   huaweicloud security group rule list <devops-sg-id>
   huaweicloud security group rule list <dev-sg-id>

   # Test access to DevOps services (using their public IPs)
   telnet <devops-gitlab-public-ip> 443
   telnet <devops-mongodb-public-ip> 27017
   ```

7. [ ] Verify load balancer
   ```bash
   huaweicloud elb show <elb-id>
   ```

8. [ ] Test connectivity
   ```bash
   ping <master-ip>
   curl -k https://<elb-address>:6443
   ```

---

## Next Phase

Proceed to **Phase 2: K8s Platform Setup** ([02-k8s-platform-plan.md](./02-k8s-platform-plan.md))
