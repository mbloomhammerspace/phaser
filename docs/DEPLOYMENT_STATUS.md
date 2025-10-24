# Deployment Status Guide

## 🎯 Current Deployment Status

This document provides a comprehensive overview of the current deployment status for both the RAG Playground and AI-Q Research Assistant systems.

## 🚀 RAG Playground Status

### ✅ **Fully Operational**
- **Service**: `clean-rag-frontend`
- **Port**: 3000 (via port-forward)
- **URL**: http://localhost:3000
- **Status**: Running and accessible

### 🔧 **Port-Forwarding Setup**
```bash
# Start RAG Playground port-forward
kubectl port-forward service/clean-rag-frontend 3000:3000

# Verify access
curl -s http://localhost:3000/ | head -5
```

### 📊 **Health Check**
```bash
# Check pod status
kubectl get pods -l app=rag-frontend

# Check service
kubectl get svc clean-rag-frontend

# Check logs
kubectl logs -l app=rag-frontend
```

## 🤖 AI-Q Research Assistant Status

### ✅ **Fully Operational**
- **Frontend**: `aiq-frontend`
- **Backend**: `aiq-aira-backend`
- **Proxy**: `aiq-aira-nginx`
- **Port**: 8051 (via port-forward)
- **URL**: http://localhost:8051
- **Status**: Running and accessible

### 🔧 **Port-Forwarding Setup**
```bash
# Start AI-Q Research Assistant port-forward
kubectl port-forward service/aiq-aira-nginx 8051:8051

# Verify access
curl -s http://localhost:8051/ | head -5
```

### 📊 **Health Check**
```bash
# Check all AI-Q components
kubectl get pods -l app.kubernetes.io/name=aiq-research-assistant

# Check services
kubectl get svc -l app.kubernetes.io/name=aiq-research-assistant

# Test API endpoints
curl -s http://localhost:8051/collections
curl -s http://localhost:8051/health
```

## 🏗️ System Architecture

### **RAG Playground Components**
```
┌─────────────────────────────────────────────────────────────────┐
│                    RAG Playground                                │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Frontend  │  │   Backend   │  │   Milvus    │            │
│  │  (Next.js)  │  │  (FastAPI)  │  │  Vector DB  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

### **AI-Q Research Assistant Components**
```
┌─────────────────────────────────────────────────────────────────┐
│                AI-Q Research Assistant                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Frontend  │  │   Backend    │  │   Nginx     │            │
│  │  (Next.js)  │  │  (FastAPI)   │  │  (Proxy)    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Milvus    │  │   NIM        │  │   Redis    │            │
│  │  Vector DB  │  │  (LLM)       │  │  (Cache)   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## 📋 Service Dependencies

### **RAG Playground Dependencies**
- **Milvus**: Vector database for embeddings
- **Redis**: Message queuing and caching
- **NVIDIA NIM**: LLM inference service
- **Ingestor Server**: Document processing

### **AI-Q Research Assistant Dependencies**
- **Milvus**: Vector database for embeddings
- **Redis**: Message queuing and caching
- **NVIDIA NIM**: LLM inference service (dedicated instance)
- **RAG Server**: Document retrieval service

## 🔍 Monitoring and Observability

### **Available Monitoring Tools**
- **Grafana**: http://MASTER_IP:30671 (admin/admin)
- **Jaeger**: http://MASTER_IP:30668
- **Zipkin**: http://MASTER_IP:30669
- **Attu (Milvus UI)**: http://MASTER_IP:30670

### **Health Check Commands**
```bash
# Overall cluster status
kubectl get nodes
kubectl get pods --all-namespaces

# RAG services
kubectl get pods -l app=rag-server
kubectl get pods -l app=rag-frontend
kubectl get pods -l app=milvus

# AI-Q services
kubectl get pods -l app=aiq-aira-backend
kubectl get pods -l app=aiq-aira-nginx
kubectl get pods -l app=aiq-frontend

# GPU services
kubectl get pods -n gpu-operator-resources
```

## 🚨 Troubleshooting

### **Common Issues**

#### Port-Forwarding Problems
```bash
# Check if ports are in use
lsof -i :3000
lsof -i :8051

# Kill existing port-forwards
pkill -f "kubectl port-forward"

# Restart port-forwards
kubectl port-forward service/clean-rag-frontend 3000:3000 &
kubectl port-forward service/aiq-aira-nginx 8051:8051 &
```

#### Service Not Responding
```bash
# Check pod status
kubectl get pods -l app=rag-frontend
kubectl get pods -l app=aiq-frontend

# Check logs
kubectl logs -l app=rag-frontend
kubectl logs -l app=aiq-frontend

# Restart services
kubectl rollout restart deployment/clean-rag-frontend
kubectl rollout restart deployment/aiq-frontend
```

#### Backend Connection Issues
```bash
# Check backend status
kubectl get pods -l app=aiq-aira-backend

# Check nginx proxy
kubectl get pods -l app=aiq-aira-nginx

# Check logs
kubectl logs -l app=aiq-aira-backend
kubectl logs -l app=aiq-aira-nginx
```

## 📊 Performance Metrics

### **Expected Performance**
- **RAG Query Latency**: < 1s (P95)
- **Document Ingestion**: < 5s per document
- **GPU Utilization**: 70-90%
- **Memory Usage**: < 80% of allocated resources

### **Resource Monitoring**
```bash
# Check resource usage
kubectl top nodes
kubectl top pods --all-namespaces

# Check GPU usage
kubectl describe node <gpu-node> | grep nvidia.com/gpu
```

## 🔄 Maintenance Tasks

### **Regular Health Checks**
```bash
# Daily health check script
#!/bin/bash
echo "=== RAG Playground Health Check ==="
kubectl get pods -l app=rag-frontend
curl -s http://localhost:3000/ | head -1

echo "=== AI-Q Research Assistant Health Check ==="
kubectl get pods -l app=aiq-frontend
curl -s http://localhost:8051/health

echo "=== Cluster Health Check ==="
kubectl get nodes
kubectl get pods --all-namespaces | grep -v Running
```

### **Backup Procedures**
```bash
# Backup cluster configuration
kubectl get all --all-namespaces -o yaml > backup-$(date +%Y%m%d).yaml

# Backup persistent data
kubectl get pvc --all-namespaces -o yaml > pvc-backup-$(date +%Y%m%d).yaml
```

## 📈 Scaling Considerations

### **Horizontal Scaling**
```bash
# Scale RAG frontend
kubectl scale deployment/clean-rag-frontend --replicas=3

# Scale AI-Q frontend
kubectl scale deployment/aiq-frontend --replicas=3
```

### **Resource Limits**
```bash
# Check current resource usage
kubectl top pods --all-namespaces

# Update resource limits
kubectl patch deployment/clean-rag-frontend -p '{"spec":{"template":{"spec":{"containers":[{"name":"rag-frontend","resources":{"limits":{"cpu":"1000m","memory":"2Gi"}}}]}}}}'
```

## 🆘 Emergency Procedures

### **Service Recovery**
```bash
# Restart all RAG services
kubectl rollout restart deployment/clean-rag-frontend
kubectl rollout restart deployment/rag-server

# Restart all AI-Q services
kubectl rollout restart deployment/aiq-frontend
kubectl rollout restart deployment/aiq-aira-backend
kubectl rollout restart deployment/aiq-aira-nginx
```

### **Complete System Reset**
```bash
# Delete all deployments (WARNING: Data loss)
kubectl delete deployment --all

# Restart cluster
sudo systemctl restart kubelet
```

## 📞 Support Information

### **Log Locations**
- **RAG Playground**: `kubectl logs -l app=rag-frontend`
- **AI-Q Frontend**: `kubectl logs -l app=aiq-frontend`
- **AI-Q Backend**: `kubectl logs -l app=aiq-aira-backend`
- **AI-Q Nginx**: `kubectl logs -l app=aiq-aira-nginx`

### **Configuration Files**
- **RAG Blueprint**: `playbooks/03-rag-blueprint.yml`
- **AI-Q Helm Chart**: `charts/aiq-research-assistant/`
- **Custom Config**: `aiq-custom-config.yaml`

### **Useful Commands**
```bash
# Get all services
kubectl get svc --all-namespaces

# Get all pods
kubectl get pods --all-namespaces

# Get all deployments
kubectl get deployment --all-namespaces

# Get all configmaps
kubectl get configmap --all-namespaces
```

---

**Last Updated**: $(date)
**Status**: All systems operational
**Next Review**: Weekly
