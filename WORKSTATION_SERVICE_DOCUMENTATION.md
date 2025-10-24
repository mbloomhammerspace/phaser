# NVIDIA RAG Blueprint - Workstation Service Documentation
## Complete Port Forward Guide for MacBook Access

**Generated:** October 23, 2025  
**Target:** MacBook Workstation  
**Purpose:** Access all NVIDIA RAG Blueprint services from local machine

---

## 🚀 **Quick Start**

```bash
# Start all port forwards
./setup-workstation-port-forwards.sh start

# Check status
./setup-workstation-port-forwards.sh status

# Connect to session
./setup-workstation-port-forwards.sh connect
```

---

## 📋 **Service Inventory**

### **Core RAG Services**

| Service | Local Port | Remote Service | Description | Access URL |
|---------|------------|----------------|-------------|------------|
| **RAG Playground** | 3000 | clean-rag-frontend:3000 | Document search and analysis interface | http://localhost:3000 |
| **RAG Server API** | 8081 | rag-server:8081 | Core RAG processing endpoints | http://localhost:8081 |
| **RAG Ingestor** | 8082 | ingestor-server:8082 | PDF and document processing service | http://localhost:8082 |

### **AI-Q Research Assistant**

| Service | Local Port | Remote Service | Description | Access URL |
|---------|------------|----------------|-------------|------------|
| **AI-Q Frontend** | 8051 | aiq-aira-frontend:3000 | Enterprise AI research interface | http://localhost:8051 |
| **AI-Q Backend** | 3838 | aiq-aira-backend:3838 | Research assistant processing | http://localhost:3838 |
| **AI-Q Nginx** | 8052 | aiq-aira-nginx:8051 | Load balancer for AI-Q services | http://localhost:8052 |
| **Phoenix Service** | 6006 | aiq-phoenix:6006 | AI-Q component | http://localhost:6006 |
| **AI-Q LLM** | 8000 | aira-instruct-llm:8000 | Language model processing | http://localhost:8000 |

### **Vector Database & Management**

| Service | Local Port | Remote Service | Description | Access URL |
|---------|------------|----------------|-------------|------------|
| **Milvus Database** | 19530 | milvus:19530 | Vector storage and retrieval | localhost:19530 |
| **Milvus Metrics** | 9091 | milvus:9091 | Database performance metrics | http://localhost:9091 |
| **Attu UI** | 3001 | attu:3000 | Milvus database management | http://localhost:3001 |

### **Observability & Monitoring**

| Service | Local Port | Remote Service | Description | Access URL |
|---------|------------|----------------|-------------|------------|
| **Jaeger Tracing** | 16686 | jaeger-query:16686 | Distributed tracing interface | http://localhost:16686 |
| **Zipkin Tracing** | 9411 | zipkin:9411 | Alternative tracing interface | http://localhost:9411 |
| **Grafana Dashboard** | 30671 | grafana:3000 | Metrics visualization | http://localhost:30671 |

### **NeMo Retriever Services**

| Service | Local Port | Remote Service | Description | Access URL |
|---------|------------|----------------|-------------|------------|
| **NeMo Embedding** | 8001 | nemoretriever-embedding-ms:8000 | Vector embedding generation | http://localhost:8001 |
| **NeMo Reranking** | 8002 | nemoretriever-reranking-ms:8000 | Search result reranking | http://localhost:8002 |

### **Data & Cache Services**

| Service | Local Port | Remote Service | Description | Access URL |
|---------|------------|----------------|-------------|------------|
| **Redis Cache** | 6379 | rag-redis-master:6379 | In-memory data store | localhost:6379 |
| **etcd Database** | 2379 | etcd:2379 | Kubernetes cluster state | localhost:2379 |

---

## 🔧 **Port Forward Management**

### **Script Commands**

```bash
# Start all port forwards
./setup-workstation-port-forwards.sh start

# Stop all port forwards
./setup-workstation-port-forwards.sh stop

# Restart all port forwards
./setup-workstation-port-forwards.sh restart

# Check status
./setup-workstation-port-forwards.sh status

# Connect to session
./setup-workstation-port-forwards.sh connect

# Show help
./setup-workstation-port-forwards.sh help
```

### **Manual Port Forwarding**

If you prefer manual control:

```bash
# RAG Playground
kubectl port-forward service/clean-rag-frontend 3000:3000 --address=0.0.0.0

# Attu (Milvus UI)
kubectl port-forward service/attu 3001:3000 --address=0.0.0.0

# Jaeger Tracing
kubectl port-forward service/jaeger-query 16686:16686 --address=0.0.0.0

# Zipkin Tracing
kubectl port-forward service/zipkin 9411:9411 --address=0.0.0.0

# Grafana Dashboard
kubectl port-forward service/grafana 30671:3000 --address=0.0.0.0

# AI-Q Research Assistant
kubectl port-forward service/aiq-aira-frontend 8051:3000 --address=0.0.0.0
```

---

## 🎯 **Primary Access Points**

### **For End Users**
- **RAG Playground**: http://localhost:3000 - Main document search interface
- **AI-Q Research Assistant**: http://localhost:8051 - Enterprise AI research tool

### **For Administrators**
- **Attu (Milvus UI)**: http://localhost:3001 - Database management
- **Grafana Dashboard**: http://localhost:30671 - System monitoring
- **Jaeger Tracing**: http://localhost:16686 - Request tracing

### **For Developers**
- **RAG Server API**: http://localhost:8081 - API endpoints
- **Milvus Database**: localhost:19530 - Vector database access
- **Redis Cache**: localhost:6379 - Cache access

---

## 📊 **Service Health Monitoring**

### **Check Service Status**
```bash
# Check all services
kubectl get pods -A | grep -E "(rag|milvus|attu|jaeger|zipkin|grafana)"

# Check specific service
kubectl get pods -l app=attu
kubectl get pods -l app=clean-rag-frontend
```

### **Service Health URLs**
- **RAG Playground Health**: http://localhost:3000/health
- **RAG Server Health**: http://localhost:8081/health
- **Milvus Health**: http://localhost:9091/health
- **Jaeger Health**: http://localhost:16686/health

---

## 🔍 **Troubleshooting**

### **Common Issues**

1. **Port Already in Use**
   ```bash
   # Find process using port
   lsof -i :3000
   
   # Kill process
   kill -9 <PID>
   ```

2. **Service Not Available**
   ```bash
   # Check if service exists
   kubectl get service <service-name>
   
   # Check pod status
   kubectl get pods -l app=<service-name>
   ```

3. **Port Forward Fails**
   ```bash
   # Check kubectl connection
   kubectl cluster-info
   
   # Restart port forwards
   ./setup-workstation-port-forwards.sh restart
   ```

### **Log Files**
- **Port Forward Log**: `./port-forward.log`
- **Screen Session**: `screen -r rag-port-forwards`

---

## 🚀 **Advanced Usage**

### **Custom Port Mapping**
Edit the script to change port mappings:
```bash
# In setup-workstation-port-forwards.sh
declare -A WORKSTATION_PORTS=(
    ["rag-playground"]="3000"  # Change to desired port
    ["attu"]="3001"            # Change to desired port
    # ... other services
)
```

### **Selective Port Forwarding**
Start only specific services:
```bash
# Start only RAG services
kubectl port-forward service/clean-rag-frontend 3000:3000 --address=0.0.0.0 &
kubectl port-forward service/rag-server 8081:8081 --address=0.0.0.0 &
```

### **Background Service**
Run as system service:
```bash
# Create systemd service (Linux)
sudo systemctl enable rag-port-forwards
sudo systemctl start rag-port-forwards
```

---

## 📝 **Service Dependencies**

### **Core Dependencies**
```
RAG Playground (3000) → RAG Server (8081) → Milvus (19530)
                    ↓
                NeMo Services (8001, 8002)
                    ↓
                Redis Cache (6379)
```

### **AI-Q Dependencies**
```
AI-Q Frontend (8051) → AI-Q Backend (3838) → AI-Q LLM (8000)
                    ↓
                Phoenix (6006)
```

### **Monitoring Dependencies**
```
Grafana (30671) → Prometheus → All Services
Jaeger (16686) → All Services
Zipkin (9411) → All Services
```

---

## 🎯 **Best Practices**

1. **Always use the script** for consistent port forwarding
2. **Check service health** before accessing URLs
3. **Monitor logs** for any connection issues
4. **Use screen session** for persistent connections
5. **Keep services updated** with latest versions

---

*This documentation is automatically generated and maintained by the NVIDIA RAG Blueprint system.*
