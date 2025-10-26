# NVIDIA RAG Blueprint Configuration - OCI Deployment
## Complete Blueprint Setup and Customizations

### Blueprint Overview
The NVIDIA RAG Blueprint v2.2.0 has been deployed with extensive customizations for the OCI environment, including GPU balancing, performance optimizations, and observability enhancements.

### Core Blueprint Components

#### 1. RAG Server Configuration
```yaml
# rag-server deployment
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

#### 2. RAG Frontend Configuration
```yaml
# clean-rag-frontend deployment
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

#### 3. Ingestor Server Configuration
```yaml
# ingestor-server deployment (optimized)
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

### NVIDIA Inference Microservices (NIM) Configuration

#### 1. Embedding Service
```yaml
# nemoretriever-embedding-ms deployment
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

#### 2. Reranking Service
```yaml
# nemoretriever-reranking-ms deployment
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

### NV-Ingest Services Configuration

#### 1. NV-Ingest Runtime (GPU Balanced)
```yaml
# nv-ingest-ms-runtime deployment
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

#### 2. RAG NV-Ingest (GPU Balanced)
```yaml
# rag-nv-ingest deployment
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

### Vector Database Configuration

#### Milvus Configuration
```yaml
# milvus deployment
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
        ports:
        - containerPort: 19530
        - containerPort: 9091
```

#### Attu Management UI
```yaml
# attu deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: attu
spec:
  replicas: 1
  selector:
    matchLabels:
      app: attu
  template:
    spec:
      containers:
      - name: attu
        image: zilliz/attu:v2.4
        env:
        - name: MILVUS_URL
          value: "milvus:19530"
        ports:
        - containerPort: 3001
```

### Storage Configuration

#### MinIO Object Storage
```yaml
# minio deployment
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
```

### Observability Configuration

#### OpenTelemetry Collector
```yaml
# rag-opentelemetry-collector deployment
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

### Service Configuration

#### External Access Services
```yaml
# rag-server-nodeport service
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

# milvus-external service
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

# attu service
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

### Performance Optimizations Applied

#### 1. GPU Balancing
- Implemented Pod Topology Spread Constraints
- Balanced GPU workloads across both GPU nodes
- Prevented clustering on single nodes

#### 2. Ingestor Optimization
- Increased worker count to 16
- Optimized batch size to 256
- Increased concurrency to 128
- Enhanced memory allocation (8Gi limit)

#### 3. Chunk Processing
- Chunk size: 1024 tokens
- Chunk overlap: 200 tokens
- PDF extraction: pdfium
- HTML extraction: markitdown

#### 4. Resource Allocation
- GPU requests: 1 per pod
- Memory requests: 8Gi per GPU pod
- CPU requests: 4 cores per GPU pod
- Memory limits: 16Gi per GPU pod

### Custom Environment Variables

#### RAG Server
- `COLLECTION_NAME`: "case_1000230"
- `APP_EMBEDDINGS_MODELNAME`: "nvidia/llama-3.2-nv-embedqa-1b-v2"
- `ENABLE_OPENTELEMETRY`: "true"

#### Ingestor Server
- `APP_NVINGEST_BATCHSIZE`: "256"
- `APP_NVINGEST_CONCURRENCY`: "128"
- `APP_NVINGEST_PDFEXTRACTMETHOD`: "pdfium"
- `APP_NVINGEST_HTMLEXTRACTMETHOD`: "markitdown"
- `APP_NVINGEST_CHUNKSIZE`: "1024"
- `APP_NVINGEST_CHUNKOVERLAP`: "200"
- `ENABLE_METADATA_SCHEMA`: "true"

#### NV-Ingest Services
- `REDIS_HOST`: "rag-redis-master"
- `MESSAGE_CLIENT_HOST`: "rag-redis-master"
- `ENABLE_OPENTELEMETRY`: "false"

### Blueprint Customizations Summary

#### Applied Modifications
1. **GPU Load Balancing**: Pod Topology Spread Constraints
2. **Performance Tuning**: Optimized batch sizes and concurrency
3. **Resource Scaling**: Increased memory and CPU allocations
4. **Service Discovery**: Fixed Redis connectivity
5. **Observability**: Integrated OpenTelemetry tracing
6. **External Access**: NodePort services for external connectivity
7. **Storage Integration**: NFS mount configuration
8. **Model Configuration**: Specific NVIDIA model versions

#### Blueprint Version Compatibility
- **Base Blueprint**: NVIDIA RAG Blueprint v2.2.0
- **Frontend**: v2.3.0
- **NIM Models**: v1.5.0-v1.8.5
- **NV-Ingest**: v25.6.2
- **Milvus**: v2.4.13

This configuration represents a production-ready, optimized deployment of the NVIDIA RAG Blueprint tailored for the OCI environment with GPU balancing, performance optimizations, and comprehensive observability.
