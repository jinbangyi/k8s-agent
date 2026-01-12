# k8s-agent Complete Initial Setup Plan

## Overview
Implement the complete initial setup for the k8s-agent repository - a comprehensive Kubernetes lifecycle management platform with full observability stack, targeting Huawei Cloud ECS with k3s lightweight Kubernetes.

## Infrastructure Environment

**Base Platform:**
- **Host:** Huawei Cloud ECS instance
- **OS:** Debian 13
- **K8s:** k3s v1.32 (lightweight Kubernetes)
- **K8s Management:** Rancher
- **GitOps:** ArgoCD

**Storage:**
- Huawei Cloud EVS (Elastic Volume Service)
- Huawei Cloud SCS (Scalable Cloud Service)
- Huawei Cloud OBS (Object Storage Service)

**Networking & Security:**
- Huawei Cloud ELB (Elastic Load Balance)
- Kong API Gateway
- cert-manager for SSL/TLS certificate management
- Linkerd service mesh for microservices
- Vault for secrets management (self-hosted)
- External Secrets Operator for multi-source secrets sync
- Bitwarden/server for personal secrets

**Development & Operations:**
- Coder for remote IDE
- GitLab for git repository management
- Terraform for Infrastructure as Code

**Manifests Management:**
- Helm
- helmfile
- kustomize

**Observability Stack:**
- **Monitoring:** Prometheus + Grafana
- **Logging:** Loki
- **Alerting:** Alertmanager
- **APM:** Signoz
- **Analytics:** Posthog
- **Error Tracking:** Sentry
- **Cost Management:** OpenCost

**Internal Developer Tools:**
- **Developer Portal:** Backstage
- **Service Portal:** Homer
- **Workflow Automation:** n8n
- **Workflow Orchestration:** Prefect
- **Data Orchestration:** Dagster
- **LLM Observability:** Langfuse
- **IDE:** Coder
- **Personal Secrets:** Bitwarden/server
- **Git Repository:** GitLab

**Infrastructure Management:**
- **Bastion Host:** Jumpserver
- **Backup/Restore:** Velero
- **External Resource Management:** Crossplane (with Huawei Cloud provider if available)

**Governance & Policy:**
- **Policy Engine:** Kyverno
- **Image Scanning:** Trivy (integrated in Harbor)

**Service Infrastructure:**
- **Config Management:** Kusion
- **Configuration Center:** Apollo
- **Local LLM:** LiteLLM
- **Go Module Proxy:** Athens
- **Python Package Index:** pypiserver
- **NPM Package Proxy:** Verdaccio
- **MCP Lifecycle Management:** kmcp
- **AI Agents for K8s:** kagent
- **MCP Customization:** mcp-context-forge

**Identity & Access Management:**
- **IAM Provider:** Keycloak / Authentik / Zitadel (choose one)

**Custom Middlewares & Databases:**
- **Kafka:** Strimzi Operator + Kafka UI
- **Redis:** Redis Operator + RedisInsight
- **PostgreSQL:** Postgres Operator
- **MongoDB:** MongoDB Operator + Compass-web
- **Elasticsearch:** cloud-on-k8s Operator + Kibana
- **Data Visualization:** Superset
- **Database DevSecOps:** Bytebase

**Application Tech Stack:**
- Python 3.11+
- FastAPI (REST API)
- python-telegram-bot (Telegram Bot)

## Architecture Principles
- Clean architecture: API/TG bot layers share business logic, separated by adapters
- Adapter pattern for external integrations (Huawei Cloud, ArgoCD, kubectl, helm, kustomize)
- GitOps for all K8s manifests managed through ArgoCD
- Infrastructure as Code with Terraform + Crossplane for hybrid resource management
- Service mesh with Linkerd for microservices communication
- Centralized secrets management: External Secrets Operator syncs from Vault, external vaults, config tools, and helmfiles
- Policy-driven governance with Kyverno for security and compliance
- Full observability with Prometheus/Grafana/Loki/Alertmanager + OpenCost for cost allocation

---

## Implementation Plan

### Phase 1: Foundation (Critical)

#### 1.1 Project Configuration
- **`pyproject.toml`** - Python project config with dependencies
- **`requirements.txt`** - Production dependencies
- **`requirements-dev.txt`** - Dev dependencies (pytest, ruff, black)
- **`.env.example`** - Environment variables template
- **Update `.gitignore`** - Add Python, IDE, Terraform, and build artifacts
- **`README.md`** - Project overview and quick start
- **`Makefile`** - Common commands (dev, test, lint, deploy, infra)

#### 1.2 Infrastructure as Code (Terraform + Crossplane)
Create `infrastructure/terraform/`:
- **`main.tf`** - Main Terraform configuration
- **`variables.tf`** - Input variables
- **`outputs.tf`** - Output values
- **`versions.tf`** - Terraform and provider versions
- **`modules/ecs/`** - Huawei Cloud ECS instance module
- **`modules/evs/`** - EVS storage module
- **`modules/obs/`** - Object storage module
- **`modules/elb/`** - Load balancer module
- **`environments/`** - dev/staging/production configurations
- **`scripts/`** - Terraform wrapper scripts

Create `infrastructure/crossplane/`:
- **`main.tf`** - Terraform for Crossplane infrastructure setup
- **`providers/`** - Crossplane provider configurations
  - **`provider-huawei/`** - Huawei Cloud provider (if available)
  - **`provider-aws/`** - AWS provider for cross-cloud resources
  - **`provider-azure/`** - Azure provider
  - **`provider-gcp/`** - GCP provider
- **`compositions/`** - Crossplane composite resource definitions
  - **`composite-database/`** - Managed database compositions
  - **`composite-storage/`** - Storage bucket compositions
  - **`composite-network/`** - Network resource compositions
- **`configs/`** - Composite resource configurations
- **`scripts/install-crossplane.sh`** - Crossplane installation script

Create `src/k8s_agent/adapters/`:
- **`crossplane_adapter.py`** - Crossplane resource management adapter
- **`external_resource_adapter.py`** - Generic external cloud resource adapter

#### 1.3 Development Environment
- **`.devcontainer/devcontainer.json`** - Coder/VS Code dev container config
- **`.devcontainer/docker-compose.yml`** - Orchestrate dev services:
  - k8s-agent application
  - Local k3s cluster for testing
  - ArgoCD local instance
  - Vault local instance
- **`.devcontainer/Dockerfile`** - Base image with Python 3.11+, kubectl, helm, helmfile, kustomize, terraform
- **`.devcontainer/requirements-dev.txt`** - Python dev dependencies

#### 1.4 Core Package Structure
Create `src/k8s_agent/` with:
- **`__init__.py`**
- **`core/interfaces.py`** - Abstract interfaces for adapters (CRITICAL)
- **`core/models.py`** - Domain models (Cluster, Deployment, Config)
- **`core/cluster_manager.py`** - Cluster lifecycle business logic
- **`core/config_manager.py`** - Configuration management
- **`core/exceptions.py`** - Custom exceptions
- **`utils/config.py`** - Config loading from env/files
- **`utils/logger.py`** - Structured logging with Loki integration
- **`utils/validators.py`** - Input validation

---

### Phase 2: Adapters Layer

#### 2.1 Base Adapter & K8s Tools
Create `src/k8s_agent/adapters/`:
- **`__init__.py`**
- **`base_adapter.py`** - Base adapter class
- **`kubectl_adapter.py`** - Kubectl operations wrapper (k3s compatible)
- **`helm_adapter.py`** - Helm chart operations
- **`helmfile_adapter.py`** - Helmfile operations
- **`kustomize_adapter.py`** - Kustomize build/apply operations

#### 2.2 Cloud & Storage Integrations
- **`argocd_adapter.py`** - ArgoCD REST API integration
- **`huawei_adapter.py`** - Huawei Cloud ECS/EVS/OBS integration
- **`rancher_adapter.py`** - Rancher API for k3s cluster management

---

### Phase 3: Security & Secrets Layer

#### 3.1 Secrets Management
Create `src/k8s_agent/security/`:
- **`__init__.py`**
- **`vault_adapter.py`** - Vault integration for secrets (self-hosted)
- **`external_secrets_adapter.py`** - External Secrets Operator integration
- **`bitwarden_adapter.py`** - Bitwarden server integration for personal secrets
- **`cert_manager_adapter.py`** - cert-manager integration for SSL/TLS
- **`secrets_manager.py`** - Unified secrets management logic
  - **Secret sources supported:**
    - Self-hosted Vault (primary)
    - External Vault instances
    - Configuration management tools (Apollo, Kusion)
    - Helmfile values
    - AWS Secrets Manager / AWS Parameter Store
    - Azure Key Vault
    - Google Secret Manager

#### 3.2 K8s Security & Governance Manifests
Create `src/manifests/base/security/`:
- **`vault/`** - Vault deployment, service, config
- **`external-secrets/`** - External Secrets Operator deployment, CRDs, config
  - **SecretStore definitions** for each external source
  - **ExternalSecret** examples for common patterns
- **`cert-manager/`** - cert-manager CRDs, deployment, configuration
- **`rbac/`** - Role-based access control policies
- **`network-policies/`** - K8s network policies
- **`pod-security-standards/`** - Pod security policies
- **`jumpserver/`** - Jumpserver bastion host
- **`velero/`** - Velero backup and restore

#### 3.3 Policy Enforcement with Kyverno
Create `src/manifests/base/governance/`:
- **`kyverno/`** - Kyverno policy engine deployment, CRDs, configuration
- **`policies/`** - Kyverno policy definitions
  - **`best-practices/`** - Security best practice policies
  - **`resource-quotas/`** - Resource quota enforcement
  - **`image-security/`** - Image verification and Trivy integration
  - **`network-policy/`** - Automatic network policy generation
  - **`compliance/`** - Compliance and regulatory policies
- **`policy-reports/`** - Policy report configuration

Create `src/k8s_agent/governance/`:
- **`__init__.py`**
- **`kyverno_adapter.py`** - Kyverno policy engine integration
- **`policy_manager.py`** - Policy management and validation
- **`quota_manager.py`** - Resource quota management
- **`cost_tracker.py`** - Cost allocation tracking (via OpenCost)

---

### Phase 3.5: Identity & Access Management

#### 3.4 IAM Provider
Create `src/manifests/base/iam/`:
- **`namespace.yaml`** - IAM namespace
- **`keycloak/`** - Keycloak deployment, service, ingress, config (if chosen)
- **`authentik/`** - Authentik deployment, service, ingress, config (if chosen)
- **`zitadel/`** - Zitadel deployment, service, ingress, config (if chosen)
- **`scripts/setup-iam.sh`** - IAM installation script

Create `src/k8s_agent/security/`:
- **`iam_adapter.py`** - IAM provider integration adapter

---

### Phase 4: Developer Tools Infrastructure

#### 4.1 Developer Portal & Tools
Create `src/manifests/base/devtools/`:
- **`backstage/`** - Backstage developer portal deployment, service, ingress, config
- **`homer/`** - Homer service portal deployment, service, config
- **`n8n/`** - n8n workflow automation deployment, service, ingress
- **`prefect/`** - Prefect workflow orchestration deployment, service, ingress
- **`dagster/`** - Dagster data orchestration deployment, service, ingress
- **`langfuse/`** - Langfuse LLM observability deployment, service, ingress
- **`gitlab/`** - GitLab instance deployment, service, ingress, registry
- **`coder/`** - Coder IDE deployment, service, ingress

Create `src/k8s_agent/adapters/`:
- **`backstage_adapter.py`** - Backstage API integration
- **`n8n_adapter.py`** - n8n workflow integration
- **`prefect_adapter.py`** - Prefect orchestration integration
- **`dagster_adapter.py`** - Dagster data orchestration integration
- **`gitlab_adapter.py`** - GitLab integration

---

### Phase 5: Service Mesh & API Gateway

#### 5.1 Linkerd Service Mesh
Create `src/manifests/base/linkerd/`:
- **`namespace.yaml`** - Linkerd namespace
- **`crds.yaml`** - Linkerd custom resource definitions
- **`deployment.yaml`** - Linkerd control plane
- **`service-profiles/`** - Service profiles for traffic management
- **`scripts/install-linkerd.sh`** - Linkerd installation script

#### 5.2 Kong API Gateway
Create `src/manifests/base/kong/`:
- **`namespace.yaml`** - Kong namespace
- **`deployment.yaml`** - Kong deployment
- **`service.yaml`** - Kong service
- **`ingress.yaml`** - Kong ingress configuration
- **`config.yaml`** - Kong configuration
- **`plugins/`** - Custom Kong plugins

---

### Phase 6: Presentation Layer

#### 6.1 FastAPI Application
Create `src/k8s_agent/api/`:
- **`main.py`** - FastAPI app entry point
- **`routes/health.py`** - Health check endpoints
- **`routes/clusters.py`** - Cluster CRUD endpoints
- **`routes/deployments.py`** - Deployment management endpoints
- **`routes/secrets.py`** - Secrets management endpoints
- **`routes/observability.py`** - Metrics and logs endpoints
- **`dependencies.py`** - FastAPI dependency injection
- **`middleware.py`** - CORS, logging, auth, Linkerd mesh middleware

#### 6.2 Telegram Bot
Create `src/k8s_agent/telegram/`:
- **`bot.py`** - Bot initialization with python-telegram-bot
- **`handlers/cluster_commands.py`** - /createcluster, /listclusters, /clusterstatus
- **`handlers/deployment_commands.py`** - /deploy, /rollback, /status
- **`handlers/secrets_commands.py`** - /getsecret, /listsecrets
- **`handlers/observability_commands.py`** - /metrics, /logs, /alerts
- **`keyboards.py`** - Inline keyboards for interactions
- **`conversations.py`** - Multi-step conversation handlers

---

### Phase 7: Observability Stack

#### 7.1 Monitoring (Prometheus + Grafana)
Create `src/manifests/base/monitoring/`:
- **`prometheus/`** - Prometheus deployment, service, config, RBAC
- **`grafana/`** - Grafana deployment, service, config, dashboards
- **`alertmanager/`** - Alertmanager deployment, service, config
- **`kube-state-metrics/`** - K8s state metrics exporter
- **`node-exporter/`** - Node metrics exporter
- **`servicemonitors/`** - ServiceMonitor CRDs for Prometheus Operator
- **`rules/`** - Prometheus alerting rules
- **`dashboards/`** - Grafana dashboard JSONs

Create `src/k8s_agent/observability/`:
- **`metrics_adapter.py`** - Prometheus metrics adapter
- **`alerts_adapter.py`** - Alertmanager integration
- **`dashboards_manager.py`** - Grafana dashboard management

#### 7.2 Application Observability (Signoz, Posthog, Sentry)
Create `src/manifests/base/app-observability/`:
- **`signoz/`** - Signoz APM deployment, service, ingress, config
- **`posthog/`** - Posthog analytics deployment, service, ingress, config
- **`sentry/`** - Sentry error tracking deployment, service, ingress, config

Create `src/k8s_agent/observability/`:
- **`signoz_adapter.py`** - Signoz APM integration
- **`posthog_adapter.py`** - Posthog analytics integration
- **`sentry_adapter.py`** - Sentry error tracking integration

#### 7.3 Logging (Loki)
Create `src/manifests/base/logging/`:
- **`loki/`** - Loki deployment, service, config
- **`promtail/`** - Promtail deployment, service, config
- **`fluentd/`** - Fluentd alternative (optional)

Create `src/k8s_agent/observability/`:
- **`logging_adapter.py`** - Loki logging adapter
- **`logger.py`** - Structured logging with Loki output

#### 7.4 Cost Management (OpenCost)
Create `src/manifests/base/cost/`:
- **`opencost/`** - OpenCost deployment, service, ingress, config
- **`prometheus/`** - OpenCost-specific Prometheus adapter configuration
- **`dashboards/`** - Grafana cost dashboards
- **`budgets/`** - Budget alert configurations

Create `src/k8s_agent/governance/`:
- **`cost_adapter.py`** - OpenCost integration for cost data
- **`budget_manager.py`** - Budget tracking and alerting
- **`allocation_manager.py`** - Cost allocation to teams/projects

---

### Phase 8: Service Infrastructure

#### 8.1 Configuration & Package Management
Create `src/manifests/base/service-infra/`:
- **`kusion/`** - Kusion configuration management deployment
- **`apollo/`** - Apollo configuration center deployment, service, ingress
- **`litellm/`** - LiteLLM deployment, service, ingress
- **`athens/`** - Athens Go module proxy deployment, service
- **`pypiserver/`** - PyPI server deployment, service
- **`verdaccio/`** - Verdaccio NPM proxy deployment, service
- **`kmcp/`** - kmcp MCP lifecycle management deployment, service
- **`kagent/`** - kagent AI agents for K8s deployment, service
- **`mcp-context-forge/`** - MCP customization deployment, service

Create `src/k8s_agent/adapters/`:
- **`kusion_adapter.py`** - Kusion configuration integration
- **`apollo_adapter.py`** - Apollo configuration center integration
- **`litellm_adapter.py`** - LiteLLM integration
- **`athens_adapter.py`** - Athens Go proxy integration
- **`kmcp_adapter.py`** - kmcp lifecycle integration
- **`kagent_adapter.py`** - AI agents integration

---

### Phase 9: Middlewares & Databases

#### 9.1 Message Queue & Caching
Create `src/manifests/base/middleware/`:
- **`kafka/`** - Strimzi operator, Kafka cluster, Kafka UI
- **`redis/`** - Redis operator, Redis cluster, RedisInsight

#### 9.2 Databases & Data Tools
- **`postgres/`** - Postgres operator, PostgreSQL cluster
- **`mongodb/`** - MongoDB operator, MongoDB cluster, Compass-web
- **`elasticsearch/`** - cloud-on-k8s operator, Elasticsearch cluster, Kibana
- **`superset/`** - Superset data visualization deployment, service, ingress
- **`bytebase/`** - Bytebase database DevSecOps deployment, service, ingress

Create `src/k8s_agent/adapters/`:
- **`kafka_adapter.py`** - Kafka operations via Strimzi
- **`redis_adapter.py`** - Redis operations
- **`postgres_adapter.py`** - Postgres operations
- **`mongodb_adapter.py`** - MongoDB operations
- **`elasticsearch_adapter.py`** - Elasticsearch operations

---

### Phase 10: GitOps Infrastructure

#### 10.1 K8s Manifests (k3s v1.32)
Create `src/manifests/`:
- **`base/argocd/`** - ArgoCD namespace, deployment, service, ingress
- **`base/k8s-agent/`** - k8s-agent namespace, deployment, service, ingress
- **`base/k3s/`** - k3s specific configurations
- **`overlays/dev/`** - Dev environment kustomization
- **`overlays/staging/`** - Staging environment kustomization
- **`overlays/production/`** - Production environment kustomization
- **`overlays/huawei-cloud/`** - Huawei Cloud specific overlays

#### 10.2 ArgoCD Applications
Create `src/manifests/base/argocd/`:
- **`apps/`** - ArgoCD Application resources
- **`appsets/`** - ArgoCD ApplicationSet resources
- **`projects/`** - ArgoCD Project definitions
- **`helmfile.yaml`** - Helmfile for ArgoCD deployment

#### 10.3 Helm Charts
- **`helm-charts/k8s-agent/`** - Helm chart for k8s-agent
- **`helm-charts/rancher/`** - Rancher management chart
- **`helm-charts/applications/`** - Example application charts

#### 10.4 Helmfile Configuration
- **`helmfile/helmfile.yaml`** - Main helmfile config
- **`helmfile/environments/`** - dev.yaml, staging.yaml, production.yaml
- **`helmfile/releases/`** - Release definitions for all services

---

### Phase 11: Scripts

Create `scripts/`:
- **`setup/install-dev-tools.sh`** - Install kubectl, helm, helmfile, kustomize, terraform, k3s
- **`setup/setup-k3s-cluster.sh`** - Setup local k3s cluster
- **`setup/init-argocd.sh`** - Initialize ArgoCD on k3s
- **`setup/install-linkerd.sh`** - Install Linkerd service mesh
- **`setup/install-vault.sh`** - Install Vault
- **`setup/install-monitoring.sh`** - Install Prometheus, Grafana, Loki, Alertmanager

- **`infrastructure/terraform-apply.sh`** - Apply Terraform configurations
- **`infrastructure/terraform-destroy.sh`** - Destroy Terraform resources
- **`infrastructure/terraform-plan.sh`** - Plan Terraform changes

- **`deployment/build.sh`** - Build Docker images
- **`deployment/push.sh`** - Push to registry
- **`deployment/deploy.sh`** - Deploy to cluster via ArgoCD
- **`deployment/rollback.sh`** - Rollback deployment

- **`cluster/create-cluster.sh`** - Create k3s cluster on Huawei ECS
- **`cluster/delete-cluster.sh`** - Delete cluster
- **`cluster/scale-cluster.sh`** - Scale cluster nodes
- **`cluster/upgrade-cluster.sh`** - Upgrade k3s version

- **`development/run-dev.sh`** - Run development server
- **`development/run-tests.sh`** - Run test suite
- **`development/format-code.sh`** - Format with black/ruff
- **`development/lint.sh`** - Lint with ruff
- **`development/setup-coder.sh`** - Setup Coder IDE

- **`observability/grafana-dashboards.sh`** - Import Grafana dashboards
- **`observability/backup-loki.sh`** - Backup Loki logs
- **`observability/test-alerts.sh`** - Test Alertmanager alerts

- **`cicd/validate-manifests.sh`** - Validate K8s manifests
- **`cicd/ci-build.sh`** - CI pipeline entry
- **`cicd/cd-deploy.sh`** - CD pipeline entry

- **`devtools/setup-backstage.sh`** - Setup Backstage developer portal
- **`devtools/setup-n8n.sh`** - Setup n8n workflow automation
- **`devtools/setup-prefect.sh`** - Setup Prefect orchestration
- **`devtools/setup-dagster.sh`** - Setup Dagster data orchestration
- **`devtools/setup-langfuse.sh`** - Setup Langfuse observability

- **`service-infra/setup-kusion.sh`** - Setup Kusion configuration
- **`service-infra/setup-apollo.sh`** - Setup Apollo config center
- **`service-infra/setup-litellm.sh`** - Setup LiteLLM
- **`service-infra/setup-athens.sh`** - Setup Athens Go proxy
- **`service-infra/setup-pypiserver.sh`** - Setup PyPI server
- **`service-infra/setup-verdaccio.sh`** - Setup Verdaccio NPM proxy
- **`service-infra/setup-kmcp.sh`** - Setup kmcp lifecycle
- **`service-infra/setup-kagent.sh`** - Setup kagent AI agents

- **`middleware/setup-kafka.sh`** - Setup Kafka via Strimzi
- **`middleware/setup-redis.sh`** - Setup Redis
- **`middleware/setup-postgres.sh`** - Setup Postgres
- **`middleware/setup-mongodb.sh`** - Setup MongoDB
- **`middleware/setup-elasticsearch.sh`** - Setup Elasticsearch
- **`middleware/setup-superset.sh`** - Setup Superset
- **`middleware/setup-bytebase.sh`** - Setup Bytebase

- **`iam/setup-keycloak.sh`** - Setup Keycloak (or authentik/zitadel)
- **`iam/configure-iam.sh`** - Configure IAM provider

- **`backup/setup-velero.sh`** - Setup Velero backup
- **`backup/backup-cluster.sh`** - Backup cluster resources
- **`backup/restore-cluster.sh`** - Restore cluster resources

---

### Phase 12: Documentation

Create documentation in `docs/`:
- **`requirements/functional-requirements.md`** - Functional requirements
- **`requirements/non-functional-requirements.md`** - NFRs (performance, security, scalability)
- **`requirements/api-requirements.md`** - API specifications

- **`biz/architecture.md`** - System architecture overview
- **`biz/cluster-lifecycle.md`** - Cluster management flows
- **`biz/gitops-workflow.md`** - GitOps processes
- **`biz/integrations.md`** - Integration patterns
- **`biz/devtools-architecture.md`** - Developer tools architecture
- **`biz/service-infra.md`** - Service infrastructure design
- **`biz/middleware-stack.md`** - Middleware and database architecture

- **`AI-external-context/huawei-cloud-ecs.md`** - Huawei Cloud ECS API context
- **`AI-external-context/huawei-cloud-storage.md`** - EVS, SCS, OBS context
- **`AI-external-context/argocd-implementation.md`** - ArgoCD specifics
- **`AI-external-context/k3s-architecture.md`** - k3s lightweight K8s context
- **`AI-external-context/linkerd-mesh.md`** - Linkerd service mesh context
- **`AI-external-context/prometheus-grafana.md`** - Monitoring stack context
- **`AI-external-context/vault-secrets.md`** - Vault secrets management context
- **`AI-external-context/signoz-apm.md`** - Signoz APM context
- **`AI-external-context/posthog-analytics.md`** - Posthog analytics context
- **`AI-external-context/sentry-tracking.md`** - Sentry error tracking context
- **`AI-external-context/backstage-portal.md`** - Backstage developer portal context
- **`AI-external-context/kusion-config.md`** - Kusion configuration context
- **`AI-external-context/kmcp-kagent.md`** - MCP and AI agents context
- **`AI-external-context/keycloak-iam.md`** - Keycloak IAM context

- **`development/26-01-08/decisions.md`** - Architecture decisions record (ADR)
- **`development/26-01-08/progress-log.md`** - Implementation progress log
- **`development/26-01-08/initial-setup-plan.md`** - This plan

- **`operations/runbook.md`** - Operational runbook
- **`operations/troubleshooting.md`** - Common issues and solutions
- **`operations/backup-restore.md`** - Backup and restore procedures

---

### Phase 13: Testing

Create `src/tests/`:
- **`conftest.py`** - Pytest configuration with fixtures
- **`unit/test_core/`** - Core business logic tests
- **`unit/test_adapters/`** - Adapter tests with mocks (Huawei, ArgoCD, Vault, Linkerd)
- **`unit/test_security/`** - Security and secrets management tests
- **`integration/test_api/`** - FastAPI endpoint tests
- **`integration/test_telegram/`** - Bot command tests
- **`integration/test_k8s_operations/`** - E2E tests with k3s
- **`integration/test_observability/`** - Monitoring and logging tests
- **`e2e/test_gitops_flow.py`** - Complete GitOps workflow test
- **`e2e/test_secrets_flow.py`** - Complete secrets management test
- **`fixtures/`** - Test fixtures and mocks
- **`performance/`** - Performance and load tests

---

## Critical Files (Implementation Order)

### Top 10 Most Critical Files

1. **`infrastructure/terraform/main.tf`** - Terraform infrastructure entry point
2. **`src/k8s_agent/core/interfaces.py`** - Foundation for all adapters
3. **`pyproject.toml`** - Python project configuration
4. **`.devcontainer/docker-compose.yml`** - Complete dev environment
5. **`src/k8s_agent/core/cluster_manager.py`** - Core business logic
6. **`src/k8s_agent/adapters/huawei_adapter.py`** - Huawei Cloud ECS/EVS/OBS integration
7. **`src/k8s_agent/security/vault_adapter.py`** - Vault secrets integration
8. **`src/manifests/base/k3s/`** - k3s v1.32 cluster manifests
9. **`src/manifests/base/monitoring/prometheus/`** - Monitoring stack
10. **`scripts/setup/install-monitoring.sh`** - Observability setup

### Other Critical Files

11. **`src/k8s_agent/api/main.py`** - FastAPI application entry
12. **`src/k8s_agent/telegram/bot.py`** - Telegram bot entry
13. **`src/manifests/base/argocd/`** - ArgoCD GitOps manifests
14. **`src/manifests/base/linkerd/`** - Linkerd service mesh
15. **`src/manifests/base/kong/`** - Kong API gateway
16. **`src/k8s_agent/observability/metrics_adapter.py`** - Prometheus integration
17. **`src/manifests/base/devtools/`** - Developer tools manifests
18. **`src/manifests/base/service-infra/`** - Service infrastructure manifests
19. **`src/manifests/base/middleware/`** - Middleware and database manifests
20. **`src/manifests/base/iam/`** - IAM provider manifests
21. **`src/k8s_agent/adapters/devtools_adapter.py`** - Developer tools adapters
22. **`scripts/infrastructure/terraform-apply.sh`** - Infrastructure deployment
23. **`scripts/setup/setup-k3s-cluster.sh`** - Local k3s setup
24. **`docs/biz/architecture.md`** - Architecture documentation
25. **`docs/AI-external-context/`** - AI context documentation

---

## Key Dependencies

### Python Application Dependencies
```
# Web Framework
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
pydantic-settings>=2.1.0

# Kubernetes
kubernetes>=28.1.0
pyyaml>=6.0.1
jinja2>=3.1.3

# Telegram Bot
python-telegram-bot>=21.0

# HTTP Clients
httpx>=0.26.0
aiohttp>=3.9.1

# Huawei Cloud SDK
huaweicloudsdkcore>=3.0.0
huaweicsdkecs>=3.0.0

# Observability
prometheus-client>=0.19.0
grafana-api>=1.0.0
loki-client>=0.1.0
signoz-api>=0.1.0  # Signoz APM
posthog>=3.0.0  # Posthog analytics
sentry-sdk>=1.40.0  # Sentry error tracking

# Secrets & Security
hvac>=2.1.0  # Vault
python-bitwarden>=0.1.0
cryptography>=41.0.0

# Governance & Cost
kubernetes>=28.1.0  # For Kyverno/Crossplane resources
pyyaml>=6.0.1  # Policy/config parsing

# Utilities
python-dotenv>=1.0.0
structlog>=24.1.0
click>=8.1.7
rich>=13.7.0
```

### Development Dependencies
```
pytest>=8.0.0
pytest-asyncio>=0.23.4
pytest-cov>=4.1.0
pytest-mock>=3.12.0
ruff>=0.2.0
black>=24.1.0
mypy>=1.8.0
pre-commit>=3.6.0
```

### External Tools & Infrastructure

**Kubernetes & Tools:**
- kubectl v1.29+ (k3s compatible)
- k3s v1.32
- helm v3.14+
- helmfile v0.157+
- kustomize v5.3+

**Infrastructure:**
- Terraform v1.6+
- Terraform provider for Huawei Cloud
- Crossplane v1.18+ (for external cloud resource management)
- Crossplane providers (Huawei Cloud, AWS, Azure, GCP as needed)

**Service Mesh & Gateway:**
- Linkerd v2.15+ (stable)
- Kong v3.5+

**Observability:**
- Prometheus v2.48+
- Grafana v10.3+
- Loki v2.9+
- Alertmanager v0.26+
- Promtail v2.9+
- Signoz (APM)
- Posthog (Analytics)
- Sentry (Error Tracking)
- OpenCost (Cost Management)

**Security & Governance:**
- Vault v1.15+
- External Secrets Operator v0.9+
- cert-manager v1.14+
- Bitwarden server v2024.x
- Keycloak / Authentik / Zitadel (IAM)
- Jumpserver (Bastion Host)
- Kyverno v1.12+ (Policy Engine)
- Trivy (Image Scanning - integrated in Harbor)

**GitOps:**
- ArgoCD v2.9+

**Development:**
- Coder v2.x (for remote IDE)
- GitLab (self-managed or cloud)

**Developer Tools:**
- Backstage (Developer Portal)
- Homer (Service Portal)
- n8n (Workflow Automation)
- Prefect (Workflow Orchestration)
- Dagster (Data Orchestration)
- Langfuse (LLM Observability)

**Service Infrastructure:**
- Kusion (Config Management)
- Apollo (Configuration Center)
- LiteLLM (Local LLM)
- Athens (Go Module Proxy)
- pypiserver (Python Package Index)
- Verdaccio (NPM Package Proxy)
- kmcp (MCP Lifecycle)
- kagent (AI Agents for K8s)

**Middlewares & Databases:**
- Strimzi (Kafka Operator)
- Kafka UI
- Redis Operator
- RedisInsight
- Postgres Operator
- MongoDB Operator
- Compass-web (MongoDB GUI)
- cloud-on-k8s (Elasticsearch Operator)
- Kibana
- Superset (Data Visualization)
- Bytebase (Database DevSecOps)

**Backup:**
- Velero (K8s Backup/Restore)

---

## Integration Points

### 1. **API ↔ Business Logic**
- FastAPI routes inject business logic via dependency injection
- Business logic returns domain models to API
- API handles HTTP concerns (status codes, validation, Linkerd headers)
- No business logic in API layer

### 2. **Telegram Bot ↔ Business Logic**
- Bot handlers call business logic directly
- Business logic operations are identical to API calls
- Bot handles Telegram-specific concerns (messages, keyboards)
- Shared business logic ensures consistency

### 3. **Business Logic ↔ Adapters**
- Business logic depends on interfaces, not concrete adapters
- Adapters implement standard interfaces
- Enables easy swapping/testing of integrations
- Adapter pattern handles external API differences

### 4. **GitOps Flow**
- Developers commit to Git repository (GitLab)
- ArgoCD watches Git repository
- ArgoCD syncs changes to k3s cluster
- k8s-agent monitors cluster state via kubectl adapter
- k8s-agent reports status via API/Telegram
- Kong API Gateway routes external traffic
- Linkerd handles service-to-service communication

### 5. **Huawei Cloud Integration**
- Terraform provisions ECS instances, EVS storage, OBS buckets, ELB
- huawei_adapter manages Huawei Cloud resources
- k3s runs on Huawei Cloud ECS instances
- Storage backed by EVS, SCS, OBS as needed

### 6. **Observability Integration**
- Applications log to Loki via Promtail/structlog
- Prometheus scrapes metrics from applications and k3s
- Grafana visualizes metrics and logs
- Alertmanager sends alerts via API/Telegram
- k8s-agent aggregates observability data

### 7. **Secrets Management**
- Vault stores application secrets (self-hosted)
- External Secrets Operator syncs secrets from multiple sources:
  - External Vault instances
  - Configuration management tools (Apollo, Kusion)
  - Helmfile values
  - AWS Secrets Manager / Parameter Store
  - Azure Key Vault
  - Google Secret Manager
- cert-manager manages SSL/TLS certificates
- Bitwarden for personal/separate secrets
- Adapters provide unified interface to all secrets sources
- Services read secrets from Kubernetes secrets synced by External Secrets Operator

### 8. **Governance & Policy Enforcement**
- Kyverno enforces security policies automatically
- Policies validate resource configurations before deployment
- Kyverno generates network policies automatically
- Image verification with Trivy integration
- Resource quotas enforced per namespace/team
- OpenCost tracks cost allocation per team/project
- Budget alerts triggered via Alertmanager

### 9. **External Resource Management**
- Crossplane manages external cloud resources via Kubernetes CRDs
- Hybrid cloud support: Huawei Cloud, AWS, Azure, GCP
- Managed databases, storage, networking via Crossplane compositions
- GitOps for external resources via ArgoCD
- Unified API for both K8s and cloud resources

---

## Architecture Diagram

**Note:** The architecture below includes all new components from the expanded infrastructure stack.

```
┌─────────────────────────────────────────────────────────────────┐
│                         External Users                           │
│  ┌──────────────┐              ┌──────────────┐                │
│  │   Web UI     │              │  Telegram    │                │
│  │  (Kong +     │              │     Bot      │                │
│  │   Linkerd)   │              │              │                │
│  └──────┬───────┘              └──────┬───────┘                │
└─────────┼──────────────────────────────┼────────────────────────┘
          │                              │
          ▼                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      k3s Cluster v1.32                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Linkerd Service Mesh                       │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │  k8s-agent   │  │   ArgoCD     │  │  Monitoring  │  │   │
│  │  │  (FastAPI +  │  │  (GitOps)    │  │  (Prometheus │  │   │
│  │  │   Telegram)  │  │              │  │  + Grafana   │  │   │
│  │  │              │  │              │  │  + Loki)     │  │   │
│  │  │  ┌────────┐  │  │              │  │              │  │   │
│  │  │  │  Core  │  │  │              │  │              │  │   │
│  │  │  │   +    │  │  │              │  │              │  │   │
│  │  │  │Adapters│  │  │              │  │              │  │   │
│  │  │  └───┬────┘  │  │              │  │              │  │   │
│  │  └──────┼───────┘  └──────────────┘  └──────────────┘  │   │
│  └─────────┼─────────────────────────────────────────────────┘   │
│            │                                                    │
│  ┌─────────▼─────────────────────────────────────────────────┐  │
│  │              Vault + cert-manager                          │  │
│  │              (Secrets & Certificates)                      │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Huawei Cloud ECS                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │   EVS    │  │   SCS    │  │   OBS    │  │   ELB    │      │
│  │ (Block)  │  │ (Shared) │  │ (Object) │  │  (Load)  │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────────────────────┘

                              ▲
                              │
┌─────────────────────────────┴─────────────────────────────────────┐
│                    GitLab (Git Repository)                       │
│                    (ArgoCD watches & syncs)                      │
└───────────────────────────────────────────────────────────────────┘
```

---

## Security Considerations

1. **Authentication & Authorization**
   - JWT tokens for API
   - Telegram user ID verification
   - Role-based access control (RBAC)
   - Linkerd mTLS for service-to-service

2. **Secrets Management**
   - Vault for application secrets
   - Kubernetes secrets for runtime
   - Sealed Secrets for GitOps
   - Bitwarden for personal secrets
   - cert-manager for SSL/TLS certificates

3. **Network Security**
   - TLS/SSL for all external communications
   - Network policies in k3s
   - Linkerd mTLS for internal traffic
   - Firewall rules for Huawei Cloud
   - Kong API Gateway for rate limiting

4. **Infrastructure Security**
   - Terraform state encryption
   - Immutable infrastructure
   - Regular security updates
   - Pod security standards

---

## Next Steps After Approval

1. **Begin with Phase 1** - Foundation (Project config, Terraform infra, Dev env, Core package)
2. **Implement Phase 2** - Adapters layer (K8s tools, Cloud integrations)
3. **Build Phase 3** - Security layer (Vault, cert-manager, RBAC)
4. **Setup Phase 4** - Service mesh (Linkerd) & API gateway (Kong)
5. **Create Phase 5** - Presentation layer (FastAPI, Telegram bot)
6. **Deploy Phase 6** - Observability stack (Prometheus, Grafana, Loki, Alertmanager)
7. **Configure Phase 7** - GitOps infrastructure (ArgoCD, Helm, Kustomize)
8. **Write Phase 8** - All automation scripts
9. **Document Phase 9** - Complete documentation
10. **Test Phase 10** - Comprehensive testing suite

---

## Files to Create Summary

**Estimated 450-550 files across the repository (expanded with governance and cost management):**

**Root Level (9 files):**
- pyproject.toml, requirements.txt, requirements-dev.txt, .env.example
- Update .gitignore, README.md, Makefile
- Dockerfile, docker-compose.yml

**infrastructure/terraform (15+ files):**
- main.tf, variables.tf, outputs.tf, versions.tf
- modules/ecs, modules/evs, modules/obs, modules/elb
- environments/dev, environments/staging, environments/production

**.devcontainer (4 files):**
- devcontainer.json, docker-compose.yml, Dockerfile, requirements-dev.txt

**src/k8s_agent/core (7 files):**
- interfaces.py, models.py, cluster_manager.py, config_manager.py, exceptions.py

**src/k8s_agent/adapters (25+ files):**
- base_adapter.py, kubectl_adapter.py, helm_adapter.py, helmfile_adapter.py, kustomize_adapter.py, argocd_adapter.py, huawei_adapter.py, rancher_adapter.py
- **NEW:** backstage_adapter.py, n8n_adapter.py, prefect_adapter.py, dagster_adapter.py, gitlab_adapter.py
- **NEW:** kusion_adapter.py, apollo_adapter.py, litellm_adapter.py, athens_adapter.py, kmcp_adapter.py, kagent_adapter.py
- **NEW:** kafka_adapter.py, redis_adapter.py, postgres_adapter.py, mongodb_adapter.py, elasticsearch_adapter.py
- **NEW:** jumpserver_adapter.py, velero_adapter.py, signoz_adapter.py, posthog_adapter.py, sentry_adapter.py
- **NEW:** crossplane_adapter.py, external_resource_adapter.py, external_secrets_adapter.py, kyverno_adapter.py

**src/k8s_agent/security (7 files):**
- vault_adapter.py, bitwarden_adapter.py, cert_manager_adapter.py, secrets_manager.py
- **NEW:** iam_adapter.py, jumpserver_adapter.py, velero_adapter.py, external_secrets_adapter.py

**src/k8s_agent/governance (7 files):** - **NEW SECTION**
- kyverno_adapter.py, policy_manager.py, quota_manager.py, cost_tracker.py, cost_adapter.py, budget_manager.py, allocation_manager.py

**src/k8s_agent/api (8 files):**
- main.py, routes/health.py, routes/clusters.py, routes/deployments.py, routes/secrets.py, routes/observability.py, dependencies.py, middleware.py

**src/k8s_agent/telegram (7 files):**
- bot.py, handlers/cluster_commands.py, handlers/deployment_commands.py, handlers/secrets_commands.py, handlers/observability_commands.py, keyboards.py, conversations.py

**src/k8s_agent/observability (7 files):**
- metrics_adapter.py, alerts_adapter.py, dashboards_manager.py, logging_adapter.py, logger.py
- **NEW:** signoz_adapter.py, posthog_adapter.py, sentry_adapter.py

**src/k8s_agent/utils (4 files):**
- config.py, logger.py, validators.py

**src/manifests (300+ yaml files):**
- base/argocd, base/k8s-agent, base/k3s, base/monitoring, base/logging, base/security, base/linkerd, base/kong
- **NEW:** base/governance (kyverno, policies, policy-reports)
- **NEW:** base/cost (opencost, dashboards, budgets)
- **NEW:** base/external-secrets (external-secrets-operator, secretstore definitions)
- **NEW:** base/crossplane (providers, compositions, configs)
- **NEW:** base/devtools (backstage, homer, n8n, prefect, dagster, langfuse, gitlab, coder)
- **NEW:** base/service-infra (kusion, apollo, litellm, athens, pypiserver, verdaccio, kmcp, kagent, mcp-context-forge)
- **NEW:** base/middleware (kafka, redis, postgres, mongodb, elasticsearch, superset, bytebase)
- **NEW:** base/iam (keycloak/authentik/zitadel)
- **NEW:** base/app-observability (signoz, posthog, sentry)
- **NEW:** base/backup (velero, jumpserver)
- overlays/dev, overlays/staging, overlays/production, overlays/huawei-cloud

**scripts (70+ shell scripts):**
- setup/, infrastructure/, deployment/, cluster/, development/, observability/, cicd/
- **NEW:** devtools/, service-infra/, middleware/, iam/, backup/
- **NEW:** governance/ (kyverno policies, cost management)
- **NEW:** crossplane/ (provider setup, composition management)

**docs (40+ markdown files):**
- requirements/, biz/, AI-external-context/, development/, operations/
- **NEW:** biz/devtools-architecture.md, biz/service-infra.md, biz/middleware-stack.md
- **NEW:** biz/governance-model.md, biz/cost-allocation.md, biz/multi-tenancy.md
- **NEW:** AI-external-context/signoz-apm.md, posthog-analytics.md, sentry-tracking.md
- **NEW:** AI-external-context/backstage-portal.md, kusion-config.md, kmcp-kagent.md, keycloak-iam.md
- **NEW:** AI-external-context/kyverno-policies.md, external-secrets-operator.md, crossplane-integration.md, opencost-usage.md

**src/tests (30+ test files):**
- unit/, integration/, e2e/, fixtures/, performance/

---

## Implementation Priority

**Must-Have (Week 1-3):**
- Phase 1: Foundation
- Phase 2: Adapters Layer
- Phase 3: Security & Secrets
- Phase 3.5: IAM
- Phase 10: GitOps Infrastructure (basic)

**Should-Have (Week 4-6):**
- Phase 4: Developer Tools Infrastructure
- Phase 5: Service Mesh & API Gateway
- Phase 6: Presentation Layer
- Phase 7: Observability Stack

**Nice-to-Have (Week 7-12):**
- Phase 8: Service Infrastructure
- Phase 9: Middlewares & Databases
- Phase 11: Scripts (comprehensive)
- Phase 12: Documentation (detailed)
- Phase 13: Testing (comprehensive)

**Timeline:**
- MVP (Minimum Viable Product): 6 weeks (Phases 1-3, 3.5, 10)
- Full Implementation: 12 weeks (All 13 phases)
