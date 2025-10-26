# OCI Deployment Documentation
## Kubernetes RAG Cluster - October 3rd, 2024 to Present

### Overview
This document provides comprehensive documentation for recreating the OCI-based Kubernetes RAG cluster deployed since October 3rd, 2024. The cluster runs NVIDIA's RAG Blueprint with GPU-accelerated AI workloads, vector database (Milvus), and document processing pipelines.

### Cluster Architecture
- **Master Node**: 1x control plane node
- **GPU Worker Nodes**: 2x high-performance GPU nodes (8 GPUs each)
- **Regular Worker Nodes**: 2x standard compute nodes
- **Total GPUs**: 16x NVIDIA GPUs across 2 nodes

---

## Hardware Specifications

### Master Node
- **Instance**: master-node
- **IP**: 10.0.0.128
- **OS**: Ubuntu 24.04.2 LTS
- **Kernel**: 6.8.0-1028-oracle
- **CPU**: 2 cores
- **Memory**: 16GB (16372216Ki)
- **Container Runtime**: containerd://1.7.21
- **Kubernetes**: v1.30.4

### GPU Worker Nodes

#### instance-20251003-1851
- **IP**: 10.0.0.25
- **OS**: Ubuntu 22.04.5 LTS
- **Kernel**: 6.8.0-1035-oracle
- **CPU**: 224 cores
- **Memory**: 2TB (2113353432Ki)
- **GPU**: 8x NVIDIA GPUs
- **Container Runtime**: containerd://1.7.27
- **Kubernetes**: v1.30.4

#### instance-20251010-1127
- **IP**: 10.0.0.60
- **OS**: Ubuntu 22.04.5 LTS
- **Kernel**: 6.8.0-1037-oracle
- **CPU**: 224 cores
- **Memory**: 2TB (2113353396Ki)
- **GPU**: 8x NVIDIA GPUs
- **Container Runtime**: containerd://1.7.28
- **Kubernetes**: v1.30.4

### Regular Worker Nodes

#### worker-node-1
- **IP**: 10.0.0.167
- **OS**: Ubuntu 24.04.2 LTS
- **Kernel**: 6.14.0-1015-oracle
- **CPU**: 2 cores
- **Memory**: 16GB (16372440Ki)
- **Status**: SchedulingDisabled
- **Container Runtime**: containerd://1.7.21
- **Kubernetes**: v1.30.4

#### worker-node-2
- **IP**: 10.0.0.249
- **OS**: Ubuntu 24.04.2 LTS
- **Kernel**: 6.8.0-1028-oracle
- **CPU**: 2 cores
- **Memory**: 16GB (16372216Ki)
- **Status**: SchedulingDisabled
- **Container Runtime**: containerd://1.7.21
- **Kubernetes**: v1.30.4

---

## Software Stack

### Core Kubernetes Components
- **Kubernetes**: v1.30.4
- **Container Runtime**: containerd 1.7.21-1.7.28
- **CNI**: Calico
- **Storage**: CSI with NFS (Hammerspace)

### NVIDIA RAG Blueprint Components

#### RAG Server
- **Image**: nvcr.io/nvidia/blueprint/rag-server:2.2.0
- **Service**: rag-server (ClusterIP: 10.233.34.93:8081)
- **External Access**: rag-server-nodeport (NodePort: 30081)

#### RAG Frontend
- **Image**: nvcr.io/nvidia/blueprint/rag-frontend:2.3.0
- **Service**: clean-rag-frontend (ClusterIP: 10.233.26.90:3000)

#### Ingestor Server
- **Image**: nvcr.io/nvidia/blueprint/ingestor-server:2.2.0
- **Replicas**: 3
- **Service**: ingestor-server (ClusterIP: 10.233.51.201:8082)

### Vector Database
- **Milvus**: milvusdb/milvus:v2.4.13
- **Service**: milvus (ClusterIP: 10.233.53.224:19530,9091)
- **External Access**: Multiple NodePort services (30195-30197)
- **Management UI**: Attu v2.4 (NodePort: 30082)

### AI/ML Services

#### NVIDIA Inference Microservices (NIM)
- **Embedding Model**: nvcr.io/nim/nvidia/llama-3.2-nv-embedqa-1b-v2:1.6.0
- **Reranking Model**: nvcr.io/nim/nvidia/llama-3.2-nv-rerankqa-1b-v2:1.5.0
- **LLM Model**: nvcr.io/nim/nvidia/llama-3.3-nemotron-super-49b-v1:1.8.5

#### NV-Ingest Services
- **Image**: nvcr.io/nvidia/nemo-microservices/nv-ingest:25.6.2
- **nv-ingest-ms-runtime**: 4 replicas
- **rag-nv-ingest**: 4 replicas
- **Services**: ClusterIP on ports 7670-7671

### Storage
- **MinIO**: minio/minio:latest
- **Service**: minio (ClusterIP: 10.233.54.117:9000,9001)
- **NFS**: Hammerspace hub mount at /mnt/anvil/hub

### Observability Stack
- **Jaeger**: jaegertracing/jaeger-query:1.45 (NodePort: 30670)
- **Zipkin**: openzipkin/zipkin:latest (NodePort: 30669)
- **OpenTelemetry Collector**: otel/opentelemetry-collector-contrib:latest
- **Redis**: redis:7-alpine and redis/redis-stack

### AIQ Research Assistant
- **Backend**: nvcr.io/nvidia/blueprint/aira-backend:v1.1.0
- **Frontend**: nvcr.io/nvidia/blueprint/aira-frontend:v1.1.0
- **Phoenix**: arizephoenix/phoenix:latest
- **Nginx**: nginx:latest

---

## Network Configuration

### Service Ports
- **RAG Server**: 8081 (internal), 30081 (external)
- **RAG Frontend**: 3000 (internal)
- **Milvus**: 19530, 9091 (internal), 30195-30197 (external)
- **Attu**: 3001 (internal), 30082 (external)
- **Jaeger**: 16686 (internal), 30670 (external)
- **Zipkin**: 9411 (internal), 30669 (external)
- **AIQ Frontend**: 3000 (internal), 30080 (external)

### External Access Points
- **RAG Pipeline**: http://10.0.0.236:8081/v1/generate (jumphost)
- **RAG Frontend**: http://<master-ip>:30080
- **Milvus**: http://<master-ip>:30195-30197
- **Attu**: http://<master-ip>:30082
- **Jaeger**: http://<master-ip>:30670
- **Zipkin**: http://<master-ip>:30669

---

## Storage Configuration

### Persistent Volumes
- **Hammerspace Hub**: NFS mount at /mnt/anvil/hub
- **NFS Server**: 150.136.225.57:/hub
- **Mount Options**: vers=4.2,hard,intr
- **Capacity**: 200Gi per PV

### Data Flow
1. **Source**: Files uploaded to /mnt/anvil/hub/case-*
2. **Processing**: folder-ingest jobs scan directories
3. **Storage**: MinIO for object storage
4. **Vector DB**: Milvus for embeddings
5. **Search**: RAG pipeline queries Milvus

---

## Deployment History (October 3rd - Present)

### Major Changes
1. **October 3rd**: Initial cluster deployment
2. **October 6th**: Ingested 11k files into Milvus
3. **October 15th**: NVIDIA RAG Blueprint deployment (v2.2.0)
4. **October 20th**: AIQ demo first release candidate
5. **October 21st**: AIQ Research Assistant deployment
6. **October 24th**: Port forwarding guide and documentation updates
7. **October 26th**: In-memory management updates

### Key Fixes Applied
- **DNS Resolution**: Fixed Calico CNI networking issues
- **NFS Mounting**: Simplified mount options for Hammerspace
- **GPU Balancing**: Implemented Pod Topology Spread Constraints
- **Performance Optimization**: Scaled ingestor-server and optimized batch processing
- **Service Health**: Fixed RAG server connectivity and model configurations

---

## Replication Instructions

### Prerequisites
1. OCI instances with GPU support
2. Ubuntu 22.04.5 LTS or 24.04.2 LTS
3. NVIDIA GPU drivers and container runtime
4. Hammerspace NFS access
5. Kubernetes v1.30.4

### Deployment Steps
1. **Infrastructure Setup**: Provision OCI instances as specified
2. **Kubernetes Installation**: Deploy Kubernetes v1.30.4 with containerd
3. **GPU Setup**: Install NVIDIA drivers and container runtime
4. **Storage Configuration**: Mount Hammerspace NFS
5. **RAG Blueprint**: Deploy NVIDIA RAG Blueprint v2.2.0
6. **Service Configuration**: Configure external access and networking
7. **Observability**: Deploy monitoring and tracing stack
8. **Testing**: Verify all services and data flow

### Configuration Files
All configuration files, manifests, and scripts are included in the `OCI deployment/` directory structure.

---

## Monitoring and Maintenance

### Key Metrics
- **GPU Utilization**: Monitor across both GPU nodes
- **Ingest Rate**: Target 10+ documents/second
- **Service Health**: Regular health checks on all components
- **Storage Usage**: Monitor NFS and MinIO capacity

### Troubleshooting
- **DNS Issues**: Check Calico CNI configuration
- **NFS Mount**: Verify Hammerspace connectivity
- **GPU Imbalance**: Use Pod Topology Spread Constraints
- **Performance**: Monitor ingestor-server scaling and batch sizes

---

## Contact Information
For questions about this deployment, refer to the comprehensive documentation in the `OCI deployment/` directory structure.
