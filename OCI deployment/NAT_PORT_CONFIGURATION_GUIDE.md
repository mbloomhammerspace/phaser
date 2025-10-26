# NVIDIA RAG Blueprint - NAT Port Configuration Guide
## Local Workstation Port Forwarding Setup

**Generated:** October 23, 2025  
**Purpose:** Complete guide for establishing NAT port forwards from Kubernetes cluster to local MacBook workstation  
**Target:** MacBook Pro/Air with local development access

---

## 🎯 **Overview**

This guide provides comprehensive instructions for establishing NAT (Network Address Translation) port forwards from your Kubernetes cluster to your local MacBook workstation, enabling seamless access to all NVIDIA RAG Blueprint services.

---

## 📋 **Prerequisites**

### **System Requirements**
- macOS 10.15+ (Catalina or later)
- kubectl installed and configured
- SSH access to Kubernetes cluster
- Screen utility (for persistent sessions)

### **Network Requirements**
- Stable internet connection
- Access to Kubernetes cluster API server
- No firewall blocking kubectl port-forward

---

## 🔧 **NAT Port Configuration**

### **Port Mapping Strategy**

| Service Category | Local Port Range | Remote Service | Protocol | Purpose |
|------------------|------------------|----------------|----------|---------|
| **Web Interfaces** | 3000-3099 | Frontend Services | HTTP/HTTPS | User interfaces |
| **API Services** | 8000-8099 | Backend APIs | HTTP/HTTPS | REST/GraphQL APIs |
| **Database Services** | 19000-19999 | Database Services | TCP/gRPC | Database connections |
| **Monitoring** | 30000-30999 | Observability | HTTP/HTTPS | Metrics and tracing |
| **Cache Services** | 6000-6999 | Cache Services | TCP | In-memory stores |

### **Complete Port Mapping Table**

| Service | Local Port | Remote Service:Port | Protocol | Access URL | Status |
|---------|------------|---------------------|----------|------------|--------|
| **RAG Playground** | 3000 | clean-rag-frontend:3000 | HTTP | http://localhost:3000 | ✅ Active |
| **Attu UI** | 3001 | attu:3000 | HTTP | http://localhost:3001 | ✅ Active |
| **RAG Server API** | 8081 | rag-server:8081 | HTTP | http://localhost:8081 | ✅ Active |
| **RAG Ingestor** | 8082 | ingestor-server:8082 | HTTP | http://localhost:8082 | ✅ Active |
| **AI-Q Frontend** | 8051 | aiq-aira-frontend:3000 | HTTP | http://localhost:8051 | ⚠️ Unhealthy |
| **AI-Q Backend** | 3838 | aiq-aira-backend:3838 | HTTP | http://localhost:3838 | ⚠️ Unhealthy |
| **AI-Q Nginx** | 8052 | aiq-aira-nginx:8051 | HTTP | http://localhost:8052 | ⚠️ Unhealthy |
| **Phoenix Service** | 6006 | aiq-phoenix:6006 | HTTP | http://localhost:6006 | ⚠️ Unhealthy |
| **AI-Q LLM** | 8000 | aira-instruct-llm:8000 | HTTP | http://localhost:8000 | ✅ Active |
| **Milvus Database** | 19530 | milvus:19530 | gRPC | localhost:19530 | ✅ Active |
| **Milvus Metrics** | 9091 | milvus:9091 | HTTP | http://localhost:9091 | ✅ Active |
| **Jaeger Tracing** | 16686 | jaeger-query:16686 | HTTP | http://localhost:16686 | ⚠️ Unhealthy |
| **Zipkin Tracing** | 9411 | zipkin:9411 | HTTP | http://localhost:9411 | ✅ Active |
| **Grafana Dashboard** | 30671 | grafana:3000 | HTTP | http://localhost:30671 | ⚠️ Unhealthy |
| **NeMo Embedding** | 8001 | nemoretriever-embedding-ms:8000 | HTTP | http://localhost:8001 | ✅ Active |
| **NeMo Reranking** | 8002 | nemoretriever-reranking-ms:8000 | HTTP | http://localhost:8002 | ✅ Active |
| **Redis Cache** | 6379 | rag-redis-master:6379 | TCP | localhost:6379 | ✅ Active |
| **etcd Database** | 2379 | etcd:2379 | TCP | localhost:2379 | ✅ Active |

---

## 🚀 **Quick Setup Commands**

### **1. Automated Setup (Recommended)**
```bash
# Check service health
./poll-services.sh poll

# Start all port forwards
./setup-workstation-port-forwards.sh start

# Verify status
./setup-workstation-port-forwards.sh status
```

### **2. Manual Setup (Advanced)**
```bash
# Core RAG Services
kubectl port-forward service/clean-rag-frontend 3000:3000 --address=0.0.0.0 &
kubectl port-forward service/rag-server 8081:8081 --address=0.0.0.0 &
kubectl port-forward service/ingestor-server 8082:8082 --address=0.0.0.0 &

# Vector Database
kubectl port-forward service/milvus 19530:19530 --address=0.0.0.0 &
kubectl port-forward service/milvus 9091:9091 --address=0.0.0.0 &
kubectl port-forward service/attu 3001:3000 --address=0.0.0.0 &

# Observability
kubectl port-forward service/zipkin 9411:9411 --address=0.0.0.0 &
kubectl port-forward service/jaeger-query 16686:16686 --address=0.0.0.0 &

# AI Services
kubectl port-forward service/nemoretriever-embedding-ms 8001:8000 --address=0.0.0.0 &
kubectl port-forward service/nemoretriever-reranking-ms 8002:8000 --address=0.0.0.0 &

# Data Services
kubectl port-forward service/rag-redis-master 6379:6379 --address=0.0.0.0 &
kubectl port-forward service/etcd 2379:2379 --address=0.0.0.0 &
```

---

## 🔍 **Port Forward Management**

### **Screen Session Management**
```bash
# Start persistent session
screen -S rag-port-forwards

# List sessions
screen -list

# Reconnect to session
screen -r rag-port-forwards

# Detach from session (Ctrl+A then D)
# Kill session
screen -S rag-port-forwards -X quit
```

### **Process Management**
```bash
# Check active port forwards
ps aux | grep "kubectl port-forward"

# Kill specific port forward
pkill -f "kubectl port-forward.*3000"

# Kill all port forwards
pkill -f "kubectl port-forward"
```

---

## 🌐 **Service Access Configuration**

### **Primary Access Points**
```bash
# Main interfaces
open http://localhost:3000  # RAG Playground
open http://localhost:3001  # Attu (Milvus UI)
open http://localhost:9411  # Zipkin Tracing

# API endpoints
curl http://localhost:8081/health  # RAG Server
curl http://localhost:8082/health  # RAG Ingestor
curl http://localhost:8000/health  # AI-Q LLM
```

### **Database Connections**
```bash
# Milvus Database (Python)
from pymilvus import connections
connections.connect("localhost", port="19530")

# Redis Cache
redis-cli -h localhost -p 6379

# etcd Database
etcdctl --endpoints=localhost:2379 endpoint health
```

---

## 📊 **Network Configuration Details**

### **Port Forward Architecture**
```
MacBook Workstation (localhost)
    ↓ NAT Port Forward
Kubernetes Cluster Services
    ↓ Service Discovery
Pod Endpoints
```

### **Traffic Flow**
```
Client Request → localhost:PORT → kubectl port-forward → K8s Service → Pod
Pod Response ← K8s Service ← kubectl port-forward ← localhost:PORT ← Client
```

### **Security Considerations**
- Port forwards use `--address=0.0.0.0` for external access
- All traffic is encrypted via kubectl tunnel
- No direct network exposure to cluster
- Authentication handled by Kubernetes RBAC

---

## 🔧 **Advanced Configuration**

### **Custom Port Mapping**
```bash
# Edit setup-workstation-port-forwards.sh
# Change port mappings in the script
kubectl port-forward service/clean-rag-frontend 4000:3000 --address=0.0.0.0 &
# Now accessible at http://localhost:4000
```

### **Load Balancing**
```bash
# Multiple port forwards for load balancing
kubectl port-forward service/rag-server 8081:8081 --address=0.0.0.0 &
kubectl port-forward service/rag-server 8082:8081 --address=0.0.0.0 &
# Access via localhost:8081 or localhost:8082
```

### **SSL/TLS Termination**
```bash
# Forward HTTPS traffic
kubectl port-forward service/clean-rag-frontend 3443:443 --address=0.0.0.0 &
# Access via https://localhost:3443
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Port Already in Use**
   ```bash
   # Find process using port
   lsof -i :3000
   sudo lsof -i :3000
   
   # Kill process
   kill -9 <PID>
   ```

2. **Service Not Found**
   ```bash
   # Check service exists
   kubectl get services
   kubectl get service <service-name>
   
   # Check pods
   kubectl get pods -l app=<service-name>
   ```

3. **Connection Refused**
   ```bash
   # Check service endpoints
   kubectl get endpoints <service-name>
   
   # Check pod health
   kubectl describe pod <pod-name>
   ```

4. **Port Forward Fails**
   ```bash
   # Check kubectl connection
   kubectl cluster-info
   
   # Restart port forwards
   ./setup-workstation-port-forwards.sh restart
   ```

### **Health Checks**
```bash
# Check all services
./poll-services.sh poll

# Check specific service
kubectl get pods -l app=clean-rag-frontend
kubectl describe pod <pod-name>

# Test connectivity
curl -v http://localhost:3000
telnet localhost 19530
```

---

## 📈 **Performance Optimization**

### **Connection Pooling**
```bash
# Use connection pooling for database connections
# Configure in application code
```

### **Keep-Alive Settings**
```bash
# Add keep-alive to kubectl port-forward
kubectl port-forward service/clean-rag-frontend 3000:3000 --address=0.0.0.0 --keep-alive=30s &
```

### **Resource Limits**
```bash
# Monitor resource usage
kubectl top pods
kubectl top nodes

# Check port forward processes
ps aux | grep "kubectl port-forward"
```

---

## 🔒 **Security Best Practices**

### **Access Control**
- Use Kubernetes RBAC for service access
- Implement network policies
- Monitor port forward usage
- Regular security audits

### **Network Security**
- Use VPN for remote access
- Implement firewall rules
- Monitor network traffic
- Encrypt sensitive data

---

## 📝 **Monitoring and Logging**

### **Log Files**
- **Port Forward Log**: `./port-forward.log`
- **Service Health Log**: `./service-health.log`
- **Screen Session**: `screen -r rag-port-forwards`

### **Monitoring Commands**
```bash
# Monitor port forwards
watch -n 5 'ps aux | grep "kubectl port-forward"'

# Monitor service health
./poll-services.sh monitor

# Check network connections
netstat -an | grep LISTEN
```

---

## 🎯 **Best Practices**

1. **Always use the automated scripts** for consistent setup
2. **Monitor service health** before accessing URLs
3. **Use screen sessions** for persistent connections
4. **Keep services updated** with latest versions
5. **Document custom configurations** for team sharing
6. **Implement monitoring** for production use
7. **Regular health checks** to ensure availability

---

## 📞 **Support and Maintenance**

### **Regular Maintenance**
- Weekly service health checks
- Monthly port forward audits
- Quarterly security reviews
- Annual configuration updates

### **Support Resources**
- **Log Files**: Check `./port-forward.log` and `./service-health.log`
- **Screen Session**: `screen -r rag-port-forwards`
- **Status Check**: `./setup-workstation-port-forwards.sh status`
- **Health Check**: `./poll-services.sh poll`

---

*This NAT port configuration guide provides complete instructions for establishing secure, reliable port forwards from your Kubernetes cluster to your local MacBook workstation.*
