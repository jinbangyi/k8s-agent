# k8s-agent TODO List

## Completed

- [x] Initial planning - Created comprehensive initial setup plan (docs/development/26-01-08/initial-setup-plan.md)

## Phase 1: Foundation

### 1.1 Project Configuration
- [ ] Create pyproject.toml with dependencies
- [ ] Create requirements.txt (production)
- [ ] Create requirements-dev.txt (dev)
- [ ] Create .env.example
- [ ] Update .gitignore
- [ ] Create README.md
- [ ] Create Makefile

### 1.2 Infrastructure as Code (Terraform)
- [ ] Create infrastructure/terraform/main.tf
- [ ] Create infrastructure/terraform/variables.tf
- [ ] Create infrastructure/terraform/outputs.tf
- [ ] Create infrastructure/terraform/versions.tf
- [ ] Create infrastructure/terraform/modules/ecs/
- [ ] Create infrastructure/terraform/modules/evs/
- [ ] Create infrastructure/terraform/modules/obs/
- [ ] Create infrastructure/terraform/modules/elb/
- [ ] Create infrastructure/terraform/environments/

### 1.3 Development Environment
- [ ] Create .devcontainer/devcontainer.json
- [ ] Create .devcontainer/docker-compose.yml
- [ ] Create .devcontainer/Dockerfile
- [ ] Create .devcontainer/requirements-dev.txt

### 1.4 Core Package Structure
- [ ] Create src/k8s_agent/__init__.py
- [ ] Create src/k8s_agent/core/interfaces.py (CRITICAL)
- [ ] Create src/k8s_agent/core/models.py
- [ ] Create src/k8s_agent/core/cluster_manager.py
- [ ] Create src/k8s_agent/core/config_manager.py
- [ ] Create src/k8s_agent/core/exceptions.py
- [ ] Create src/k8s_agent/utils/config.py
- [ ] Create src/k8s_agent/utils/logger.py
- [ ] Create src/k8s_agent/utils/validators.py

## Phase 2: Adapters Layer

- [ ] Create src/k8s_agent/adapters/__init__.py
- [ ] Create src/k8s_agent/adapters/base_adapter.py
- [ ] Create src/k8s_agent/adapters/kubectl_adapter.py
- [ ] Create src/k8s_agent/adapters/helm_adapter.py
- [ ] Create src/k8s_agent/adapters/helmfile_adapter.py
- [ ] Create src/k8s_agent/adapters/kustomize_adapter.py
- [ ] Create src/k8s_agent/adapters/argocd_adapter.py
- [ ] Create src/k8s_agent/adapters/huawei_adapter.py
- [ ] Create src/k8s_agent/adapters/rancher_adapter.py

## Phase 3: Security & Secrets Layer

- [ ] Create src/k8s_agent/security/__init__.py
- [ ] Create src/k8s_agent/security/vault_adapter.py
- [ ] Create src/k8s_agent/security/bitwarden_adapter.py
- [ ] Create src/k8s_agent/security/cert_manager_adapter.py
- [ ] Create src/k8s_agent/security/secrets_manager.py
- [ ] Create src/manifests/base/security/ (vault, cert-manager, rbac, network-policies)

## Phase 4: Service Mesh & API Gateway

- [ ] Create src/manifests/base/linkerd/
- [ ] Create src/manifests/base/kong/
- [ ] Create scripts/setup/install-linkerd.sh

## Phase 5: Presentation Layer

### FastAPI Application
- [ ] Create src/k8s_agent/api/main.py
- [ ] Create src/k8s_agent/api/routes/health.py
- [ ] Create src/k8s_agent/api/routes/clusters.py
- [ ] Create src/k8s_agent/api/routes/deployments.py
- [ ] Create src/k8s_agent/api/routes/secrets.py
- [ ] Create src/k8s_agent/api/routes/observability.py
- [ ] Create src/k8s_agent/api/dependencies.py
- [ ] Create src/k8s_agent/api/middleware.py

### Telegram Bot
- [ ] Create src/k8s_agent/telegram/bot.py
- [ ] Create src/k8s_agent/telegram/handlers/cluster_commands.py
- [ ] Create src/k8s_agent/telegram/handlers/deployment_commands.py
- [ ] Create src/k8s_agent/telegram/handlers/secrets_commands.py
- [ ] Create src/k8s_agent/telegram/handlers/observability_commands.py
- [ ] Create src/k8s_agent/telegram/keyboards.py
- [ ] Create src/k8s_agent/telegram/conversations.py

## Phase 6: Observability Stack

- [ ] Create src/manifests/base/monitoring/ (prometheus, grafana, alertmanager)
- [ ] Create src/manifests/base/logging/ (loki, promtail)
- [ ] Create src/k8s_agent/observability/metrics_adapter.py
- [ ] Create src/k8s_agent/observability/alerts_adapter.py
- [ ] Create src/k8s_agent/observability/dashboards_manager.py
- [ ] Create src/k8s_agent/observability/logging_adapter.py

## Phase 7: GitOps Infrastructure

- [ ] Create src/manifests/base/argocd/
- [ ] Create src/manifests/base/k8s-agent/
- [ ] Create src/manifests/base/k3s/
- [ ] Create src/manifests/overlays/dev/
- [ ] Create src/manifests/overlays/staging/
- [ ] Create src/manifests/overlays/production/
- [ ] Create src/manifests/overlays/huawei-cloud/
- [ ] Create src/helm-charts/k8s-agent/
- [ ] Create src/helmfile/

## Phase 8: Scripts

- [ ] Create scripts/setup/
- [ ] Create scripts/infrastructure/
- [ ] Create scripts/deployment/
- [ ] Create scripts/cluster/
- [ ] Create scripts/development/
- [ ] Create scripts/observability/
- [ ] Create scripts/cicd/

## Phase 9: Documentation

- [ ] Create docs/requirements/
- [ ] Create docs/biz/
- [ ] Create docs/AI-external-context/
- [ ] Create docs/development/26-01-08/decisions.md
- [ ] Create docs/development/26-01-08/progress-log.md
- [ ] Create docs/operations/

## Phase 10: Testing

- [ ] Create src/tests/conftest.py
- [ ] Create src/tests/unit/
- [ ] Create src/tests/integration/
- [ ] Create src/tests/e2e/
- [ ] Create src/tests/fixtures/
- [ ] Create src/tests/performance/
