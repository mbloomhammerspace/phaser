# Network Configuration - OCI Deployment
## Complete Network Setup and Service Access

### Network Overview
The OCI deployment uses a multi-tier network architecture with internal cluster networking, external access points, and specialized service routing for the RAG pipeline.

### Cluster Network Configuration

#### Core Network Settings
- **Cluster CIDR**: 10.233.0.0/16
- **Service CIDR**: 10.233.0.0/16
- **Pod CIDR**: 10.233.64.0/18 (Calico)
- **CNI**: Calico
- **DNS**: CoreDNS with nodelocaldns

#### Node Network Configuration
| Node | Internal IP | External Access | Role |
|------|-------------|-----------------|------|
| master-node | 10.0.0.128 | Control Plane | Kubernetes API |
| instance-20251003-1851 | 10.0.0.25 | GPU Worker | Primary GPU Node |
| instance-20251010-1127 | 10.0.0.60 | GPU Worker | Secondary GPU Node |
| worker-node-1 | 10.0.0.167 | Regular Worker | Cordoned |
| worker-node-2 | 10.0.0.249 | Regular Worker | Cordoned |

### Service Network Configuration

#### Core RAG Services
```yaml
# RAG Server Service
rag-server:
  type: ClusterIP
  clusterIP: 10.233.34.93
  ports:
    - port: 8081
      targetPort: 8081
      protocol: TCP

# RAG Server External Access
rag-server-nodeport:
  type: NodePort
  clusterIP: 10.233.42.149
  ports:
    - port: 8081
      targetPort: 8081
      nodePort: 30081
      protocol: TCP

# RAG Frontend Service
clean-rag-frontend:
  type: ClusterIP
  clusterIP: 10.233.26.90
  ports:
    - port: 3000
      targetPort: 3000
      protocol: TCP
```

#### Vector Database Services
```yaml
# Milvus Core Service
milvus:
  type: ClusterIP
  clusterIP: 10.233.53.224
  ports:
    - port: 19530
      targetPort: 19530
      protocol: TCP
    - port: 9091
      targetPort: 9091
      protocol: TCP

# Milvus External Access
milvus-external:
  type: NodePort
  clusterIP: 10.233.37.133
  ports:
    - port: 19530
      targetPort: 19530
      nodePort: 30196
      protocol: TCP
    - port: 9091
      targetPort: 9091
      nodePort: 30992
      protocol: TCP

# Attu Management UI
attu:
  type: NodePort
  clusterIP: 10.233.9.227
  ports:
    - port: 3001
      targetPort: 3001
      nodePort: 30082
      protocol: TCP
```

#### AI/ML Services
```yaml
# NVIDIA Inference Microservices
nemoretriever-embedding-ms:
  type: ClusterIP
  clusterIP: 10.233.14.87
  ports:
    - port: 8000
      targetPort: 8000
      protocol: TCP

nemoretriever-reranking-ms:
  type: ClusterIP
  clusterIP: 10.233.18.82
  ports:
    - port: 8000
      targetPort: 8000
      protocol: TCP

# NV-Ingest Services
nv-ingest-ms-runtime:
  type: ClusterIP
  clusterIP: 10.233.40.241
  ports:
    - port: 7670
      targetPort: 7670
      protocol: TCP
    - port: 7671
      targetPort: 7671
      protocol: TCP

rag-nv-ingest:
  type: ClusterIP
  clusterIP: 10.233.18.9
  ports:
    - port: 7670
      targetPort: 7670
      protocol: TCP
```

#### Storage Services
```yaml
# MinIO Object Storage
minio:
  type: ClusterIP
  clusterIP: 10.233.54.117
  ports:
    - port: 9000
      targetPort: 9000
      protocol: TCP
    - port: 9001
      targetPort: 9001
      protocol: TCP

# Redis Cache
rag-redis-master:
  type: ClusterIP
  clusterIP: 10.233.59.49
  ports:
    - port: 6379
      targetPort: 6379
      protocol: TCP

redis:
  type: ClusterIP
  clusterIP: 10.233.32.174
  ports:
    - port: 6379
      targetPort: 6379
      protocol: TCP
```

#### Observability Services
```yaml
# Jaeger Tracing
jaeger-query:
  type: NodePort
  clusterIP: 10.233.58.187
  ports:
    - port: 16686
      targetPort: 16686
      nodePort: 30670
      protocol: TCP

# Zipkin Tracing
zipkin:
  type: NodePort
  clusterIP: 10.233.30.181
  ports:
    - port: 9411
      targetPort: 9411
      nodePort: 30669
      protocol: TCP

# OpenTelemetry Collector
rag-opentelemetry-collector:
  type: ClusterIP
  clusterIP: 10.233.31.84
  ports:
    - port: 4317
      targetPort: 4317
      protocol: TCP
    - port: 4318
      targetPort: 4318
      protocol: TCP
```

### External Access Configuration

#### Primary Access Points
- **RAG Pipeline**: http://10.0.0.236:8081/v1/generate (jumphost)
- **RAG Frontend**: http://<master-ip>:30080
- **Milvus**: http://<master-ip>:30196
- **Attu**: http://<master-ip>:30082
- **Jaeger**: http://<master-ip>:30670
- **Zipkin**: http://<master-ip>:30669

#### Port Forward Configuration
```bash
# Jumphost Port Forward (10.0.0.236)
kubectl port-forward --address 0.0.0.0 rag-server-59578bdf68-f6gnr 8081:8081

# Local Port Forwards
kubectl port-forward svc/rag-server 8081:8081
kubectl port-forward svc/milvus-external 19530:19530
kubectl port-forward svc/attu 3001:3001
```

### DNS Configuration

#### CoreDNS Configuration
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: coredns
  namespace: kube-system
data:
  Corefile: |
    .:53 {
        errors
        health {
           lameduck 5s
        }
        ready
        kubernetes cluster.local in-addr.arpa ip6.arpa {
           pods insecure
           fallthrough in-addr.arpa ip6.arpa
           ttl 30
        }
        prometheus :9153
        forward . /etc/resolv.conf {
           max_concurrent 1000
        }
        cache 30
        loop
        reload
        loadbalance
    }
```

#### Service Discovery
- **Internal Services**: Resolved via Kubernetes DNS
- **External Services**: Forwarded to upstream DNS
- **Service Mesh**: None (direct service-to-service communication)

### Network Policies

#### Calico CNI Configuration
```yaml
apiVersion: projectcalico.org/v3
kind: Installation
metadata:
  name: default
spec:
  calicoNetwork:
    ipPools:
    - blockSize: 26
      cidr: 10.233.64.0/18
      encapsulation: VXLANCrossSubnet
      natOutgoing: true
      nodeSelector: all()
```

#### Network Security
- **Pod-to-Pod Communication**: Allowed within cluster
- **External Access**: Controlled via NodePort services
- **Service Mesh**: Not implemented
- **Network Policies**: Default allow-all (no restrictions)

### Load Balancing

#### Service Load Balancing
- **Internal**: Kubernetes service load balancing
- **External**: NodePort with manual load balancing
- **Ingress**: Not configured
- **Load Balancer**: MetalLB not deployed

#### Traffic Distribution
- **RAG Requests**: Distributed across ingestor-server replicas
- **GPU Workloads**: Balanced via Pod Topology Spread Constraints
- **Storage Access**: Direct service-to-service communication

### Network Performance

#### Bandwidth Configuration
- **Internal Cluster**: High-bandwidth internal networking
- **External Access**: Limited by NodePort configuration
- **Storage Network**: NFS over dedicated network path

#### Latency Optimization
- **Service Locality**: Pods scheduled near required services
- **DNS Caching**: CoreDNS with 30-second TTL
- **Connection Pooling**: Redis connection pooling enabled

### Troubleshooting Network Issues

#### Common Network Problems
1. **DNS Resolution Failures**
   - Check CoreDNS pod status
   - Verify nodelocaldns configuration
   - Test upstream DNS resolution

2. **Service Connectivity Issues**
   - Verify service endpoints
   - Check pod network policies
   - Test service-to-service communication

3. **External Access Problems**
   - Verify NodePort configuration
   - Check firewall rules
   - Test port forwarding

#### Network Debugging Commands
```bash
# Check service endpoints
kubectl get endpoints

# Test DNS resolution
kubectl run test-dns --rm -i --restart=Never --image=busybox -- nslookup rag-server

# Test service connectivity
kubectl run test-connectivity --rm -i --restart=Never --image=busybox -- wget -qO- http://rag-server:8081/health

# Check network policies
kubectl get networkpolicies
```

### Network Monitoring

#### Service Health Checks
- **RAG Server**: HTTP health checks on port 8081
- **Milvus**: TCP health checks on port 19530
- **MinIO**: HTTP health checks on port 9000
- **Redis**: TCP health checks on port 6379

#### Network Metrics
- **Service Response Times**: Monitored via OpenTelemetry
- **DNS Resolution Times**: Tracked via CoreDNS metrics
- **Network Throughput**: Monitored at node level

This network configuration provides a robust, scalable networking foundation for the NVIDIA RAG Blueprint deployment with comprehensive external access and internal service communication.
