# NVIDIA Blueprint Software Manifest
## Comprehensive Version Documentation

**Generated:** October 23, 2025  
**System:** NVIDIA RAG Blueprint on Kubernetes  
**Documentation Version:** 1.0

---

## 🖥️ **Operating System & Base Infrastructure**

### **Kubernetes Cluster**
| Component | Version | Platform | Build Date |
|-----------|---------|----------|------------|
| **Kubernetes Server** | v1.30.4 | linux/amd64 | 2024-08-14 |
| **Kubernetes Client** | v1.33.4 | darwin/arm64 | 2025-08-13 |
| **Go Version** | go1.22.5 (server) / go1.25.0 (client) | - | - |
| **Kustomize** | v5.6.0 | - | - |

### **Node Information**
| Node Name | Role | OS Image | Kernel | Container Runtime | Status |
|-----------|------|----------|--------|-------------------|--------|
| master-node | control-plane | Ubuntu 24.04.2 LTS | 6.8.0-1028-oracle | containerd://1.7.21 | Ready |
| worker-node-1 | worker | Ubuntu 24.04.2 LTS | 6.8.0-1028-oracle | containerd://1.7.21 | Ready |
| worker-node-2 | worker | Ubuntu 24.04.2 LTS | 6.8.0-1028-oracle | containerd://1.7.21 | Ready |
| instance-20251003-1851 | worker | Ubuntu 22.04.5 LTS | 6.8.0-1035-oracle | containerd://1.7.27 | Ready |
| instance-20251010-1127 | worker | Ubuntu 22.04.5 LTS | 6.8.0-1035-oracle | containerd://1.7.28 | Ready |

---

## 🧠 **NVIDIA Blueprint Components**

### **Core RAG Infrastructure**
| Component | Image | Version | Namespace | Status |
|-----------|-------|---------|-----------|--------|
| **Milvus Vector Database** | milvusdb/milvus | v2.4.13 | default | Running |
| **NeMo Retriever Embedding** | nvcr.io/nim/nvidia/llama-3.2-nv-embedqa-1b-v2 | 1.6.0 | default | Running |
| **NeMo Retriever Reranking** | nvcr.io/nim/nvidia/llama-3.2-nv-embedqa-1b-v2 | 1.6.0 | default | Running |
| **RAG Frontend** | nvcr.io/nvidia/blueprint/rag-frontend | 2.3.0 | default | Running |
| **RAG Server** | nvcr.io/nvidia/blueprint/rag-server | 2.2.0 | default | Running |
| **Ingestor Server** | nvcr.io/nvidia/blueprint/ingestor-server | 2.2.0 | default | Running |

### **AI-Q Research Assistant**
| Component | Image | Version | Namespace | Status |
|-----------|-------|---------|-----------|--------|
| **AI-Q Backend** | nvcr.io/nvidia/blueprint/aira-backend | v1.1.0 | default | Running |
| **AI-Q Frontend** | nvcr.io/nvidia/blueprint/aira-frontend | v1.1.0 | default | Running |
| **AI-Q Nginx** | nginx | latest | default | Running |
| **Phoenix** | arizephoenix/phoenix | latest | default | Running |

### **Milvus Management & Monitoring**
| Component | Image | Version | Namespace | Status |
|-----------|-------|---------|-----------|--------|
| **Attu (Milvus UI)** | zilliz/attu | v2.4 | default | Running |
| **Jaeger Query** | jaegertracing/jaeger-query | 1.45 | default | Running |
| **MinIO** | minio/minio | latest | default | Running |

---

## 🔧 **Networking & Storage**

### **Container Network Interface (CNI)**
| Component | Image | Version | Namespace | Status |
|-----------|-------|---------|-----------|--------|
| **Calico API Server** | docker.io/calico/apiserver | v3.27.3 | kube-system | Running |
| **Calico Kube Controllers** | docker.io/calico/kube-controllers | v3.27.3 | kube-system | Running |
| **Calico Node** | docker.io/calico/node | v3.27.3 | kube-system | Running |
| **Calico Typha** | docker.io/calico/typha | v3.27.3 | kube-system | Running |
| **Calico CSI** | docker.io/calico/csi | v3.27.3 | kube-system | Running |
| **Node Driver Registrar** | docker.io/calico/node-driver-registrar | v3.27.3 | kube-system | Running |

### **Storage Systems**
| Component | Image | Version | Namespace | Status |
|-----------|-------|---------|-----------|--------|
| **Local Path Provisioner** | rancher/local-path-provisioner | latest | local-path-storage | Running |
| **etcd** | quay.io/coreos/etcd | v3.5.5 | default | Running |

---

## 📊 **Data & Cache Layer**

### **Database & Cache Services**
| Component | Image | Version | Namespace | Status |
|-----------|-------|---------|-----------|--------|
| **Redis Master** | redis | latest | default | Running |
| **Milvus Database** | milvusdb/milvus | v2.4.13 | default | Running |

---

## 🚨 **Service Status Summary**

### **Running Services (Healthy)**
- ✅ **RAG Frontend** - Port 3000 (Port-forwarded)
- ✅ **Milvus Database** - Port 19530
- ✅ **Attu UI** - Port 3001 (Port-forwarded)
- ✅ **NeMo Retriever Services** - Embedding & Reranking
- ✅ **RAG Server API** - Port 8081
- ✅ **AI-Q Research Assistant** - Port 8051

### **Service Issues**
- ⚠️ **NeMo Agent Toolkit** - CrashLoopBackOff (2 instances)
  - Status: 942 restarts (2m52s ago)
  - Status: 687 restarts (3m59s ago)

---

## 🔌 **Port Mappings & Access**

### **External Access Points**
| Service | Local Port | Remote Port | Protocol | Status |
|---------|------------|-------------|----------|--------|
| **RAG Playground** | 3000 | 3000 | HTTP | ✅ Active |
| **Attu (Milvus UI)** | 3001 | 3000 | HTTP | ✅ Active |
| **Milvus Database** | 19530 | 19530 | gRPC | ✅ Available |
| **RAG Server API** | 8081 | 8081 | HTTP | ✅ Available |

### **NodePort Services**
| Service | NodePort | Target Port | Protocol |
|---------|----------|-------------|----------|
| **Milvus Direct** | 30197 | 19530 | TCP |
| **Milvus External** | 30196 | 19530 | TCP |
| **Milvus NodePort** | 30195 | 19530 | TCP |

---

## 📋 **Configuration Management**

### **Active ConfigMaps**
| ConfigMap | Namespace | Data Count | Purpose |
|-----------|-----------|------------|---------|
| **blueprint-ingest-script** | default | 1 | RAG ingestion scripts |
| **fix-milvus-schema-configmap** | default | 1 | Milvus schema configuration |
| **fix-milvus-schema-langchain-configmap** | default | 1 | LangChain integration |
| **milvus-mcp-server-config** | default | 1 | MCP server configuration |
| **nvidia-rag-ingest-script** | default | 1 | NVIDIA RAG ingestion |
| **nvidia-rag-mcp-configmap** | default | 2 | MCP configuration |
| **rag-playground-registry-configmap** | default | 4 | Playground registry |
| **rag-playground-script** | default | 1 | Playground scripts |
| **rag-server-mcp-script** | default | 1 | RAG server MCP |

---

## 🎯 **Blueprint Architecture Summary**

### **Core Components**
1. **Vector Database**: Milvus v2.4.13 with Attu v2.4 management UI
2. **AI Models**: NeMo Retriever with Llama 3.2 embedding model v1.6.0
3. **RAG Pipeline**: NVIDIA Blueprint v2.3.0 frontend, v2.2.0 server
4. **Research Assistant**: AI-Q v1.1.0 with Phoenix integration
5. **Storage**: Local path provisioner with etcd v3.5.5
6. **Networking**: Calico CNI v3.27.3

### **Service Dependencies**
```
RAG Frontend (3000) → RAG Server (8081) → Milvus (19530)
                    ↓
                NeMo Retriever Services
                    ↓
                Redis Cache
```

### **Access URLs**
- **RAG Playground**: http://localhost:3000
- **Attu (Milvus UI)**: http://localhost:3001
- **AI-Q Research Assistant**: http://localhost:8051 (if port-forwarded)

---

## 📝 **Notes & Recommendations**

### **Version Compatibility**
- ✅ Kubernetes v1.30.4 is production-ready
- ✅ Milvus v2.4.13 is the latest stable release
- ✅ NeMo Retriever v1.6.0 supports latest NVIDIA models
- ⚠️ Client/Server version skew warning (client v1.33 vs server v1.30)

### **Operational Status**
- 🟢 **Core RAG Pipeline**: Fully operational
- 🟢 **Vector Database**: Healthy with management UI
- 🟢 **AI Models**: Embedding and reranking services active
- 🟡 **NeMo Agent Toolkit**: Requires troubleshooting (CrashLoopBackOff)

### **Next Steps**
1. Investigate NeMo Agent Toolkit crash issues
2. Consider upgrading Kubernetes client to match server version
3. Monitor resource usage for GPU workloads
4. Implement backup strategy for Milvus data

---

*This manifest was automatically generated from the live Kubernetes cluster state on October 23, 2025.*
