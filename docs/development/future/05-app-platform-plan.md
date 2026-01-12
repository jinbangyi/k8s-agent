# Phase 5: Application Platform Setup

## Overview
Implement developer tools, service infrastructure, middleware, and databases. This phase provides the complete application platform for teams to build and deploy services.

---

## 5.1 Developer Tools Infrastructure

### Backstage (Developer Portal)

#### `scripts/devtools/setup-backstage.sh`
```bash
#!/bin/bash
set -e

# Create namespace
kubectl create namespace backstage --dry-run=client -o yaml | kubectl apply -f -

# Install PostgreSQL for Backstage
helm upgrade --install backstage-db bitnami/postgresql \
  --namespace backstage \
  --set auth.password=backstage \
  --set primary.persistence.size=20Gi \
  --wait

# Install Backstage
helm upgrade --install backstage backstage/backstage \
  --namespace backstage \
  --set postgresql.host=backstage-postgresql \
  --set postgresql.password=backstage \
  --set ingress.enabled=true \
  --set ingress.hostname=backstage.example.com \
  --set appConfig.baseUrl=https://backstage.example.com \
  --set integrations.github=[{host: github.example.com, token: ${GITHUB_TOKEN}}] \
  --set integrations.gitlab=[{host: gitlab.example.com, token: ${GITLAB_TOKEN}}] \
  --wait

echo "Backstage installed!"
echo "Developer Portal: https://backstage.example.com"
```

### Homer (Service Portal)

#### `scripts/devtools/setup-homer.sh`
```bash
#!/bin/bash
set -e

kubectl create namespace homer --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install homer bitnami/homer \
  --namespace homer \
  --set ingress.enabled=true \
  --set ingress.hostname=services.example.com \
  --set config.services[0].name=Grafana \
  --set config.services[0].url=https://grafana.example.com \
  --set config.services[1].name=ArgoCD \
  --set config.services[1].url=https://argocd.example.com \
  --set config.services[2].name=Backstage \
  --set config.services[2].url=https://backstage.example.com \
  --wait

echo "Homer installed!"
echo "Service Portal: https://services.example.com"
```

### n8n (Workflow Automation)

#### `scripts/devtools/setup-n8n.sh`
```bash
#!/bin/bash
set -e

kubectl create namespace n8n --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install n8n n8n/n8n \
  --namespace n8n \
  --set postgresql.enabled=true \
  --set postgresql.persistence.size=10Gi \
  --set ingress.enabled=true \
  --set ingress.hostname=n8n.example.com \
  --set env.N8N_BASIC_AUTH_ACTIVE=true \
  --set env.N8N_BASIC_AUTH_USER=admin \
  --set env.N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD} \
  --wait

echo "n8n installed!"
echo "Workflow Automation: https://n8n.example.com"
```

### Prefect (Workflow Orchestration)

#### `scripts/devtools/setup-prefect.sh`
```bash
#!/bin/bash
set -e

kubectl create namespace prefect --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install prefect prefect/prefect-orion \
  --namespace prefect \
  --set postgresql.enabled=true \
  --set postgresql.persistence.size=20Gi \
  --set ingress.enabled=true \
  --set ingress.hostname=prefect.example.com \
  --wait

echo "Prefect installed!"
echo "Workflow Orchestration: https://prefect.example.com"
```

### Langfuse (LLM Observability)

#### `scripts/devtools/setup-langfuse.sh`
```bash
#!/bin/bash
set -e

kubectl create namespace langfuse --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install langfuse langfuse/langfuse \
  --namespace langfuse \
  --set postgresql.enabled=true \
  --set redis.enabled=true \
  --set ingress.enabled=true \
  --set ingress.hostname=langfuse.example.com \
  --set password=${LANGFUSE_PASSWORD} \
  --set salt=${LANGFUSE_SALT} \
  --wait

echo "Langfuse installed!"
echo "LLM Observability: https://langfuse.example.com"
```

### Coder (Remote IDE)

#### `scripts/development/setup-coder.sh`
```bash
#!/bin/bash
set -e

# Add Coder helm repo
helm repo add coder-v2 https://coder.com/coder-v2
helm repo update

# Create Coder namespace
kubectl create namespace coder --dry-run=client -o yaml | kubectl apply -f -

# Install PostgreSQL for Coder
helm upgrade --install coder-db bitnami/postgresql \
  --namespace coder \
  --set auth.password=coder \
  --set primary.persistence.size=50Gi \
  --wait

# Install Coder
helm upgrade --install coder coder-v2/coder \
  --namespace coder \
  --set coder.postgres.host=coder-postgresql.coder.svc.cluster.local \
  --set coder.postgres.password=coder \
  --set coder.devURL=https://coder.example.com \
  --set ingress.enabled=true \
  --set ingress.hostname=coder.example.com \
  --set persistence.storageClass=huaweicloud-ssd \
  --set persistence.size=20Gi \
  --wait

echo "Coder installed!"
echo "Remote IDE: https://coder.example.com"
```

---

## 5.2 Service Infrastructure

### Kusion (Configuration Management)

#### `scripts/service-infra/setup-kusion.sh`
```bash
#!/bin/bash
set -e

kubectl create namespace kusionup --dry-run=client -o yaml | kubectl apply -f -

# Install Kusion
kubectl apply -f manifests/base/service-infra/kusion/

echo "Kusion installed!"
```

### Apollo (Configuration Center)

#### `scripts/service-infra/setup-apollo.sh`
```bash
#!/bin/bash
set -e

kubectl create namespace apollo --dry-run=client -o yaml | kubectl apply -f -

# Install Apollo Portal
helm upgrade --install apollo-portal bitnami/apollo \
  --namespace apollo \
  --set postgresql.enabled=true \
  --set ingress.enabled=true \
  --set ingress.hostname=apollo.example.com \
  --wait

# Install Apollo Config Service
helm upgrade --install apollo-config bitnami/apollo \
  --namespace apollo \
  --set service.config.enabled=true \
  --set service.admin.enabled=true \
  --wait

echo "Apollo installed!"
echo "Configuration Center: https://apollo.example.com"
```

### LiteLLM (Local LLM)

#### `scripts/service-infra/setup-litellm.sh`
```bash
#!/bin/bash
set -e

kubectl create namespace litellm --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install litellm litellm/litellm \
  --namespace litellm \
  --set litellm.enabled=true \
  --set ingress.enabled=true \
  --set ingress.hostname=litellm.example.com \
  --set masterKey=${LITELLM_MASTER_KEY} \
  --set saltKey=${LITELLM_SALT_KEY} \
  --set storage.size=10Gi \
  --wait

echo "LiteLLM installed!"
echo "Local LLM Gateway: https://litellm.example.com"
```

### Athens (Go Module Proxy)

#### `scripts/service-infra/setup-athens.sh`
```bash
#!/bin/bash
set -e

kubectl create namespace athens --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install athens gomods/athens \
  --namespace athens \
  --set persistence.enabled=true \
  --set persistence.size=50Gi \
  --set ingress.enabled=true \
  --set ingress.hostname=athens.example.com \
  --wait

echo "Athens installed!"
echo "Go Module Proxy: https://athens.example.com"
```

### pypiserver (Python Package Index)

#### `scripts/service-infra/setup-pypiserver.sh`
```bash
#!/bin/bash
set -e

kubectl create namespace pypiserver --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install pypiserver pypiserver/pypiserver \
  --namespace pypiserver \
  --set persistence.enabled=true \
  --set persistence.size=100Gi \
  --set ingress.enabled=true \
  --set ingress.hostname=pypi.example.com \
  --wait

echo "pypiserver installed!"
echo "Python Package Index: https://pypi.example.com"
```

### Verdaccio (NPM Package Proxy)

#### `scripts/service-infra/setup-verdaccio.sh`
```bash
#!/bin/bash
set -e

kubectl create namespace verdaccio --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install verdaccio verdaccio/verdaccio \
  --namespace verdaccio \
  --set persistence.enabled=true \
  --set persistence.size=50Gi \
  --set ingress.enabled=true \
  --set ingress.hostname=npm.example.com \
  --wait

echo "Verdaccio installed!"
echo "NPM Package Proxy: https://npm.example.com"
```

---

## 5.3 Middlewares & Databases

### Kafka (Strimzi Operator)

#### `scripts/middleware/setup-kafka.sh`
```bash
#!/bin/bash
set -e

# Install Strimzi operator
kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f \
  https://strimzi.io/install/latest?namespace=kafka

# Wait for operator to be ready
kubectl wait --for=condition=available deployment/strimzi-cluster-operator -n kafka --timeout=300s

# Create Kafka cluster
kubectl apply -f manifests/base/middleware/kafka/kafka-cluster.yaml

# Install Kafka UI
helm upgrade --install kafka-ui provectuslabs/kafka-ui \
  --namespace kafka \
  --set ingress.enabled=true \
  --set ingress.hostname=kafka-ui.example.com \
  --set yaml.kafka.clusters[0].name=k8s \
  --set yaml.kafka.clusters[0].bootstrapServers=kafka.kafka.svc.cluster.local:9092 \
  --wait

echo "Kafka installed!"
echo "Kafka UI: https://kafka-ui.example.com"
```

#### `src/manifests/base/middleware/kafka/kafka-cluster.yaml`
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: kafka
  namespace: kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 3
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      default.replication.factor: 3
      min.insync.replicas: 2
      inter.broker.protocol.version: "3.6"
    storage:
      type: jbod
      volumes:
      - id: 0
        type: persistent-claim
        size: 100Gi
        storageClassName: huaweicloud-ssd
    metricsConfig:
      type: jmxPrometheusExporter
      valueFrom:
        configMapKeyRef:
          name: kafka-metrics
          key: jmxPrometheusExporter.yml

  zookeeper:
    replicas: 3
    storage:
      type: persistent-claim
      size: 10Gi
      storageClassName: huaweicloud-ssd
    metricsConfig:
      type: jmxPrometheusExporter
      valueFrom:
        configMapKeyRef:
          name: kafka-metrics
          key: jmxPrometheusExporter.yml

  entityOperator:
    topicOperator:
      enabled: true
    userOperator:
      enabled: true
```

### Redis (Redis Operator)

#### `scripts/middleware/setup-redis.sh`
```bash
#!/bin/bash
set -e

# Install Redis operator
kubectl apply -f https://raw.githubusercontent.com/Otter-keeper/otter-redis/main/install/release.yaml

# Wait for operator
kubectl wait --for=condition=available deployment/otter-redis-operator -n redis-system --timeout=300s

# Create Redis cluster
kubectl apply -f manifests/base/middleware/redis/redis-cluster.yaml

# Install RedisInsight
helm upgrade --install redisinsight redis/redisinsight \
  --namespace redis \
  --set service.type=LoadBalancer \
  --set ingress.enabled=true \
  --set ingress.hostname=redisinsight.example.com \
  --wait

echo "Redis installed!"
echo "RedisInsight: https://redisinsight.example.com"
```

#### `src/manifests/base/middleware/redis/redis-cluster.yaml`
```yaml
apiVersion: redis.redis.opstreelabs.in/v1beta1
kind: RedisCluster
metadata:
  name: redis-cluster
  namespace: redis
spec:
  nodes: 3
  replication: true
  storage:
    type: persistent-claim
    size: 20Gi
    storageClassName: huaweicloud-ssd
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 2000m
      memory: 4Gi
  metrics:
    enabled: true
```

### PostgreSQL (Postgres Operator)

#### `scripts/middleware/setup-postgres.sh`
```bash
#!/bin/bash
set -e

# Install CloudNativePG operator
kubectl apply -f https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/main/releases/cnpg-1.23.yaml

# Wait for operator
kubectl wait --for=condition=available deployment/cnpg-controller-manager -n cnpg-system --timeout=300s

# Create PostgreSQL cluster
kubectl apply -f manifests/base/middleware/postgres/postgres-cluster.yaml

echo "PostgreSQL installed!"
```

#### `src/manifests/base/middleware/postgres/postgres-cluster.yaml`
```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: postgres-cluster
  namespace: postgres
spec:
  instances: 3
  primaryUpdateStrategy: unsupervised

  postgresql:
    parameters:
      max_connections: "200"
      shared_buffers: "256MB"
      effective_cache_size: "1GB"
      maintenance_work_mem: "64MB"
      checkpoint_completion_target: "0.9"
      wal_buffers: "16MB"
      default_statistics_target: "100"
      random_page_cost: "1.1"
      effective_io_concurrency: "200"
      work_mem: "2621kB"
      min_wal_size: "1GB"
      max_wal_size: "4GB"

  bootstrap:
    initdb:
      database: appdb
      owner: appuser
      secret:
        name: postgres-credentials

  storage:
    size: 100Gi
    storageClass: huaweicloud-ssd

  monitoring:
    enabled: true

  backup:
    barmanObjectStore:
      destinationPath: s3://postgres-backup
      endpointURL: https://obs.cn-north-4.myhuaweicloud.com
      s3Credentials:
        accessKeyId:
          name: backup-creds
          key: accessKeyId
        secretAccessKey:
          name: backup-creds
          key: secretAccessKey
      wal:
        retention: 7d
      data:
        retention: 30d
```

### MongoDB (MongoDB Operator)

#### `scripts/middleware/setup-mongodb.sh`
```bash
#!/bin/bash
set -e

# Install MongoDB operator
kubectl apply -f https://raw.githubusercontent.com/mongodb/mongodb-enterprise-kubernetes/main/crds.yaml
kubectl apply -f https://raw.githubusercontent.com/mongodb/mongodb-enterprise-kubernetes/main/operator.yaml

# Wait for operator
kubectl wait --for=condition=available deployment/mongodb-enterprise-operator -n mongodb --timeout=300s

# Create MongoDB cluster
kubectl apply -f manifests/base/middleware/mongodb/mongodb-cluster.yaml

# Install Compass-web
helm upgrade --install compass mongodb/compass-web \
  --namespace mongodb \
  --set ingress.enabled=true \
  --set ingress.hostname=mongodb-ui.example.com \
  --wait

echo "MongoDB installed!"
echo "Compass UI: https://mongodb-ui.example.com"
```

### Elasticsearch + Kibana

#### `scripts/middleware/setup-elasticsearch.sh`
```bash
#!/bin/bash
set -e

# Install Elastic operator
kubectl apply -f https://download.elastic.co/downloads/eck-chart/latest/eck-operator-crds.yaml
kubectl apply -f https://download.elastic.co/downloads/eck-chart/latest/eck-operator.yaml

# Wait for operator
kubectl wait --for=condition=available deployment/elastic-operator -n elastic-system --timeout=300s

# Create Elasticsearch cluster
kubectl apply -f manifests/base/middleware/elasticsearch/elasticsearch-cluster.yaml

# Create Kibana
kubectl apply -f manifests/base/middleware/elasticsearch/kibana.yaml

echo "Elasticsearch + Kibana installed!"
```

### Superset (Data Visualization)

#### `scripts/middleware/setup-superset.sh`
```bash
#!/bin/bash
set -e

kubectl create namespace superset --dry-run=client -o yaml | kubectl apply -f -

# Install Redis for Superset
helm upgrade --install superset-redis bitnami/redis \
  --namespace superset \
  --set auth.enabled=false \
  --set master.persistence.size=5Gi \
  --wait

# Install PostgreSQL for Superset
helm upgrade --install superset-db bitnami/postgresql \
  --namespace superset \
  --set auth.password=superset \
  --set primary.persistence.size=20Gi \
  --wait

# Install Superset
helm upgrade --install superset apache/superset \
  --namespace superset \
  --set redis.host=superset-redis-master \
  --set postgresql.host=superset-postgresql \
  --set postgresql.password=superset \
  --set ingress.enabled=true \
  --set ingress.hostname=superset.example.com \
  --set secretKey=$(openssl rand -hex 32) \
  --wait

echo "Superset installed!"
echo "Data Visualization: https://superset.example.com"
```

### Bytebase (Database DevSecOps)

#### `scripts/middleware/setup-bytebase.sh`
```bash
#!/bin/bash
set -e

kubectl create namespace bytebase --dry-run=client -o yaml | kubectl apply -f -

# Install Bytebase
helm upgrade --install bytebase bytebase/bytebase \
  --namespace bytebase \
  --set postgresql.enabled=true \
  --set ingress.enabled=true \
  --set ingress.hostname=bytebase.example.com \
  --wait

echo "Bytebase installed!"
echo "Database DevSecOps: https://bytebase.example.com"
```

---

## 5.4 Service Infrastructure Adapters

#### `src/k8s_agent/adapters/kafka_adapter.py`
```python
"""Kafka operations adapter via Strimzi."""
from typing import Dict, Any, List
import httpx


class KafkaAdapter:
    """Adapter for Kafka operations via Strimzi."""

    def __init__(self, kubeconfig: str = None):
        self.kubeconfig = kubeconfig

    async def create_topic(
        self,
        name: str,
        partitions: int,
        replication_factor: int,
        config: Dict[str, Any] = None
    ) -> bool:
        """Create Kafka topic."""
        # Implementation using Kubernetes API
        pass

    async def list_topics(self, namespace: str = None) -> List[Dict[str, Any]]:
        """List Kafka topics."""
        # Implementation
        pass

    async def get_consumer_groups(self) -> List[Dict[str, Any]]:
        """Get consumer group information."""
        # Implementation
        pass

    async def produce_message(self, topic: str, message: Any) -> bool:
        """Produce message to topic."""
        # Implementation
        pass
```

#### `src/k8s_agent/adapters/redis_adapter.py`
```python
"""Redis operations adapter."""
import redis.asyncio as redis
from typing import Any, Dict, List, Optional


class RedisAdapter:
    """Adapter for Redis operations."""

    def __init__(self, host: str, port: int = 6379, password: str = None, db: int = 0):
        self.client = redis.Redis(
            host=host,
            port=port,
            password=password,
            db=db,
            decode_responses=True
        )

    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        return await self.client.get(key)

    async def set(self, key: str, value: str, ttl: int = None) -> bool:
        """Set value in Redis."""
        if ttl:
            return await self.client.setex(key, ttl, value)
        return await self.client.set(key, value)

    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        return await self.client.delete(key) > 0

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return await self.client.exists(key) > 0

    async def get_info(self) -> Dict[str, Any]:
        """Get Redis server info."""
        return await self.client.info()
```

#### `src/k8s_agent/adapters/postgres_adapter.py`
```python
"""PostgreSQL operations adapter."""
import asyncpg
from typing import List, Dict, Any, Optional


class PostgresAdapter:
    """Adapter for PostgreSQL operations."""

    def __init__(self, dsn: str):
        self.dsn = dsn

    async def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute SQL query."""
        async with asyncpg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                results = await conn.fetch(query, *params) if params else await conn.fetch(query)
                return [dict(row) for row in results]

    async def create_database(self, db_name: str) -> bool:
        """Create database."""
        async with asyncpg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                await conn.execute(f'CREATE DATABASE "{db_name}"')
                return True

    async def create_user(self, username: str, password: str) -> bool:
        """Create user."""
        async with asyncpg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                await conn.execute(f"CREATE USER {username} WITH PASSWORD '{password}'")
                return True

    async def grant_privileges(
        self,
        database: str,
        username: str,
        privileges: List[str]
    ) -> bool:
        """Grant privileges to user."""
        priv_string = ", ".join(privileges)
        async with asyncpg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                await conn.execute(f"GRANT {priv_string} ON DATABASE {database} TO {username}")
                return True
```

#### `src/k8s_agent/adapters/mongodb_adapter.py`
```python
"""MongoDB operations adapter."""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, Any, List, Optional


class MongoDBAdapter:
    """Adapter for MongoDB operations."""

    def __init__(self, connection_string: str, database: str):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client[database]

    async def find(
        self,
        collection: str,
        filter: Dict[str, Any] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Find documents."""
        cursor = self.db[collection].find(filter or {}).limit(limit)
        return await cursor.to_list(length=limit)

    async def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        """Insert document."""
        result = await self.db[collection].insert_one(document)
        return str(result.inserted_id)

    async def update_one(
        self,
        collection: str,
        filter: Dict[str, Any],
        update: Dict[str, Any]
    ) -> bool:
        """Update document."""
        result = await self.db[collection].update_one(filter, {"$set": update})
        return result.modified_count > 0

    async def delete_one(self, collection: str, filter: Dict[str, Any]) -> bool:
        """Delete document."""
        result = await self.db[collection].delete_one(filter)
        return result.deleted_count > 0

    async def aggregate(
        self,
        collection: str,
        pipeline: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Run aggregation pipeline."""
        cursor = self.db[collection].aggregate(pipeline)
        return await cursor.to_list(length=None)
```

#### `src/k8s_agent/adapters/elasticsearch_adapter.py`
```python
"""Elasticsearch operations adapter."""
from elasticsearch import AsyncElasticsearch
from typing import Dict, Any, List, Optional


class ElasticsearchAdapter:
    """Adapter for Elasticsearch operations."""

    def __init__(self, hosts: List[str], verify_certs: bool = True):
        self.client = AsyncElasticsearch(hosts=hosts, verify_certs=verify_certs)

    async def create_index(self, index: str, mapping: Dict[str, Any] = None) -> bool:
        """Create index with optional mapping."""
        if mapping:
            await self.client.indices.create(index=index, body=mapping)
        else:
            await self.client.indices.create(index=index)
        return True

    async def index_document(
        self,
        index: str,
        doc_id: str,
        document: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Index document."""
        return await self.client.index(index=index, id=doc_id, document=document)

    async def search(
        self,
        index: str,
        query: Dict[str, Any],
        size: int = 10
    ) -> List[Dict[str, Any]]:
        """Search documents."""
        response = await self.client.search(index=index, body=query, size=size)
        return [hit["_source"] for hit in response["hits"]["hits"]]

    async def delete_index(self, index: str) -> bool:
        """Delete index."""
        await self.client.indices.delete(index=index)
        return True

    async def get_cluster_health(self) -> Dict[str, Any]:
        """Get cluster health."""
        return await self.client.cluster.health()
```

---

## 5.5 FastAPI Application

### Core API Routes

#### `src/k8s_agent/api/main.py`
```python
"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import health, clusters, deployments, secrets, observability
from .middleware import AuthMiddleware, LoggingMiddleware

app = FastAPI(
    title="k8s-agent API",
    description="Kubernetes lifecycle management platform",
    version="0.1.0"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)
app.add_middleware(LoggingMiddleware)

# Routes
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(clusters.router, prefix="/api/clusters", tags=["clusters"])
app.include_router(deployments.router, prefix="/api/deployments", tags=["deployments"])
app.include_router(secrets.router, prefix="/api/secrets", tags=["secrets"])
app.include_router(observability.router, prefix="/api/observability", tags=["observability"])
```

#### `src/k8s_agent/api/routes/clusters.py`
```python
"""Cluster management routes."""
from fastapi import APIRouter, HTTPException
from typing import List
from ...core.cluster_manager import ClusterManager
from ...core.models import Cluster

router = APIRouter()
cluster_manager = ClusterManager(...)  # Initialize with adapters

@router.get("/", response_model=List[Cluster])
async def list_clusters():
    """List all clusters."""
    return await cluster_manager.list_clusters()

@router.post("/", response_model=Cluster)
async def create_cluster(cluster: Cluster):
    """Create a new cluster."""
    return await cluster_manager.create_cluster(
        name=cluster.name,
        node_count=cluster.node_count,
        region=cluster.region
    )

@router.get("/{cluster_id}", response_model=Cluster)
async def get_cluster(cluster_id: str):
    """Get cluster by ID."""
    cluster = await cluster_manager.get_cluster(cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster

@router.post("/{cluster_id}/scale")
async def scale_cluster(cluster_id: str, node_count: int):
    """Scale cluster."""
    return await cluster_manager.scale_cluster(cluster_id, node_count)
```

---

## Verification Steps

After completing this phase:

1. [ ] Verify developer tools
   ```bash
   curl -I https://backstage.example.com
   curl -I https://services.example.com
   curl -I https://n8n.example.com
   ```

2. [ ] Verify service infrastructure
   ```bash
   curl -I https://apollo.example.com
   curl -I https://litellm.example.com
   curl -I https://pypi.example.com
   ```

3. [ ] Verify middleware
   ```bash
   kubectl get kafka -n kafka
   kubectl get redis -n redis
   kubectl get postgresql -n postgres
   ```

4. [ ] Test API
   ```bash
   curl https://api.k8s-agent.example.com/api/health
   curl https://api.k8s-agent.example.com/api/clusters
   ```

5. [ ] Test external resources (Crossplane)
   ```bash
   kubectl get managed
   kubectl get composite
   ```

---

## Summary

All 5 phases are now complete:
1. ✅ Cloud Infrastructure (Huawei Cloud ECS, networking, storage)
2. ✅ K8s Platform (k3s, ArgoCD, Kong, Linkerd)
3. ✅ Security & Governance (Vault, External Secrets, Kyverno, IAM)
4. ✅ Observability (Prometheus, Loki, OpenCost, Signoz, Posthog, Sentry)
5. ✅ Application Platform (Developer tools, middleware, databases)

The platform is now ready for teams to deploy and manage their applications!
