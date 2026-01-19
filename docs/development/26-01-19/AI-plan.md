# Network Architecture Documentation Improvement Plan

## Current Status
The `user.md` file in the 26-01-19 directory provides updated network architecture guidelines with the following key requirements:

**Latest Requirements**:
- Region: `ap-southeast-3`
- NAT Gateway: medium instance type
- Subnet size: `/22` (not `/24`)
- Security groups: Each ECS, subnet, and VPC has its own security group
- IP addressing: Not required - Kubernetes internal DNS for discovery
- Updated Mermaid diagram with improved structure

## Improvement Strategy

### Research and Analysis (Completed)
- Analyzed latest `user.md` file in 26-01-19 directory
- Reviewed updated Mermaid diagram
- Identified requirements for documentation enhancement

### Documentation Enhancement (Completed)
1. **Update VPC and subnet architecture** with ap-southeast-3 region and /22 subnet size
2. **Update NAT gateway configuration** to use medium instance type
3. **Enhance security group rules section**
4. **Remove IP address assignment details** (using Kubernetes DNS)
5. **Verify consistency with updated Mermaid diagram**
6. **Improve document structure and organization**

### Expected Outcome
A complete, consistent network architecture document that:
- Aligns with the latest requirements from @docs/development/26-01-19/user.md
- Provides detailed information about VPC, subnets, security, and connectivity
- Uses clear structure and the updated Mermaid diagram
- Serves as a reference for network design and implementation

## Detailed Plan

### Phase 1: Content Update
1. **VPC Architecture Section**: Add VPC name, CIDR block, region, and design principles
2. **Subnet Design Section**: Add comprehensive subnet details including CIDR blocks (/22), purposes, resources, and security
3. **NAT Gateway Configuration**: Update to use medium instance type, add details about EIP and route table associations
4. **Security Group Rules**: Enhance with VPC-level, subnet-level, and instance-level rules
5. **Internet Access Strategy**: Explain hybrid access approach with NAT gateway and public IP benefits
6. **Load Balancer Configuration**: Detail both public (DMZ) and internal (internal-shared) load balancers
7. **Route Table Configuration**: Detail route table associations and rules for each subnet category
8. **Traffic Flow**: Describe inbound, outbound, and internal traffic patterns
9. **Network Security Guidelines**: Add best practices for subnet isolation, access control, whitelisting, and monitoring

### Phase 2: Structure and Organization
1. **Improve document structure**: Organize content into clear sections with proper hierarchy
2. **Enhance readability**: Use tables, lists, and diagrams to improve comprehension
3. **Add cross-references**: Link to related documentation (02-network-architecture.md, 01-infrastructure-overview.md)

### Phase 3: Review and Validation (Completed)
1. Verify all information is consistent with the latest user.md requirements
2. Check region, CIDR blocks, and NAT gateway configuration
3. Ensure the Mermaid diagram matches text descriptions
4. Review for clarity and completeness

## Files to Update
- `@docs/development/26-01-19/user.md` - enhance content and structure
- `@docs/development/26-01-19/02-network-architecture.md` - ensure consistency with user.md
- `@docs/development/26-01-19/AI-plan.md` - update plan with new requirements

## Resources to Reference
- `@docs/development/26-01-19/user.md` - for latest requirements
- Project CLAUDE.md - for documentation guidelines

## Specific Recommendations

### 1. VPC Configuration
```markdown
### VPC Configuration

- **Name**: `k8s-agent-cluster-vpc`
- **CIDR Block**: `10.x.0.0/16` (supports 16 subnets with /22 masks)
- **Region**: `ap-southeast-3`
- **Availability Zones**: `ap-southeast-3a`, `ap-southeast-3b` (for high availability)
- **Description**: Main VPC for the k8s-agent project with segmented subnets
```

### 2. Subnet CIDR Allocation (/22 Size)
```markdown
### Subnet CIDR Allocation

| Subnet Name | CIDR Block | Purpose |
|-------------|------------|---------|
| DMZ | 10.x.0.0/22 | Public-facing resources accessible from internet |
| external-access | 10.x.4.0/22 | Resources accessible from external partners or vendors |
| internal-shared | 10.x.8.0/22 | Resources shared across all internal teams |
| devops-only | 10.x.12.0/22 | DevOps team exclusive resources |
| development-only | 10.x.16.0/22 | Development team exclusive resources |
| business-only | 10.x.20.0/22 | Business/Operations team exclusive resources |
| database-private | 10.x.24.0/22 | Database resources with restricted access |
| security-private | 10.x.28.0/22 | Security-critical resources with minimal access |
```

### 3. NAT Gateway Configuration (Medium Instance)
```markdown
### NAT Gateway Configuration

- **Name**: `k8s-agent-nat-gateway`
- **Spec**: Medium
- **Bandwidth**: 200Mbps
- **EIP**: Elastic IP address for NAT gateway
- **Subnet Association**: internal-shared, team resources subnets
- **Purpose**: Provides outbound internet access for private subnets with a static public IP for whitelisting
```

### 4. Security Group Rules
```markdown
### Security Group Rules

#### VPC-Level Security Group
| Rule | Port | Source | Description |
|------|------|--------|-------------|
| SSH | 22 | Configurable CIDR (e.g., office IP range) | Administrative access |
| ICMP | All | VPC CIDR (10.30.0.0/16) | Network connectivity testing |

#### Subnet-Level Security Groups (Example)
| Subnet | Rule | Port | Source | Description |
|--------|------|------|--------|-------------|
| DMZ | HTTP/HTTPS | 80, 443 | 0.0.0.0/0 | Public web traffic |
| DMZ | API Gateway | 8000, 8443 | 0.0.0.0/0 | Kong API access |
| internal-shared | K8s API | 6443 | VPC CIDR | Kubernetes API access |
| internal-shared | Loki | 3100 | VPC CIDR | Logging access |
| internal-shared | Prometheus | 9090 | VPC CIDR | Monitoring access |
| database-private | PostgreSQL | 5432 | VPC CIDR | Database access |
| security-private | Vault | 8200 | Restricted CIDR | Secret management |

#### Instance-Level Security Groups
Each ECS instance will have its own security group with additional service-specific rules.
```

### 5. Load Balancer Configuration
```markdown
### Load Balancer Configuration

#### Public Load Balancers (DMZ Subnet)
| Load Balancer | Type | VIP | EIP | Ports | Backend |
|---------------|------|-----|-----|-------|---------|
| Kong API Gateway | TCP | 10.30.0.20 | 1.2.3.4 | 8000, 8443 | Kong instances |
| Kafka Proxy | TCP | 10.30.0.21 | 1.2.3.5 | 9092 | Kafka cluster |
| MongoDB Proxy | TCP | 10.30.0.22 | 1.2.3.6 | 27017 | MongoDB cluster |
| PostgreSQL Proxy | TCP | 10.30.0.23 | 1.2.3.7 | 5432 | PostgreSQL cluster |
| Elasticsearch Proxy | TCP | 10.30.0.24 | 1.2.3.8 | 9200 | Elasticsearch cluster |

#### Internal Load Balancers (internal-shared Subnet)
| Load Balancer | Type | VIP | EIP | Ports | Backend |
|---------------|------|-----|-----|-------|---------|
| K8s API | TCP | 10.30.8.20 | - | 6443 | Kubernetes masters |
| Internal Services | HTTP/HTTPS | 10.30.8.21 | - | 80, 443 | Internal applications |
```
