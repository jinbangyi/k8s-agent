# Phase 2: K8s Platform Setup

## Overview
Initialize the Kubernetes platform with k3s, ArgoCD for GitOps, Kong API Gateway, and Linkerd service mesh.

---

## 2.1 k3s Cluster Installation

### Prerequisites
- ECS instances from Phase 1 are running
- SSH access to all nodes
- Minimum 3 master nodes (HA)

### Master Node Setup

#### `scripts/setup/install-k3s-master.sh`
```bash
#!/bin/bash
set -e

MASTER_IP="$1"
MASTER_COUNT="$2"
API_PORT="6443"

# Install k3s on first master
if [ "$1" == "$2" ]; then
  curl -sfL https://get.k3s.io | sh \
    -s server \
    --tls-san ${MASTER_IP} \
    --disable traefik \
    --disable servicelb \
    --write-kubeconfig-mode 644 \
    --node-name k3s-master-0

  # Get join token
  TOKEN=$(cat /var/lib/rancher/k3s/server/node-token)
  echo "Token: $TOKEN"
  echo "Save this token for other master nodes"
else
  # Join additional masters
  curl -sfL https://get.k3s.io | sh \
    -s server \
    --tls-san ${MASTER_IP} \
    --server https://${FIRST_MASTER_IP}:6443 \
    --token ${TOKEN} \
    --disable traefik \
    --disable servicelb \
    --node-name k3s-master-$1
fi

# Wait for k3s to be ready
until kubectl get nodes &>/dev/null; do
  echo "Waiting for k3s to start..."
  sleep 5
done

echo "k3s master node ready!"
```

### Worker Node Setup

#### `scripts/setup/install-k3s-worker.sh`
```bash
#!/bin/bash
set -e

MASTER_URL="$1"
TOKEN="$2"
NODE_NAME="$3"

curl -sfL https://get.k3s.io | sh \
  -s agent \
  --server ${MASTER_URL} \
  --token ${TOKEN} \
  --node-name ${NODE_NAME}

echo "k3s worker node ready!"
```

### Cluster Verification

#### `scripts/cluster/verify-cluster.sh`
```bash
#!/bin/bash

# Check nodes
kubectl get nodes -o wide

# Check cluster info
kubectl cluster-info

# Check all pods
kubectl get pods --all-namespaces

# Run connectivity test
kubectl run test-pod --image=busybox --rm -it --restart=Never -- nslookup kubernetes.default
```

---

## 2.2 Crossplane Installation

### Install Crossplane for External Resource Management

#### `scripts/setup/install-crossplane.sh`
```bash
#!/bin/bash
set -e

# Install Crossplane
helm repo add crossplane-stable https://charts.crossplane.io/stable
helm repo update

helm upgrade --install crossplane crossplane-stable/crossplane \
  --namespace crossplane-system \
  --create-namespace \
  --wait

# Wait for Crossplane to be ready
kubectl wait --for=condition=available deployment/crossplane -n crossplane-system --timeout=300s

echo "Crossplane installed successfully!"

# Install Huawei Cloud provider if available
if [ -n "$HUAWEI_CLOUD_PROVIDER" ]; then
  kubectl apply -f infrastructure/crossplane/providers/provider-huawei.yaml
  kubectl wait --for=condition=healthy provider.pkg.crossplane.io/huawei-cloud --timeout=300s
  echo "Huawei Cloud provider installed!"
fi

# Install AWS provider for cross-cloud resources
kubectl apply -f infrastructure/crossplane/providers/provider-aws.yaml
kubectl wait --for=condition=healthy provider.pkg.crossplane.io/provider-aws --timeout=300s

# Install sample compositions
kubectl apply -f infrastructure/crossplane/compositions/
echo "Crossplane compositions installed!"
```

#### `infrastructure/crossplane/providers/provider-aws.yaml`
```yaml
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws
spec:
  package: crossplanecontrib/provider-aws:v0.40.0
  controllerConfigRef:
    name: provider-aws-config
```

#### `infrastructure/crossplane/compositions/composite-database.yaml`
```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: composite_databases.example.org
spec:
  group: example.org
  names:
    kind: CompositeDatabase
    plural: compositedatabases
  versions:
  - name: v1alpha1
    served: true
    referenceable: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              engine:
                type: string
              version:
                type: string
              size:
                type: string
              storageGB:
                type: integer

---
apiVersion: example.org/v1alpha1
kind: CompositeDatabase
metadata:
  name: example-rds
spec:
  engine: postgres
  version: "15"
  size: db.t3.micro
  storageGB: 100
```

---

## 2.3 ArgoCD Installation

### Install ArgoCD for GitOps

#### `scripts/setup/install-argocd.sh`
```bash
#!/bin/bash
set -e

# Create namespace
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for ArgoCD to be ready
kubectl wait --for=condition=available deployment/argocd-server -n argocd --timeout=300s

# Create admin password
argocd admin initial-password -n argocd > argocd-initial-password.txt

# Expose ArgoCD via ingress
kubectl apply -f manifests/base/argocd/ingress.yaml

echo "ArgoCD installed successfully!"
echo "Initial admin password saved to argocd-initial-password.txt"
```

#### `src/manifests/base/argocd/ingress.yaml`
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: argocd-server-ingress
  namespace: argocd
  annotations:
    konghq.com/protocol: https
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: kong
  rules:
  - host: argocd.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: argocd-server
            port:
              number: 80
  tls:
  - hosts:
    - argocd.example.com
    secretName: argocd-server-tls
```

### ArgoCD Application Sets

#### `src/manifests/base/argocd/appsets/platform-appset.yaml`
```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: platform
  namespace: argocd
spec:
  description: Platform infrastructure applications
  sourceRepos:
  - https://gitlab.example.com/k8s-agent/manifests.git
  destinations:
  - namespace: '*'
    server: https://kubernetes.default.svc
  clusterResourceWhitelist:
  - group: '*'
    kind: '*'

---
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: platform-apps
  namespace: argocd
spec:
  generators:
  - git:
      repoURL: https://gitlab.example.com/k8s-agent/manifests.git
      revision: HEAD
      directories:
      - path: manifests/base/*/apps/*
  template:
    metadata:
      name: '{{path.basename}}'
    spec:
      project: platform
      source:
        repoURL: https://gitlab.example.com/k8s-agent/manifests.git
        targetRevision: HEAD
        path: '{{path}}'
      destination:
        server: https://kubernetes.default.svc
        namespace: '{{path.basename}}'
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
        - CreateNamespace=true
```

---

## 2.4 Kong API Gateway

### Install Kong

#### `scripts/setup/install-kong.sh`
```bash
#!/bin/bash
set -e

# Add Kong helm repo
helm repo add kong https://charts.konghq.com
helm repo update

# Create Kong namespace
kubectl create namespace kong --dry-run=client -o yaml | kubectl apply -f -

# Install Kong
helm upgrade --install kong kong/kong \
  --namespace kong \
  --set ingressController.installCRDs=false \
  --set replicaCount=2 \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=5 \
  --set env.anonymous_reports=false \
  --set proxy.type=LoadBalancer \
  --wait

echo "Kong gateway installed successfully!"
```

---

## 2.5 Linkerd Service Mesh

### Install Linkerd

#### `scripts/setup/install-linkerd.sh`
```bash
#!/bin/bash
set -e

# Install linkerd2 CLI
curl -sL https://run.linkerd.io/install | sh

# Validate cluster
linkerd check --pre

# Install Linkerd
linkerd install | kubectl apply -f -

# Verify installation
linkerd check

# Install viz extension
linkerd viz install | kubectl apply -f -

echo "Linkerd service mesh installed!"
echo "Access dashboard: linkerd viz dashboard"
```

### Linkerd Service Profiles

#### `src/manifests/base/linkerd/k8s-agent-profile.yaml`
```yaml
apiVersion: linkerd.io/v1alpha2
kind: ServiceProfile
metadata:
  name: k8s-agent
  namespace: k8s-agent
spec:
  routes:
  - name: /api/health
    condition:
      method: GET
      pathRegex: /api/health
  - name: /api/clusters
    condition:
      method: GET
      pathRegex: /api/clusters/.*
  retryPolicy:
    maxRetries: 3
    perTryTimeout: 200ms
```

---

## 2.6 Core Python Package

### Base Application Structure

#### `src/k8s_agent/__init__.py`
```python
"""k8s-agent - Kubernetes lifecycle management platform."""

__version__ = "0.1.0"
```

#### `src/k8s_agent/core/interfaces.py`
```python
"""Abstract interfaces for adapters."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class ClusterAdapter(ABC):
    """Abstract interface for cluster operations."""

    @abstractmethod
    async def get_cluster(self, cluster_id: str) -> Dict[str, Any]:
        """Get cluster information."""
        pass

    @abstractmethod
    async def list_clusters(self) -> List[Dict[str, Any]]:
        """List all clusters."""
        pass


class SecretsAdapter(ABC):
    """Abstract interface for secrets operations."""

    @abstractmethod
    async def get_secret(self, name: str, namespace: str) -> Optional[str]:
        """Get secret value."""
        pass

    @abstractmethod
    async def create_secret(self, name: str, namespace: str, value: str) -> bool:
        """Create a secret."""
        pass


class ObservabilityAdapter(ABC):
    """Abstract interface for observability data."""

    @abstractmethod
    async def get_metrics(self, query: str) -> Dict[str, Any]:
        """Query metrics."""
        pass
```

#### `src/k8s_agent/core/models.py`
```python
"""Domain models."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class Cluster(BaseModel):
    """Kubernetes cluster model."""

    id: str = Field(..., description="Cluster ID")
    name: str = Field(..., description="Cluster name")
    version: str = Field(default="1.32", description="Kubernetes version")
    status: str = Field(default="provisioning", description="Cluster status")
    node_count: int = Field(default=0, description="Number of nodes")
    region: str = Field(..., description="Cloud region")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SecretReference(BaseModel):
    """Secret reference model."""

    name: str
    namespace: str
    source: str = Field(..., description="Secret source: vault, aws, azure, etc.")


class DeploymentConfig(BaseModel):
    """Deployment configuration model."""

    name: str
    namespace: str
    image: str
    replicas: int = 1
    secrets: List[SecretReference] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)
```

#### `src/k8s_agent/core/cluster_manager.py`
```python
"""Cluster lifecycle business logic."""
from typing import List, Optional
from .models import Cluster
from .interfaces import ClusterAdapter


class ClusterManager:
    """Business logic for cluster lifecycle management."""

    def __init__(self, adapter: ClusterAdapter):
        self.adapter = adapter

    async def create_cluster(
        self,
        name: str,
        node_count: int,
        region: str,
        version: str = "1.32"
    ) -> Cluster:
        """Create a new cluster."""
        # Business logic for cluster creation
        cluster = Cluster(
            id=f"{name}-{region}",
            name=name,
            version=version,
            node_count=node_count,
            region=region,
            status="provisioning"
        )
        return cluster

    async def get_cluster_status(self, cluster_id: str) -> dict:
        """Get cluster status."""
        return await self.adapter.get_cluster(cluster_id)

    async def scale_cluster(self, cluster_id: str, node_count: int) -> bool:
        """Scale cluster to specified node count."""
        # Implementation
        return True
```

---

## 2.7 Adapters for K8s Operations

#### `src/k8s_agent/adapters/kubectl_adapter.py`
```python
"""Kubectl operations adapter."""
from typing import Dict, Any
import subprocess
import json


class KubectlAdapter:
    """Adapter for kubectl operations."""

    def __init__(self, kubeconfig: str = None):
        self.kubeconfig = kubeconfig

    async def get_nodes(self) -> list:
        """Get all cluster nodes."""
        cmd = ["kubectl", "get", "nodes", "-o", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout).get("items", [])

    async def get_pods(self, namespace: str = None) -> list:
        """Get pods in namespace."""
        cmd = ["kubectl", "get", "pods", "-o", "json"]
        if namespace:
            cmd.extend(["-n", namespace])
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout).get("items", [])

    async def apply_manifest(self, manifest_path: str) -> bool:
        """Apply a Kubernetes manifest."""
        cmd = ["kubectl", "apply", "-f", manifest_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
```

---

## Verification Steps

After completing this phase:

1. [ ] Verify k3s cluster
   ```bash
   kubectl get nodes
   kubectl get pods --all-namespaces
   ```

2. [ ] Verify Crossplane
   ```bash
   kubectl get providers
   kubectl get compositions
   ```

3. [ ] Verify ArgoCD
   ```bash
   kubectl get pods -n argocd
   argocd app list
   ```

4. [ ] Verify Kong
   ```bash
   kubectl get pods -n kong
   curl -I https://kong.example.com
   ```

5. [ ] Verify Linkerd
   ```bash
   linkerd check
   linkerd viz -n k8s-agent top
   ```

---

## Next Phase

Proceed to **Phase 3: Security & Governance** ([03-security-governance-plan.md](./03-security-governance-plan.md))
