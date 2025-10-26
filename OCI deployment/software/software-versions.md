# Software Versions - OCI Deployment
## Complete Software Stack Inventory

### Core Infrastructure

#### Kubernetes
- **Version**: v1.30.4
- **CNI**: Calico
- **Container Runtime**: containerd
  - master-node: containerd://1.7.21
  - instance-20251003-1851: containerd://1.7.27
  - instance-20251010-1127: containerd://1.7.28
  - worker-node-1: containerd://1.7.21
  - worker-node-2: containerd://1.7.21

#### Operating Systems
- **master-node**: Ubuntu 24.04.2 LTS (kernel 6.8.0-1028-oracle)
- **instance-20251003-1851**: Ubuntu 22.04.5 LTS (kernel 6.8.0-1035-oracle)
- **instance-20251010-1127**: Ubuntu 22.04.5 LTS (kernel 6.8.0-1037-oracle)
- **worker-node-1**: Ubuntu 24.04.2 LTS (kernel 6.14.0-1015-oracle)
- **worker-node-2**: Ubuntu 24.04.2 LTS (kernel 6.8.0-1028-oracle)

### NVIDIA RAG Blueprint Components

#### Core RAG Services
- **RAG Server**: nvcr.io/nvidia/blueprint/rag-server:2.2.0
- **RAG Frontend**: nvcr.io/nvidia/blueprint/rag-frontend:2.3.0
- **Ingestor Server**: nvcr.io/nvidia/blueprint/ingestor-server:2.2.0

#### AI/ML Models (NIM)
- **Embedding Model**: nvcr.io/nim/nvidia/llama-3.2-nv-embedqa-1b-v2:1.6.0
- **Reranking Model**: nvcr.io/nim/nvidia/llama-3.2-nv-rerankqa-1b-v2:1.5.0
- **LLM Model**: nvcr.io/nim/nvidia/llama-3.3-nemotron-super-49b-v1:1.8.5

#### NV-Ingest Services
- **NV-Ingest Runtime**: nvcr.io/nvidia/nemo-microservices/nv-ingest:25.6.2
- **RAG NV-Ingest**: nvcr.io/nvidia/nemo-microservices/nv-ingest:25.6.2

### Data Storage

#### Vector Database
- **Milvus**: milvusdb/milvus:v2.4.13
- **Attu (Management UI)**: zilliz/attu:v2.4

#### Object Storage
- **MinIO**: minio/minio:latest

#### Cache/Database
- **Redis**: redis:7-alpine
- **Redis Stack**: redis/redis-stack

### Observability Stack

#### Tracing
- **Jaeger Query**: jaegertracing/jaeger-query:1.45
- **Zipkin**: openzipkin/zipkin:latest
- **OpenTelemetry Collector**: otel/opentelemetry-collector-contrib:latest

#### Monitoring
- **RAG OpenTelemetry Collector**: otel/opentelemetry-collector-contrib:latest

### AIQ Research Assistant

#### Core Components
- **AIQ Backend**: nvcr.io/nvidia/blueprint/aira-backend:v1.1.0
- **AIQ Frontend**: nvcr.io/nvidia/blueprint/aira-frontend:v1.1.0
- **Phoenix**: arizephoenix/phoenix:latest
- **Nginx**: nginx:latest

### Supporting Services

#### Infrastructure
- **etcd**: quay.io/coreos/etcd:v3.5.5
- **Nemo Agent Toolkit**: python:3.12-slim

#### External Services
- **AIQ Instruct LLM**: nvcr.io/nim/nvidia/llama-3.3-nemotron-super-49b-v1:1.8.5
- **NIM AIQ**: nvcr.io/nim/nvidia/llama-3.3-nemotron-super-49b-v1:1.8.5
- **NIM LLM**: nvcr.io/nim/nvidia/llama-3.3-nemotron-super-49b-v1:1.8.5

### Helm Charts

#### Deployed Charts
- **nvidia-rag**: nvidia-blueprint-rag-v2.2.0 (v2.2.0) - Status: deployed
- **rag-blueprint-redis**: redis-23.1.3 (8.2.2) - Status: deployed
- **aiq**: aiq-research-assistant-0.1.0 (0.1.0) - Status: failed

### Container Images Summary

#### NVIDIA NGC Images
- nvcr.io/nvidia/blueprint/rag-server:2.2.0
- nvcr.io/nvidia/blueprint/rag-frontend:2.3.0
- nvcr.io/nvidia/blueprint/ingestor-server:2.2.0
- nvcr.io/nvidia/blueprint/aira-backend:v1.1.0
- nvcr.io/nvidia/blueprint/aira-frontend:v1.1.0
- nvcr.io/nvidia/nemo-microservices/nv-ingest:25.6.2

#### NVIDIA NIM Images
- nvcr.io/nim/nvidia/llama-3.2-nv-embedqa-1b-v2:1.6.0
- nvcr.io/nim/nvidia/llama-3.2-nv-rerankqa-1b-v2:1.5.0
- nvcr.io/nim/nvidia/llama-3.3-nemotron-super-49b-v1:1.8.5

#### Third-Party Images
- milvusdb/milvus:v2.4.13
- zilliz/attu:v2.4
- minio/minio:latest
- redis:7-alpine
- redis/redis-stack
- jaegertracing/jaeger-query:1.45
- openzipkin/zipkin:latest
- otel/opentelemetry-collector-contrib:latest
- quay.io/coreos/etcd:v3.5.5
- nginx:latest
- python:3.12-slim
- alpine:3.19
- arizephoenix/phoenix:latest

### Service Versions

#### Core Services
- **RAG Server**: v2.2.0
- **RAG Frontend**: v2.3.0
- **Ingestor Server**: v2.2.0
- **Milvus**: v2.4.13
- **Attu**: v2.4

#### AI Models
- **Embedding**: llama-3.2-nv-embedqa-1b-v2:1.6.0
- **Reranking**: llama-3.2-nv-rerankqa-1b-v2:1.5.0
- **LLM**: llama-3.3-nemotron-super-49b-v1:1.8.5

#### Observability
- **Jaeger**: 1.45
- **Zipkin**: latest
- **OpenTelemetry**: latest

### Deployment Status

#### Active Deployments
- clean-rag-frontend: 1/1 ready
- ingestor-server: 3/3 ready
- milvus: 1/1 ready
- minio: 1/1 ready
- nemoretriever-embedding-ms: 1/1 ready
- nemoretriever-reranking-ms: 1/1 ready
- nv-ingest-ms-runtime: 4/4 ready
- rag-nv-ingest: 4/4 ready
- rag-opentelemetry-collector: 1/1 ready
- rag-redis-master: 1/1 ready
- rag-server: 1/1 ready
- redis: 1/1 ready
- zipkin: 1/1 ready

#### Failed/Inactive Deployments
- aiq-aira-backend: 0/0 ready
- aiq-aira-frontend: 0/0 ready
- aiq-aira-nginx: 0/0 ready
- aiq-frontend: 0/0 ready
- aiq-phoenix: 0/0 ready
- etcd: 0/0 ready
- jaeger-query: 0/0 ready
- nemo-agent-toolkit: 0/1 ready
- otel-collector: 0/0 ready

### Version Compatibility Matrix

#### Kubernetes Compatibility
- All container images compatible with Kubernetes v1.30.4
- Containerd versions: 1.7.21-1.7.28
- CNI: Calico (latest)

#### NVIDIA Stack Compatibility
- RAG Blueprint: v2.2.0-v2.3.0
- NIM Models: v1.5.0-v1.8.5
- NV-Ingest: v25.6.2

#### Observability Compatibility
- Jaeger: v1.45
- Zipkin: latest
- OpenTelemetry: latest
- All compatible with Kubernetes v1.30.4
