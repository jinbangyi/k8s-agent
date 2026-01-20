# Network Architecture

## Overview

This document provides the visual architecture diagrams for the k8s-agent network infrastructure on Huawei Cloud (ap-southeast-3).

---

## Single VPC Architecture

```mermaid
graph TD
    internet[Internet]

    subgraph vpc["VPC - 10.x.0.0/16 (ap-southeast-3)"]
        pgw[Public Network Gateway]

        %% Public Route Table (DMZ and External-Access subnets)
        subgraph public-rt["Public Route Table"]
            subgraph dmz-subnet["DMZ Subnet - 10.x.0.0/22"]
                web[Web Servers]
                public-lb[Public Load Balancers EIP]
            end

            subgraph external-subnet["External-Access Subnet - 10.x.4.0/24"]
                partner[Partner-Facing Services]
                kafka-proxy[Kafka Proxy]
                mongo-proxy[MongoDB Proxy]
                pg-proxy[PostgreSQL Proxy]
                es-proxy[Elasticsearch Proxy]
            end
        end

        %% Private-Egress Route Table (all subnets with NAT egress)
        subgraph private-egress-rt["Private-Egress Route Table"]
            subgraph internal-shared-subnet["Internal-Shared Subnet - 10.x.8.0/22"]
                internal-lb[Internal Load Balancer]
                loki[Loki Logging]
                prometheus[Prometheus Monitoring]
                gitlab[GitLab]
                nat[NAT Gateway EIP]
            end

            subgraph devops-subnet["DevOps-Only Subnet - 10.x.12.0/22"]
                ci[CI/CD Servers]
                build[Build Agents]
            end

            subgraph dev-subnet["Development-Only Subnet - 10.x.16.0/22"]
                test[Test Environments]
                devservers[Dev Servers]
            end

            subgraph business-subnet["Business-Only Subnet - 10.x.20.0/22"]
                erp[ERP Systems]
                business-apps[Business Applications]
            end

            subgraph database-subnet["Database-Private Subnet - 10.x.24.0/22"]
                self-hosted-pg[Self-Hosted PostgreSQL]
                cloud-pg[Cloud PostgreSQL/RDS]
                cache[Caches Redis]
            end

            subgraph security-subnet["Security-Private Subnet - 10.x.28.0/24"]
                vault[Vault]
                ids[Intrusion Detection]
            end
        end
    end

    %% Internet ingress to public-facing subnets
    internet --> pgw
    pgw --> dmz-subnet
    pgw --> external-subnet

    %% All private subnets egress via NAT Gateway
    internal-shared-subnet -.->|SNAT| nat
    devops-subnet -.->|SNAT| nat
    dev-subnet -.->|SNAT| nat
    business-subnet -.->|SNAT| nat
    database-subnet -.->|limited egress| nat
    security-subnet -.->|limited egress| nat
    nat --> internet

    %% Load Balancer traffic flows
    public-lb --> web
    public-lb --> kafka-proxy
    public-lb --> mongo-proxy
    public-lb --> pg-proxy
    public-lb --> es-proxy

    internal-lb --> loki
    internal-lb --> prometheus
    internal-lb --> gitlab

    %% Style definitions
    classDef vpc-style fill:#f0f8ff,stroke:#1e90ff,stroke-width:2px
    classDef rt-style fill:#fff5ee,stroke:#ff8c00,stroke-width:1px
    classDef public-style fill:#ffcccc,stroke:#cc0000,stroke-width:2px
    classDef internal-shared-style fill:#ccffcc,stroke:#00aa00,stroke-width:2px
    classDef team-style fill:#ffffcc,stroke:#ccaa00,stroke-width:2px
    classDef private-style fill:#ccccff,stroke:#0000cc,stroke-width:2px
    classDef resource-style fill:#e8f4f8,stroke:#3498db,stroke-width:1px
    classDef lb-style fill:#a8d8ea,stroke:#0094c6,stroke-width:2px
    classDef gateway-style fill:#ffffff,stroke:#333333,stroke-width:2px,stroke-dasharray:5,5

    class vpc vpc-style
    class public-rt,private-egress-rt rt-style
    class dmz-subnet,external-subnet public-style
    class internal-shared-subnet internal-shared-style
    class devops-subnet,dev-subnet,business-subnet team-style
    class database-subnet,security-subnet private-style
    class web,kafka-proxy,mongo-proxy,pg-proxy,es-proxy,partner,loki,prometheus,gitlab,ci,build,test,devservers,erp,business-apps,self-hosted-pg,cloud-pg,cache,vault,ids resource-style
    class public-lb,internal-lb lb-style
    class pgw,nat gateway-style
```

---

## Multi-VPC Peering Architecture

```mermaid
graph TD
    internet[Internet]

    subgraph prod["Production VPC - 10.20.0.0/16"]
        prod-pgw[Public Network Gateway]
        prod-nat[NAT Gateway]

        subgraph prod-dmz["DMZ Subnet"]
            prod-web[Web Servers]
            prod-lb[Public Load Balancers]
        end

        subgraph prod-shared["Internal-Shared Subnet"]
            prod-loki[Loki Logging]
            prod-prometheus[Prometheus Monitoring]
        end

        subgraph prod-devops["DevOps-Only Subnet"]
            prod-ci[CI/CD Servers]
        end

        subgraph prod-db["Database-Private Subnet"]
            prod-pg[PostgreSQL]
            prod-redis[Redis Cache]
        end
    end

    subgraph dev["Development VPC - 10.21.0.0/16"]
        dev-pgw[Public Network Gateway]
        dev-nat[NAT Gateway]

        subgraph dev-dmz["DMZ Subnet"]
            dev-web[Web Servers]
            dev-lb[Public Load Balancers]
        end

        subgraph dev-shared["Internal-Shared Subnet"]
            dev-gitlab[GitLab]
        end

        subgraph dev-business["Business-Only Subnet"]
            dev-app1[App Server 1]
            dev-app2[App Server 2]
        end

        subgraph dev-debug["Development-Only Subnet"]
            dev-debug1[Debug Instance 1]
            dev-debug2[Debug Instance 2]
        end
    end

    peering[VPC Peering Connection]

    %% prod connectivity
    internet --> prod-pgw
    prod-pgw --> prod-dmz
    prod-shared -.->|SNAT| prod-nat
    prod-devops -.->|SNAT| prod-nat
    prod-db -.->|limited egress| prod-nat
    prod-nat --> internet

    %% dev connectivity
    internet --> dev-pgw
    dev-pgw --> dev-dmz
    dev-shared -.->|SNAT| dev-nat
    dev-business -.->|SNAT| dev-nat
    dev-debug -.->|SNAT| dev-nat
    dev-nat --> internet

    %% VPC Peering routes
    prod-db -.->|10.21.0.0/16 via peering| peering
    dev-business -.->|10.20.0.0/16 via peering| peering
    dev-debug -.->|10.20.0.0/16 via peering| peering

    %% Cross-VPC application traffic
    dev-app1 -.->|accesses| prod-pg
    dev-app2 -.->|accesses| prod-pg
    dev-app1 -.->|accesses| prod-redis
    dev-debug1 -.->|accesses| prod-pg
    dev-debug2 -.->|accesses| prod-pg

    %% Style definitions
    classDef vpc-style fill:#f0f8ff,stroke:#1e90ff,stroke-width:2px
    classDef subnet-style fill:#fff0f5,stroke:#ff69b4,stroke-width:1px
    classDef resource-style fill:#f0fff0,stroke:#32cd32,stroke-width:1px
    classDef gateway-style fill:#ffffff,stroke:#808080,stroke-width:2px,stroke-dasharray:5,5
    classDef peering-style fill:#ffd700,stroke:#ff8c00,stroke-width:3px,stroke-dasharray:10,5

    class prod,dev vpc-style
    class prod-dmz,prod-shared,prod-devops,prod-db,dev-dmz,dev-shared,dev-business,dev-debug subnet-style
    class prod-web,prod-lb,prod-loki,prod-prometheus,prod-ci,prod-pg,prod-redis,dev-web,dev-lb,dev-gitlab,dev-app1,dev-app2,dev-debug1,dev-debug2 resource-style
    class prod-pgw,prod-nat,dev-pgw,dev-nat gateway-style
    class peering peering-style
```

---

## Quick Reference

| Environment | VPC CIDR | Region |
|-------------|----------|--------|
| Production | 10.20.0.0/16 | ap-southeast-3 |
| Development | 10.21.0.0/16 | ap-southeast-3 |

---

## Related Documentation

- [Specifications](./network-specifications.md) - Detailed subnet, route table, and load balancer specifications
- [Guidelines](./network-guidelines.md) - Design rules, principles, and best practices
- [Flows](./network-flows.md) - Traffic flow examples and golden flows
- [User Rules](../user.md) - High-level network rules and guidelines
