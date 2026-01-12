this is the initial plan for this repo

repo purpose:

this repo includes: 
- all resources of a k8s lifecycle, include k8s cluster create, manage, monitor, and so on. 
- all current k8s manifests through gitops way to manage k8s clusters

repo structure:

.
├── .ai
│   └── summaries -> all ai generated summaries saved here, the summarys should saved into date based folders
│       └── 26-01-08
├── .devcontainer -> all docker compose configs for start the repo
├── .claude -> configs for claude code
├── debug -> all the temp files saved here for debugging
├── docs
│   ├── AI-external-context -> docs content help ai get special context from external
│   ├── biz -> all logic about this repo
│   ├── blogs -> knowledge of how to let the ai manage the k8s env better
│   ├── development -> all development plans, notes and logs
│   │   ├── 26-01-08
│   │   │   └── init-plan.md
│   │   └── 26-01-09
│   ├── requirements -> all requirements docs
│   └── TODO.md -> todo list for this repo, only include not finished tasks
├── src -> all source code/manifests for this repo
└── scripts -> all scripts for this repo

base environment:
- huawei cloud ecs instance as the base host
- storage: huaweicloud evs, scs, and obs
- os: debian 13
- lbs: huaweicloud elb
- terraform for infra as code
- k3s for lightweight k8s cluster
- rancher for k8s cluster management
- helm/helmfile/kustomize for k8s manifests management
- k8s version: 1.32
- system basic monitoring tool: prometheus + grafana + loki + tempo
- alerting tool: alertmanager

app monitoring:
- posthog: product analytics
- sentry: error tracking
- signoz: application performance monitoring

internal developer tools:
- backstage: as developer portal
- homer: as internal services portal
- n8n: as workflow automation tool
- prefect: as workflow orchestration tool
- dagster: as data orchestration tool
- langfuse: as llm observability platform
- coder: for ide
- bitwarden/server: for personal secrets management
- gitlab: for git repo management

infra management:
- jumpserver: bastion host
- velero: for k8s backup and restore

environment infrastructure:
- cert-manager: for ssl certs management
- kong/kgateway: as api gateway
- identity and access management: Keycloak/authentik/zitadel
- argocd: for gitops
- Linkerd: as Microservices mesh
- vault: for secrets management
- Cilium: as networking and security layer
- Harbor: as container image registry

service infrastructure:
- kusion: developer create an AppConfiguration without environment-specific values, kusion will help to generate the final configuration for different environments.
- apollo: as configuration center
- litellm: as local llm deployment
- athens: as go module proxy
- pypiserver: as python package index server
- verdaccio: as npm package proxy server
- kmcp: manage mcp lifecycle in k8s
- kagent: Kagent is an open-source programming framework that brings the power of agentic AI to cloud-native environments. Built specifically for DevOps and platform engineers, Kagent enables AI agents to run directly in Kubernetes clusters to automate operations, troubleshoot issues, and solve complex cloud-native challenges.
- mcp-context-forge: customize new mcp from diff mcp servers

custom middlewares & databases:
- kafka ui: as kafka management tool
- strimzi-kafka-operator: as kafka operator
- redisinsight: as redis gui tool
- redis-operator: as redis operator
- superset: as data visualization platform
- postgres-operator: as postgres operator
- compass-web: mongodb gui tool
- mongodb-kubernetes: as mongodb operator
- cloud-on-k8s: as elasticsearch operator
- kibana: as elasticsearch gui tool
- bytebase: DevSecOps platform for database
