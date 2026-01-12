# Phase 3: Security & Governance Setup

## Overview
Implement security foundations including Vault for secrets, External Secrets Operator for multi-source secrets sync, Kyverno for policy enforcement, and IAM provider.

---

## 3.1 Vault Installation

### Install Vault for Self-Hosted Secrets

#### `scripts/setup/install-vault.sh`
```bash
#!/bin/bash
set -e

# Add HashiCorp helm repo
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update

# Create Vault namespace
kubectl create namespace vault --dry-run=client -o yaml | kubectl apply -f -

# Create Vault storage using EVS
kubectl apply -f manifests/base/vault/storage.yaml

# Install Vault
helm upgrade --install vault hashicorp/vault \
  --namespace vault \
  --set global.openshift=true \
  --set injector.enabled=true \
  --set injector.externalTlsCert=/cert-manager/tls.crt \
  --set injector.externalTlsKey=/cert-manager/tls.key \
  --set server.dev.enabled=false \
  --set server.dataStorage.enabled=true \
  --set server.dataStorage.size=10Gi \
  --set server.ha.enabled=true \
  --set server.ha.replicas=3 \
  --set ui.enabled=true \
  --set ui.serviceType=LoadBalancer \
  --wait

# Wait for Vault to be ready
kubectl wait --for=condition=available deployment/vault -n vault --timeout=300s

# Initialize and unseal
kubectl exec -n vault vault-0 -- vault operator init -key-shares=5 -key-threshold=3 -format=json > vault-init.json

# Unseal Vault
UNSEAL_KEYS=$(jq -r '.unseal_keys_b64[:3]' vault-init.json)
for KEY in $UNSEAL_KEYS; do
  kubectl exec -n vault vault-0 -- vault operator unseal $KEY
  kubectl exec -n vault vault-1 -- vault operator unseal $KEY
  kubectl exec -n vault vault-2 -- vault operator unseal $KEY
done

# Save root token
jq -r '.root_token' vault-init.json > vault-root-token.txt

echo "Vault installed and initialized!"
echo "Root token saved to vault-root-token.txt"
```

### Vault Configuration

#### `src/manifests/base/vault/config.yaml`
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: vault-config
  namespace: vault
data:
  vault.hcl: |
    listener "tcp" {
      address       = "[::]:8200"
      cluster_address = "[::]:8201"
      tls_cert_file = "/vault/userconfig/tls-server/tls.crt"
      tls_key_file  = "/vault/userconfig/tls-server/tls.key"
      tls_client_ca_file = "/vault/userconfig/tls-ca/tls.crt"
    }

    storage "raft" {
      path = "/vault/data"
    }

    api_addr = "https://vault.vault.svc.cluster.local:8200"
    cluster_addr = "https://vault.vault.svc.cluster.local:8201"

    ui = true

    # Enable audit logging
    audit {
      enabled = true
      path = "file"
      options {
        path = "/vault/logs/audit.log"
      }
    }
```

#### `src/manifests/base/vault/storage.yaml`
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: vault-data
  namespace: vault
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: huaweicloud-ssd
```

---

## 3.2 External Secrets Operator

### Install External Secrets Operator

#### `scripts/setup/install-external-secrets.sh`
```bash
#!/bin/bash
set -e

# Add ESO helm repo
helm repo add external-secrets https://charts.external-secrets.io
helm repo update

# Install External Secrets Operator
helm upgrade --install external-secrets external-secrets/external-secrets \
  --namespace external-secrets \
  --create-namespace \
  --set installCRDs=true \
  --wait

echo "External Secrets Operator installed!"
```

### Configure Secret Stores

#### `src/manifests/base/external-secrets/secretstore-vault.yaml`
```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
  namespace: external-secrets
spec:
  provider:
    vault:
      server: "https://vault.vault.svc.cluster.local:8200"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "external-secrets"
          serviceAccountRef:
            name: external-secrets
```

#### `src/manifests/base/external-secrets/secretstore-aws.yaml`
```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: external-secrets
spec:
  provider:
    aws:
      service: SecretsManager
      region: cn-north-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets
```

#### `src/manifests/base/external-secrets/secretstore-apollo.yaml`
```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: apollo-config
  namespace: external-secrets
spec:
  provider:
    webhook:
      url: "http://apollo-portal.apollo.svc.cluster.local/config"
      result:
        jsonPath: "$.data"
      headers:
        - name: "Content-Type"
          value: "application/json"
```

### Example External Secret

#### `src/manifests/base/external-secrets/examples/database-credentials.yaml`
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: database-credentials
  namespace: default
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: db-credentials
    creationPolicy: Owner
  data:
  - secretKey: username
    remoteRef:
      key: "secret/data/database/creds"
      property: username
  - secretKey: password
    remoteRef:
      key: "secret/data/database/creds"
      property: password
```

---

## 3.3 Kyverno Policy Engine

### Install Kyverno

#### `scripts/setup/install-kyverno.sh`
```bash
#!/bin/bash
set -e

# Install Kyverno
kubectl apply -f https://raw.githubusercontent.com/kyverno/kyverno/main/config/release/install.yaml

# Wait for Kyverno to be ready
kubectl wait --for=condition=available deployment/kyverno-admission-controller -n kyverno --timeout=300s

# Install policies
kubectl apply -f manifests/base/governance/policies/

echo "Kyverno installed with policies!"
```

### Kyverno Policies

#### `src/manifests/base/governance/policies/best-practices/pod-security.yaml`
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: pod-security
  annotations:
    policies.kyverno.io/title: Pod Security Standards
    policies.kyverno.io/category: Pod Security
spec:
  validationFailureAction: enforce
  background: true
  rules:
  - name: require-run-as-nonroot
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "Containers must run as non-root"
      pattern:
        spec:
          containers:
          - securityContext:
              runAsNonRoot: true

  - name: require-dropped-capabilities
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "Containers must drop ALL capabilities"
      pattern:
        spec:
          containers:
          - securityContext:
              capabilities:
                drop:
                - ALL

  - name: require-read-only-root
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "Root filesystem must be read-only"
      pattern:
        spec:
          containers:
          - securityContext:
              readOnlyRootFilesystem: true
```

#### `src/manifests/base/governance/policies/resource-quotas/namespace-quota.yaml`
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-resource-quotas
  annotations:
    policies.kyverno.io/title: Require Resource Quotas
spec:
  validationFailureAction: enforce
  background: true
  rules:
  - name: check-resource-quota
    match:
      any:
      - resources:
          kinds:
          - Namespace
    preconditions:
      all:
      - key: "{{request.object.metadata.name}}"
        operator: NotIn
        value: ["kube-system", "kube-public", "kube-node-lease", "default", "kyverno"]
    validate:
      message: "Namespaces must have resource quotas"
      pattern:
        metadata:
          labels:
            quota: "*"
```

#### `src/manifests/base/governance/policies/image-security/image-verification.yaml`
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signature
  annotations:
    policies.kyverno.io/title: Verify Container Images
spec:
  validationFailureAction: enforce
  background: true
  webhookTimeoutSeconds: 30
  rules:
  - name: verify-signature
    match:
      any:
      - resources:
          kinds:
          - Pod
    verifyImages:
    - image: "*"
      required: true
      verifyDigest: true
      mutateDigest: true
      attestors:
      - entries:
        - keys:
            publicKeys: |-
              -----BEGIN PUBLIC KEY-----
              MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE8sXRkQsWJVXvr7msW9pLQ7uQjOWd2
              QXiXM4JtX2H9f2y8m+91VqVNqKbKXXDqpS0L8m8+KBLlYx4y3m7Jn5pNQ==
              -----END PUBLIC KEY-----
```

#### `src/manifests/base/governance/policies/compliance/network-policy.yaml`
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: generate-network-policies
  annotations:
    policies.kyverno.io/title: Generate Network Policies
spec:
  validationFailureAction: audit
  background: true
  rules:
  - name: generate-deny-all-ingress
    match:
      any:
      - resources:
          kinds:
          - Namespace
    exclude:
      any:
      - resources:
          namespaces:
          - kube-system
          - kyverno
    generate:
      kind: NetworkPolicy
      name: default-deny-ingress
      namespace: "{{request.object.metadata.name}}"
      data:
        spec:
          podSelector: {}
          policyTypes:
          - Ingress
```

---

## 3.4 IAM Provider (Keycloak)

### Install Keycloak

#### `scripts/setup/install-keycloak.sh`
```bash
#!/bin/bash
set -e

# Add Bitnami helm repo
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Create Keycloak namespace
kubectl create namespace keycloak --dry-run=client -o yaml | kubectl apply -f -

# Install PostgreSQL for Keycloak
helm upgrade --install keycloak-db bitnami/postgresql \
  --namespace keycloak \
  --set auth.password=keycloak \
  --set primary.persistence.size=20Gi \
  --wait

# Install Keycloak
helm upgrade --install keycloak bitnami/keycloak \
  --namespace keycloak \
  --set auth.adminUser=admin \
  --set auth.adminPassword=$(openssl rand -base64 16) \
  --set database.host=keycloak-postgresql \
  --set postgresql.database=bitnami_keycloak \
  --set postgresql.username=bn_keycloak \
  --set postgresql.password=keycloak \
  --set service.type=LoadBalancer \
  --set ingress.enabled=true \
  --set ingress.hostname=keycloak.example.com \
  --set ingress.ingressClassName=kong \
  --wait

# Get admin password
echo "Keycloak admin password:"
kubectl get secret keycloak-admin -n keycloak -o jsonpath="{.data.password}" | base64 -d

echo "Keycloak installed!"
```

### Keycloak Configuration

#### `src/manifests/base/iam/keycloak/initial-config.yaml`
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: keycloak-initial-config
  namespace: keycloak
data:
  k8s-agent-realm.json: |
    {
      "realm": "k8s-agent",
      "enabled": true,
      "sslRequired": "external",
      "registrationAllowed": false,
      "loginWithEmailAllowed": true,
      "duplicateEmailsAllowed": false,
      "resetPasswordAllowed": true,
      "editUsernameAllowed": false,
      "bruteForceProtected": true,
      "clients": [
        {
          "clientId": "k8s-agent-api",
          "enabled": true,
          "clientAuthenticatorType": "client-secret",
          "secret": "${env.KC_CLIENT_SECRET}",
          "redirectUris": ["https://api.k8s-agent.example.com/*"],
          "webOrigins": ["https://api.k8s-agent.example.com"],
          "bearerOnly": false,
          "consentRequired": false,
          "standardFlowEnabled": true,
          "implicitFlowEnabled": false,
          "directAccessGrantsEnabled": true,
          "serviceAccountsEnabled": true,
          "publicClient": false,
          "protocol": "openid-connect",
          "attributes": {
            "access.token.lifespan": "3600"
          }
        }
      ],
      "roles": {
        "realm": [
          {
            "name": "admin",
            "description": "Administrator with full access"
          },
          {
            "name": "developer",
            "description": "Developer with deploy permissions"
          },
          {
            "name": "readonly",
            "description": "Read-only access"
          }
        ]
      }
    }
```

---

## 3.5 Security Adapters

#### `src/k8s_agent/security/vault_adapter.py`
```python
"""Vault adapter for secrets management."""
import hvac
from typing import Optional, Dict, Any


class VaultAdapter:
    """Adapter for Vault operations."""

    def __init__(self, url: str, token: str):
        self.client = hvac.Client(url=url, token=token)
        self.client.auth.token = token

    async def get_secret(self, path: str) -> Optional[Dict[str, Any]]:
        """Get secret from Vault."""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(path=path)
            return response['data']['data']
        except Exception as e:
            print(f"Error getting secret: {e}")
            return None

    async def create_secret(self, path: str, data: Dict[str, str]) -> bool:
        """Create secret in Vault."""
        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=data
            )
            return True
        except Exception as e:
            print(f"Error creating secret: {e}")
            return False

    async def create_policy(self, name: str, policy: str) -> bool:
        """Create Vault policy."""
        try:
            self.client.auth.token.create_or_update_policy(
                name=name,
                policy=policy
            )
            return True
        except Exception as e:
            print(f"Error creating policy: {e}")
            return False
```

#### `src/k8s_agent/security/external_secrets_adapter.py`
```python
"""External Secrets Operator adapter."""
from typing import Optional, Dict, Any
import httpx


class ExternalSecretsAdapter:
    """Adapter for External Secrets Operator."""

    def __init__(self, kubeconfig: str = None):
        self.kubeconfig = kubeconfig

    async def create_secret_store(self, name: str, config: Dict[str, Any]) -> bool:
        """Create SecretStore resource."""
        # Implementation using kubectl or kubernetes python client
        pass

    async def create_external_secret(
        self,
        name: str,
        namespace: str,
        store_name: str,
        secret_mappings: Dict[str, str]
    ) -> bool:
        """Create ExternalSecret resource."""
        # Implementation
        pass

    async def get_external_secret_status(self, name: str, namespace: str) -> Dict[str, Any]:
        """Get ExternalSecret status."""
        # Implementation
        pass
```

#### `src/k8s_agent/governance/kyverno_adapter.py`
```python
"""Kyverno adapter for policy management."""
from typing import List, Dict, Any
import httpx


class KyvernoAdapter:
    """Adapter for Kyverno policy operations."""

    async def list_policies(self) -> List[Dict[str, Any]]:
        """List all Kyverno policies."""
        # Implementation using kubectl
        pass

    async def create_policy(self, policy: Dict[str, Any]) -> bool:
        """Create a Kyverno policy."""
        # Implementation
        pass

    async def get_policy_report(self, namespace: str) -> Dict[str, Any]:
        """Get policy report for namespace."""
        # Implementation
        pass

    async def test_policy(self, policy: Dict[str, Any], resource: Dict[str, Any]) -> Dict[str, Any]:
        """Test policy against resource."""
        # Implementation
        pass
```

#### `src/k8s_agent/governance/policy_manager.py`
```python
"""Policy management business logic."""
from typing import List, Dict, Any
from .kyverno_adapter import KyvernoAdapter


class PolicyManager:
    """Business logic for policy management."""

    def __init__(self, kyverno_adapter: KyvernoAdapter):
        self.kyverno = kyverno_adapter

    async def enforce_best_practices(self) -> List[Dict[str, Any]]:
        """Apply security best practice policies."""
        policies = [
            # Pod security policies
            # Resource requirements
            # Network policies
        ]
        results = []
        for policy in policies:
            result = await self.kyverno.create_policy(policy)
            results.append({"policy": policy, "result": result})
        return results

    async def scan_cluster(self) -> Dict[str, Any]:
        """Scan cluster for policy violations."""
        # Implementation
        pass
```

---

## Verification Steps

After completing this phase:

1. [ ] Verify Vault
   ```bash
   kubectl get pods -n vault
   export VAULT_ADDR="https://vault.example.com"
   export VAULT_TOKEN=$(cat vault-root-token.txt)
   vault status
   ```

2. [ ] Verify External Secrets Operator
   ```bash
   kubectl get pods -n external-secrets
   kubectl get secretstore -A
   kubectl get externalsecret -A
   ```

3. [ ] Verify Kyverno
   ```bash
   kubectl get policies -n kyverno
   kubectl get cpol
   kubectl get policyreports -A
   ```

4. [ ] Verify Keycloak
   ```bash
   kubectl get pods -n keycloak
   curl -I https://keycloak.example.com
   ```

5. [ ] Test secret sync
   ```bash
   vault kv put secret/test username=admin password=secret
   kubectl apply -f manifests/base/external-secrets/examples/database-credentials.yaml
   kubectl get secret db-credentials -o yaml
   ```

---

## Next Phase

Proceed to **Phase 4: Observability Services** ([04-observability-services-plan.md](./04-observability-services-plan.md))
