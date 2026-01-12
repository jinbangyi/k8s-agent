# Phase 4: Observability Services Setup

## Overview
Implement comprehensive observability stack including Prometheus/Grafana for monitoring, Loki for logging, OpenCost for cost management, and Signoz/Posthog/Sentry for application observability.

---

## 4.1 Prometheus + Grafana

### Install Prometheus Operator

#### `scripts/setup/install-prometheus.sh`
```bash
#!/bin/bash
set -e

# Add prometheus-community helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Create monitoring namespace
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Install Prometheus Operator
helm upgrade --install kube-prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set prometheus.prometheusSpec.retention=15d \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.storageClassName=huaweicloud-ssd \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi \
  --set grafana.persistence.enabled=true \
  --set grafana.persistence.storageClassName=huaweicloud-ssd \
  --set grafana.persistence.size=10Gi \
  --set grafana.adminPassword=admin \
  --set grafana.ingress.enabled=true \
  --set grafana.ingress.ingressClassName=kong \
  --set grafana.ingress.hosts=grafana.example.com \
  --set defaultRules.enabled=true \
  --set kubeControllerManager.enabled=true \
  --set kubeScheduler.enabled=true \
  --set kubeDns.enabled=true \
  --wait

echo "Prometheus + Grafana installed!"
echo "Grafana: https://grafana.example.com (admin/admin)"
```

### Prometheus Configuration

#### `src/manifests/base/monitoring/prometheus/recording-rules.yaml`
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: k8s-aggregated-recording-rules
  namespace: monitoring
spec:
  groups:
  - name: cluster.rules
    interval: 30s
    rules:
    - record: cluster:cpu_usage:rate5m
      expr: sum(rate(container_cpu_usage_seconds_total{container!=""}[5m])) by (cluster)

    - record: cluster:memory_usage:rate5m
      expr: sum(container_memory_working_set_bytes{container!=""}) by (cluster)

    - record: namespace:cpu_usage:rate5m
      expr: sum(rate(container_cpu_usage_seconds_total{container!=""}[5m])) by (namespace)

    - record: namespace:memory_usage:rate5m
      expr: sum(container_memory_working_set_bytes{container!=""}) by (namespace)

    - record: cluster:pods_ready:ratio
      expr: sum(kube_pod_status_phase{phase="Running"}) / sum(kube_pod_status_phase)
```

#### `src/manifests/base/monitoring/prometheus/alerting-rules.yaml`
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: k8s-alerting-rules
  namespace: monitoring
spec:
  groups:
  - name: cluster_alerts
    interval: 30s
    rules:
    - alert: ClusterNodeDown
      expr: up{job="node-exporter"} == 0
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "Node {{ $labels.instance }} is down"
        description: "Node has been down for more than 5 minutes"

    - alert: PodCrashLooping
      expr: rate(kube_pod_container_status_restarts_total{namespace!="kube-system"}[15m]) > 0
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Pod {{ $labels.pod }} is crash looping"
        description: "Pod has been restarting frequently"

    - alert: HighMemoryUsage
      expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
      for: 10m
      labels:
        severity: warning
      annotations:
        summary: "High memory usage on {{ $labels.pod }}"
        description: "Memory usage is above 90%"

    - alert: OOMKilled
      expr: increase(kube_pod_container_status_terminated_reason{reason="OOMKilled"}[1h]) > 0
      labels:
        severity: critical
      annotations:
        summary: "Pod {{ $labels.pod }} was OOM killed"
        description: "Container was killed due to out of memory"
```

---

## 4.2 Loki + Promtail (Logging)

### Install Loki

#### `scripts/setup/install-loki.sh`
```bash
#!/bin/bash
set -e

# Add grafana helm repo
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Loki
helm upgrade --install loki grafana/loki-stack \
  --namespace monitoring \
  --set loki.persistence.enabled=true \
  --set loki.persistence.storageClassName=huaweicloud-ssd \
  --set loki.persistence.size=20Gi \
  --set loki.retention.enabled=true \
  --set loki.retention.days=30 \
  --set promtail.enabled=true \
  --set grafana.enabled=false \
  --set prometheusRules.enabled=false \
  --wait

echo "Loki + Promtail installed!"
```

### Loki Configuration

#### `src/manifests/base/logging/loki/config.yaml`
```yaml
auth_enabled: false

server:
  http_listen_port: 3100

memberlist:
  join_members:
  - loki-gossip

common:
  path_prefix: /loki
  replication_factor: 3
  storage:
    s3:
      endpoint: obs.cn-north-4.myhuaweicloud.com
      bucket_name: loki-logs
      access_key_id: ${OBS_ACCESS_KEY}
      secret_access_key: ${OBS_SECRET_KEY}
      s3forcepathstyle: true
  ring:
    kvstore:
      store: memberlist

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h

chunk_store_config:
  max_look_back_period: 168h

schema_config:
  configs:
  - from: 2024-01-01
    store: boltdb-shipper
    object_store: s3
    schema: v11
    index:
      prefix: index_
      period: 24h

ruler:
  storage:
    s3:
      bucketnames: loki-ruler
  alertmanager_url: http://alertmanager.monitoring.svc.cluster.local:9093
```

---

## 4.3 OpenCost (Cost Management)

### Install OpenCost

#### `scripts/setup/install-opencost.sh`
```bash
#!/bin/bash
set -e

# Install OpenCost
helm upgrade --install opencost opencost/opencost \
  --namespace monitoring \
  --set opencost.prometheus.internal.enabled=true \
  --set opencost.prometheus.internal.serverAddress=http://kube-prometheus-prometheus.monitoring.svc.cluster.local:9090 \
  --set opencost.grafana.internal.enabled=true \
  --set opencost.grafana.internal.serverAddress=http://kube-prometheus-grafana.monitoring.svc.cluster.local:80 \
  --set opencost.grafana.internal.username=admin \
  --set opencost.grafana.internal.password=admin \
  --set opencost.grafana.internal.folderName="OpenCost" \
  --wait

echo "OpenCost installed!"
echo "Dashboard: http://opencost.monitoring.svc.cluster.local:9090"
```

### OpenCost Configuration

#### `src/manifests/base/cost/opencost/budgets.yaml`
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: opencost-cost-analyzer
  namespace: monitoring
data:
  opencost.json: |
    {
      "budgets": [
        {
          "name": "monthly-budget",
          "amount": 5000,
          "currency": "CNY",
          "window": "monthly",
          "alerts": [
            {
              "type": "email",
              "threshold": 0.8,
              "recipients": ["finance@example.com"]
            },
            {
              "type": "slack",
              "threshold": 0.9,
              "recipients": ["#alerts"]
            }
          ]
        }
      ]
    }
```

---

## 4.4 Signoz (APM)

### Install Signoz

#### `scripts/setup/install-signoz.sh`
```bash
#!/bin/bash
set -e

# Add Signoz helm repo
helm repo add signoz https://charts.signoz.io
helm repo update

# Create Signoz namespace
kubectl create namespace signoz --dry-run=client -o yaml | kubectl apply -f -

# Install Signoz
helm upgrade --install signoz signoz/signoz \
  --namespace signoz \
  --set signoz.clickhouse.persistence.enabled=true \
  --set signoz.clickhouse.persistence.storageClassName=huaweicloud-ssd \
  --set signoz.clickhouse.persistence.size=100Gi \
  --set signoz.keyValuePersistence.size=10Gi \
  --set signoz.queryService.persistence.enabled=true \
  --set signoz.queryService.persistence.size=20Gi \
  --set signoz.ingress.enabled=true \
  --set signoz.ingress.ingressClassName=kong \
  --set signoz.ingress.hosts=signoz.example.com \
  --wait

echo "Signoz installed!"
echo "APM Dashboard: https://signoz.example.com"
```

---

## 4.5 Posthog (Analytics)

### Install Posthog

#### `scripts/setup/install-posthog.sh`
```bash
#!/bin/bash
set -e

# Create Posthog namespace
kubectl create namespace posthog --dry-run=client -o yaml | kubectl apply -f -

# Install PostgreSQL for Posthog
helm upgrade --install posthog-db bitnami/postgresql \
  --namespace posthog \
  --set auth.password=posthog \
  --set primary.persistence.size=50Gi \
  --wait

# Install Redis for Posthog
helm upgrade --install posthog-redis bitnami/redis \
  --namespace posthog \
  --set auth.enabled=false \
  --set master.persistence.size=10Gi \
  --wait

# Install Posthog
helm upgrade --install posthog posthog/posthog \
  --namespace posthog \
  --set postgresql.host=posthog-postgresql \
  --set postgresql.password=posthog \
  --set redis.host=posthog-redis-master \
  --set ingress.enabled=true \
  --set ingress.hostname=posthog.example.com \
  --set secretKey=$(openssl rand -hex 32) \
  --wait

echo "Posthog installed!"
echo "Analytics Dashboard: https://posthog.example.com"
```

---

## 4.6 Sentry (Error Tracking)

### Install Sentry

#### `scripts/setup/install-sentry.sh`
```bash
#!/bin/bash
set -e

# Create Sentry namespace
kubectl create namespace sentry --dry-run=client -o yaml | kubectl apply -f -

# Install Clickhouse for Sentry
kubectl apply -f manifests/base/app-observability/sentry/clickhouse/

# Install Kafka for Sentry
kubectl apply -f manifests/base/app-observability/sentry/kafka/

# Install Redis for Sentry
kubectl apply -f manifests/base/app-observability/sentry/redis/

# Install PostgreSQL for Sentry
kubectl apply -f manifests/base/app-observability/sentry/postgres/

# Install Sentry
helm upgrade --install sentry self-hosted/sentry \
  --namespace sentry \
  --set clickhouse.cluster.enabled=true \
  --set clickhouse.persistence.enabled=true \
  --set kafka.enabled=true \
  --set redis.enabled=true \
  --set postgresql.enabled=true \
  --set filestore.backend=s3 \
  --set filestore.s3.bucket.name=sentry-data \
  --set ingress.enabled=true \
  --set ingress.hostname=sentry.example.com \
  --set email.backend=smtp \
  --wait

echo "Sentry installed!"
echo "Error Tracking Dashboard: https://sentry.example.com"
```

---

## 4.7 Grafana Dashboards

### Import Dashboards

#### `scripts/observability/import-grafana-dashboards.sh`
```bash
#!/bin/bash
set -e

GRAFANA_URL="https://grafana.example.com"
GRAFANA_TOKEN="${GRAFANA_TOKEN:-admin:admin}"

# Import dashboards
for dashboard in dashboards/*.json; do
  curl -X POST "$GRAFANA_URL/api/dashboards/import" \
    -H "Authorization: Bearer $GRAFANA_TOKEN" \
    -H "Content-Type: application/json" \
    -d @"$dashboard"
done

echo "Grafana dashboards imported!"
```

#### `dashboards/cluster-overview.json`
```json
{
  "dashboard": {
    "title": "Cluster Overview",
    "panels": [
      {
        "title": "CPU Usage",
        "targets": [
          {
            "expr": "sum(rate(container_cpu_usage_seconds_total{container!=\"\"}[5m])) by (namespace)"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Memory Usage",
        "targets": [
          {
            "expr": "sum(container_memory_working_set_bytes{container!=\"\"}) by (namespace)"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Network Traffic",
        "targets": [
          {
            "expr": "sum(rate(container_network_receive_bytes_total[5m])) by (namespace)"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Pod Count by Namespace",
        "targets": [
          {
            "expr": "sum(kube_pod_status_phase) by (namespace)"
          }
        ],
        "type": "stat"
      }
    ]
  }
}
```

---

## 4.8 Observability Adapters

#### `src/k8s_agent/observability/metrics_adapter.py`
```python
"""Prometheus metrics adapter."""
import httpx
from typing import Dict, Any, List


class PrometheusAdapter:
    """Adapter for Prometheus metrics."""

    def __init__(self, url: str):
        self.base_url = url

    async def query(self, promql: str) -> Dict[str, Any]:
        """Query Prometheus."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/query",
                params={"query": promql}
            )
            return response.json()

    async def query_range(
        self,
        promql: str,
        start: str,
        end: str,
        step: str
    ) -> Dict[str, Any]:
        """Query Prometheus with time range."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/query_range",
                params={
                    "query": promql,
                    "start": start,
                    "end": end,
                    "step": step
                }
            )
            return response.json()

    async def get_cluster_metrics(self) -> Dict[str, Any]:
        """Get cluster-level metrics."""
        metrics = {
            "cpu_usage": await self.query("sum(rate(container_cpu_usage_seconds_total[5m]))"),
            "memory_usage": await self.query("sum(container_memory_working_set_bytes)"),
            "pod_count": await self.query("sum(kube_pod_status_phase)"),
            "node_count": await self.query("count(kube_node_info)")
        }
        return metrics
```

#### `src/k8s_agent/observability/logging_adapter.py`
```python
"""Loki logging adapter."""
import httpx
from typing import Dict, Any, List


class LokiAdapter:
    """Adapter for Loki logging."""

    def __init__(self, url: str):
        self.base_url = url

    async def query_logs(
        self,
        query: str,
        start: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Query logs from Loki."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/loki/api/v1/query_range",
                params={
                    "query": query,
                    "start": start,
                    "limit": limit
                }
            )
            data = response.json()
            return data.get("data", {}).get("result", [])

    async def tail_logs(self, query: str, namespace: str) -> List[Dict[str, Any]]:
        """Tail logs in real-time."""
        # Implementation
        pass
```

#### `src/k8s_agent/governance/cost_adapter.py`
```python
"""OpenCost cost management adapter."""
import httpx
from typing import Dict, Any, List, Optional


class CostAdapter:
    """Adapter for OpenCost cost data."""

    def __init__(self, url: str):
        self.base_url = url

    async def get_monthly_cost(self, month: str) -> Dict[str, Any]:
        """Get total cost for a month."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/cost/monthly",
                params={"month": month}
            )
            return response.json()

    async def get_namespace_cost(self, namespace: str, window: str = "monthly") -> Dict[str, Any]:
        """Get cost breakdown by namespace."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/cost/allocation",
                params={
                    "aggregate": "namespace",
                    "window": window,
                    "filterNamespaces": namespace
                }
            )
            return response.json()

    async def get_budget_status(self, budget_name: str) -> Dict[str, Any]:
        """Get budget status and alerts."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/budgets/{budget_name}"
            )
            return response.json()

    async def forecast_cost(self, namespace: str) -> Dict[str, Any]:
        """Forecast cost for namespace."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/cost/forecast",
                params={"namespace": namespace}
            )
            return response.json()
```

#### `src/k8s_agent/governance/budget_manager.py`
```python
"""Budget management business logic."""
from typing import List, Dict, Any
from .cost_adapter import CostAdapter


class BudgetManager:
    """Business logic for budget management."""

    def __init__(self, cost_adapter: CostAdapter):
        self.cost_adapter = cost_adapter

    async def check_budget_alerts(self) -> List[Dict[str, Any]]:
        """Check for budget alerts across all namespaces."""
        alerts = []
        namespaces = await self._get_all_namespaces()

        for namespace in namespaces:
            cost = await self.cost_adapter.get_namespace_cost(namespace)
            budget = await self.cost_adapter.get_budget_status(namespace)

            usage_ratio = cost["totalCost"] / budget["amount"]
            if usage_ratio > 0.8:
                alerts.append({
                    "namespace": namespace,
                    "severity": "warning" if usage_ratio < 0.9 else "critical",
                    "usage": cost["totalCost"],
                    "budget": budget["amount"],
                    "ratio": usage_ratio
                })

        return alerts

    async def _get_all_namespaces(self) -> List[str]:
        """Get all namespaces with budgets."""
        # Implementation
        pass
```

---

## Verification Steps

After completing this phase:

1. [ ] Verify Prometheus
   ```bash
   kubectl get pods -n monitoring | grep prometheus
   curl http://kube-prometheus-prometheus.monitoring.svc.cluster.local:9090/api/v1/query?query=up
   ```

2. [ ] Verify Grafana
   ```bash
   kubectl get pods -n monitoring | grep grafana
   curl -I https://grafana.example.com
   ```

3. [ ] Verify Loki
   ```bash
   kubectl get pods -n monitoring | grep loki
   curl http://loki.monitoring.svc.cluster.local:3100/ready
   ```

4. [ ] Verify OpenCost
   ```bash
   kubectl get pods -n monitoring | grep opencost
   curl http://opencost.monitoring.svc.cluster.local:9090
   ```

5. [ ] Verify Signoz
   ```bash
   kubectl get pods -n signoz
   curl -I https://signoz.example.com
   ```

6. [ ] Verify Posthog
   ```bash
   kubectl get pods -n posthog
   curl -I https://posthog.example.com
   ```

7. [ ] Verify Sentry
   ```bash
   kubectl get pods -n sentry
   curl -I https://sentry.example.com
   ```

8. [ ] Test cost tracking
   ```bash
   curl http://opencost.monitoring.svc.cluster.local:9090/api/cost/allocation?aggregate=namespace
   ```

---

## Next Phase

Proceed to **Phase 5: Application Platform** ([05-app-platform-plan.md](./05-app-platform-plan.md))
