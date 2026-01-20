## Golden Flows

### Flow 1: Internet to Application (Public Ingress)

```
Internet
    ↓ (HTTPS :443)
Public Network Gateway
    ↓ (DMZ subnet - 10.21.0.0/22)
Public Load Balancer (EIP)
    ↓ (HTTP :8080, target: app servers)
App Servers (Business-Only - 10.21.20.0/22)
    ↓ (PostgreSQL :5432)
PostgreSQL (Database-Private - 10.21.24.0/22)
```

**Key points:**
- Public LB SG allows: 0.0.0.0/0:443
- App SG allows: Public LB SG:8080
- DB SG allows: App SG:5432
- No NAT involved (ingress traffic path)

### Flow 2: Private Egress (Package Updates)

```
App Server (Business-Only - 10.21.20.0/22)
    ↓ (default route 0.0.0.0/0)
NAT Gateway (Internal-Shared - 10.21.8.0/22)
    ↓ (via EIP, SNAT rule for 10.21.20.0/22)
Internet
    ↓ (repository.example.com)
Package Repository (apt/yum/pip)
```

**Key points:**
- App server has no public IP
- Uses single NAT Gateway for outbound internet access
- SNAT rule maps source CIDR to NAT EIP
- Return traffic follows reverse path via NAT

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
