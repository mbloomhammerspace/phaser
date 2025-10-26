# Replication Instructions - OCI Deployment
## Complete Guide to Recreate the Kubernetes RAG Cluster

### Prerequisites

#### OCI Infrastructure Requirements
- **Master Node**: 1x instance (2 CPU, 16GB RAM)
- **GPU Worker Nodes**: 2x instances (224 CPU, 2TB RAM, 8x NVIDIA GPUs each)
- **Regular Worker Nodes**: 2x instances (2 CPU, 16GB RAM each)
- **Network**: VCN with proper security groups
- **Storage**: Access to Hammerspace NFS (150.136.225.57:/hub)

#### Software Requirements
- **Operating System**: Ubuntu 22.04.5 LTS or 24.04.2 LTS
- **Kubernetes**: v1.30.4
- **Container Runtime**: containerd 1.7.21+
- **NVIDIA Drivers**: Latest compatible drivers
- **Helm**: v3.x (optional)

---

## Step 1: Infrastructure Setup

### 1.1 Provision OCI Instances
```bash
# Master Node
Instance: master-node
OS: Ubuntu 24.04.2 LTS
CPU: 2 cores
Memory: 16GB
IP: 10.0.0.128

# GPU Worker Node 1
Instance: instance-20251003-1851
OS: Ubuntu 22.04.5 LTS
CPU: 224 cores
Memory: 2TB
GPU: 8x NVIDIA GPUs
IP: 10.0.0.25

# GPU Worker Node 2
Instance: instance-20251010-1127
OS: Ubuntu 22.04.5 LTS
CPU: 224 cores
Memory: 2TB
GPU: 8x NVIDIA GPUs
IP: 10.0.0.60

# Regular Worker Node 1
Instance: worker-node-1
OS: Ubuntu 24.04.2 LTS
CPU: 2 cores
Memory: 16GB
IP: 10.0.0.167

# Regular Worker Node 2
Instance: worker-node-2
OS: Ubuntu 24.04.2 LTS
CPU: 2 cores
Memory: 16GB
IP: 10.0.0.249
```

### 1.2 Configure Network Security
```bash
# Allow required ports
- 6443 (Kubernetes API)
- 2379-2380 (etcd)
- 10250 (kubelet)
- 10251 (kube-scheduler)
- 10252 (kube-controller-manager)
- 30000-32767 (NodePort services)
- 22 (SSH)
```

---

## Step 2: Kubernetes Installation

### 2.1 Install Kubernetes v1.30.4
```bash
# On all nodes
curl -fsSL https://pkgs.k8s.io/core-stable/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core-stable/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet=1.30.4-1.1 kubeadm=1.30.4-1.1 kubectl=1.30.4-1.1
sudo apt-mark hold kubelet kubeadm kubectl
```

### 2.2 Install Containerd
```bash
# On all nodes
sudo apt-get update
sudo apt-get install -y containerd
sudo mkdir -p /etc/containerd
sudo containerd config default | sudo tee /etc/containerd/config.toml
sudo systemctl restart containerd
sudo systemctl enable containerd
```

### 2.3 Initialize Master Node
```bash
# On master-node
sudo kubeadm init --pod-network-cidr=10.233.64.0/18 --service-cidr=10.233.0.0/16
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

### 2.4 Join Worker Nodes
```bash
# On each worker node (use token from master init)
sudo kubeadm join <master-ip>:6443 --token <token> --discovery-token-ca-cert-hash <hash>
```

---

## Step 3: CNI and Network Configuration

### 3.1 Install Calico CNI
```bash
# On master node
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.4/manifests/tigera-operator.yaml
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.4/manifests/custom-resources.yaml
```

### 3.2 Configure Calico IP Pool
```yaml
# calico-ip-pool.yaml
apiVersion: projectcalico.org/v3
kind: IPPool
metadata:
  name: default-ipv4-ippool
spec:
  blockSize: 26
  cidr: 10.233.64.0/18
  ipipMode: Never
  natOutgoing: true
  nodeSelector: all()
```

```bash
kubectl apply -f calico-ip-pool.yaml
```

---

## Step 4: GPU Setup

### 4.1 Install NVIDIA Drivers
```bash
# On GPU nodes
sudo apt-get update
sudo apt-get install -y nvidia-driver-535
sudo reboot
```

### 4.2 Install NVIDIA Container Runtime
```bash
# On GPU nodes
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart containerd
```

### 4.3 Install NVIDIA Device Plugin
```bash
# On master node
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.1/deployments/static/nvidia-device-plugin.yml
```

---

## Step 5: Storage Configuration

### 5.1 Create NFS Persistent Volume
```yaml
# hammerspace-hub-pv.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: hammerspace-hub-pv
spec:
  capacity:
    storage: 200Gi
  accessModes:
    - ReadWriteMany
  nfs:
    server: 150.136.225.57
    path: /hub
  mountOptions:
    - vers=4.2
    - hard
    - intr
  persistentVolumeReclaimPolicy: Retain
```

```bash
kubectl apply -f hammerspace-hub-pv.yaml
```

### 5.2 Create Persistent Volume Claim
```yaml
# hammerspace-hub-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: hammerspace-hub-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 200Gi
```

```bash
kubectl apply -f hammerspace-hub-pvc.yaml
```

---

## Step 6: Core Services Deployment

### 6.1 Deploy MinIO
```yaml
# minio-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: minio
spec:
  replicas: 1
  selector:
    matchLabels:
      app: minio
  template:
    spec:
      containers:
      - name: minio
        image: minio/minio:latest
        command: ["minio", "server", "/data", "--console-address", ":9001"]
        env:
        - name: MINIO_ROOT_USER
          value: "minioadmin"
        - name: MINIO_ROOT_PASSWORD
          value: "minioadmin"
        ports:
        - containerPort: 9000
        - containerPort: 9001
        volumeMounts:
        - name: minio-data
          mountPath: /data
      volumes:
      - name: minio-data
        persistentVolumeClaim:
          claimName: minio-pvc
```

### 6.2 Deploy Milvus
```yaml
# milvus-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: milvus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: milvus
  template:
    spec:
      containers:
      - name: milvus
        image: milvusdb/milvus:v2.4.13
        env:
        - name: ETCD_ENDPOINTS
          value: "etcd:2379"
        - name: MINIO_ADDRESS
          value: "minio:9000"
        - name: MINIO_ACCESS_KEY
          value: "minioadmin"
        - name: MINIO_SECRET_KEY
          value: "minioadmin"
        ports:
        - containerPort: 19530
        - containerPort: 9091
```

### 6.3 Deploy Redis
```yaml
# redis-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-redis-master
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rag-redis-master
  template:
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
```

---

## Step 7: NVIDIA RAG Blueprint Deployment

### 7.1 Deploy RAG Server
```yaml
# rag-server-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rag-server
  template:
    spec:
      containers:
      - name: rag-server
        image: nvcr.io/nvidia/blueprint/rag-server:2.2.0
        env:
        - name: COLLECTION_NAME
          value: "case_1000230"
        - name: APP_EMBEDDINGS_MODELNAME
          value: "nvidia/llama-3.2-nv-embedqa-1b-v2"
        - name: ENABLE_OPENTELEMETRY
          value: "true"
        ports:
        - containerPort: 8081
```

### 7.2 Deploy RAG Frontend
```yaml
# rag-frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: clean-rag-frontend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: clean-rag-frontend
  template:
    spec:
      containers:
      - name: rag-frontend
        image: nvcr.io/nvidia/blueprint/rag-frontend:2.3.0
        ports:
        - containerPort: 3000
```

### 7.3 Deploy Ingestor Server
```yaml
# ingestor-server-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ingestor-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ingestor-server
  template:
    spec:
      containers:
      - name: ingestor-server
        image: nvcr.io/nvidia/blueprint/ingestor-server:2.2.0
        command: ["uvicorn", "nvidia_rag.ingestor_server.server:app", "--port", "8082", "--host", "0.0.0.0", "--workers", "16"]
        env:
        - name: APP_NVINGEST_BATCHSIZE
          value: "256"
        - name: APP_NVINGEST_CONCURRENCY
          value: "128"
        - name: APP_NVINGEST_PDFEXTRACTMETHOD
          value: "pdfium"
        - name: APP_NVINGEST_HTMLEXTRACTMETHOD
          value: "markitdown"
        - name: APP_NVINGEST_CHUNKSIZE
          value: "1024"
        - name: APP_NVINGEST_CHUNKOVERLAP
          value: "200"
        - name: ENABLE_METADATA_SCHEMA
          value: "true"
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
        ports:
        - containerPort: 8082
```

---

## Step 8: NVIDIA Inference Microservices

### 8.1 Deploy Embedding Service
```yaml
# embedding-ms-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nemoretriever-embedding-ms
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nemoretriever-embedding-ms
  template:
    spec:
      containers:
      - name: embedding-nim
        image: nvcr.io/nim/nvidia/llama-3.2-nv-embedqa-1b-v2:1.6.0
        resources:
          requests:
            nvidia.com/gpu: "1"
          limits:
            nvidia.com/gpu: "1"
        ports:
        - containerPort: 8000
```

### 8.2 Deploy Reranking Service
```yaml
# reranking-ms-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nemoretriever-reranking-ms
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nemoretriever-reranking-ms
  template:
    spec:
      containers:
      - name: reranking-nim
        image: nvcr.io/nim/nvidia/llama-3.2-nv-rerankqa-1b-v2:1.5.0
        resources:
          requests:
            nvidia.com/gpu: "1"
          limits:
            nvidia.com/gpu: "1"
        ports:
        - containerPort: 8000
```

---

## Step 9: NV-Ingest Services with GPU Balancing

### 9.1 Deploy NV-Ingest Runtime
```yaml
# nv-ingest-runtime-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nv-ingest-ms-runtime
spec:
  replicas: 4
  selector:
    matchLabels:
      app: nv-ingest-ms-runtime
  template:
    spec:
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: kubernetes.io/hostname
        whenUnsatisfiable: ScheduleAnyway
        labelSelector:
          matchLabels:
            app: nv-ingest-ms-runtime
      containers:
      - name: nv-ingest
        image: nvcr.io/nvidia/nemo-microservices/nv-ingest:25.6.2
        resources:
          requests:
            nvidia.com/gpu: "1"
            memory: "8Gi"
            cpu: "4"
          limits:
            nvidia.com/gpu: "1"
            memory: "16Gi"
            cpu: "8"
        env:
        - name: ENABLE_OPENTELEMETRY
          value: "false"
        ports:
        - containerPort: 7670
        - containerPort: 7671
```

### 9.2 Deploy RAG NV-Ingest
```yaml
# rag-nv-ingest-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-nv-ingest
spec:
  replicas: 4
  selector:
    matchLabels:
      app: rag-nv-ingest
  template:
    spec:
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: kubernetes.io/hostname
        whenUnsatisfiable: ScheduleAnyway
        labelSelector:
          matchLabels:
            app: rag-nv-ingest
      containers:
      - name: nv-ingest
        image: nvcr.io/nvidia/nemo-microservices/nv-ingest:25.6.2
        resources:
          requests:
            nvidia.com/gpu: "1"
            memory: "8Gi"
            cpu: "4"
          limits:
            nvidia.com/gpu: "1"
            memory: "16Gi"
            cpu: "8"
        env:
        - name: REDIS_HOST
          value: "rag-redis-master"
        - name: MESSAGE_CLIENT_HOST
          value: "rag-redis-master"
        - name: ENABLE_OPENTELEMETRY
          value: "false"
        ports:
        - containerPort: 7670
```

---

## Step 10: External Access Configuration

### 10.1 Create NodePort Services
```yaml
# external-services.yaml
apiVersion: v1
kind: Service
metadata:
  name: rag-server-nodeport
spec:
  type: NodePort
  ports:
  - port: 8081
    targetPort: 8081
    nodePort: 30081
  selector:
    app: rag-server

---
apiVersion: v1
kind: Service
metadata:
  name: milvus-external
spec:
  type: NodePort
  ports:
  - port: 19530
    targetPort: 19530
    nodePort: 30196
  - port: 9091
    targetPort: 9091
    nodePort: 30992
  selector:
    app: milvus

---
apiVersion: v1
kind: Service
metadata:
  name: attu
spec:
  type: NodePort
  ports:
  - port: 3001
    targetPort: 3001
    nodePort: 30082
  selector:
    app: attu
```

---

## Step 11: Observability Stack

### 11.1 Deploy Zipkin
```yaml
# zipkin-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zipkin
spec:
  replicas: 1
  selector:
    matchLabels:
      app: zipkin
  template:
    spec:
      containers:
      - name: zipkin
        image: openzipkin/zipkin:latest
        ports:
        - containerPort: 9411
```

### 11.2 Deploy OpenTelemetry Collector
```yaml
# otel-collector-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-opentelemetry-collector
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rag-opentelemetry-collector
  template:
    spec:
      containers:
      - name: otel-collector
        image: otel/opentelemetry-collector-contrib:latest
        ports:
        - containerPort: 4317
        - containerPort: 4318
```

---

## Step 12: Verification and Testing

### 12.1 Verify Cluster Status
```bash
# Check node status
kubectl get nodes -o wide

# Check pod status
kubectl get pods -o wide

# Check services
kubectl get services -o wide

# Check GPU resources
kubectl describe nodes | grep -A 5 "Capacity:"
```

### 12.2 Test Service Connectivity
```bash
# Test RAG server
curl http://<master-ip>:30081/health

# Test Milvus
curl http://<master-ip>:30196/health

# Test Attu
curl http://<master-ip>:30082
```

### 12.3 Test GPU Functionality
```bash
# Check GPU allocation
kubectl get pods -o wide | grep nv-ingest

# Test GPU workload
kubectl run gpu-test --rm -i --restart=Never --image=nvidia/cuda:11.8-base-ubuntu20.04 -- nvidia-smi
```

---

## Step 13: Data Ingestion Setup

### 13.1 Create Test Collection
```bash
# Create collection in Milvus
kubectl run milvus-client --rm -i --restart=Never --image=milvusdb/milvus -- milvus-cli collection create --collection-name case_1000230
```

### 13.2 Test File Ingestion
```bash
# Create test folder-ingest job
kubectl create job test-ingest --image=alpine:3.19 -- sh -c "
apk add --no-cache curl
curl -X POST http://ingestor-server:8082/collection -H 'Content-Type: application/json' -d '{\"collection_name\":\"case_1000230\"}'
echo 'Collection created successfully'
"
```

---

## Troubleshooting

### Common Issues
1. **DNS Resolution**: Check Calico CNI configuration
2. **NFS Mount**: Verify Hammerspace connectivity
3. **GPU Allocation**: Check NVIDIA device plugin
4. **Service Health**: Verify all dependencies are running

### Debug Commands
```bash
# Check cluster status
kubectl cluster-info

# Check pod logs
kubectl logs <pod-name>

# Check service endpoints
kubectl get endpoints

# Check resource usage
kubectl top nodes
kubectl top pods
```

---

## Post-Deployment Configuration

### Performance Optimization
1. **GPU Balancing**: Monitor pod distribution
2. **Resource Tuning**: Adjust memory and CPU limits
3. **Batch Optimization**: Tune batch sizes for optimal performance
4. **Monitoring**: Set up comprehensive monitoring

### Security Hardening
1. **Network Policies**: Implement network segmentation
2. **RBAC**: Configure proper role-based access control
3. **Secrets Management**: Use Kubernetes secrets for sensitive data
4. **Image Security**: Scan container images for vulnerabilities

This comprehensive replication guide provides all the necessary steps to recreate the OCI Kubernetes RAG cluster with the exact same configuration and performance characteristics.
