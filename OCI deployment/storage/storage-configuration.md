# Storage Configuration - OCI Deployment
## Complete Storage Setup and Data Management

### Storage Overview
The OCI deployment uses a hybrid storage architecture combining NFS-based shared storage (Hammerspace) for data ingestion, MinIO for object storage, and persistent volumes for application data.

### Primary Storage Systems

#### 1. Hammerspace NFS Storage
- **Server**: 150.136.225.57
- **Path**: /hub
- **Mount Point**: /mnt/anvil/hub
- **Protocol**: NFSv4.2
- **Purpose**: Source data storage and file ingestion

##### NFS Configuration
```yaml
# Persistent Volume for Hammerspace Hub
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

# Persistent Volume Claim
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

##### Mount Configuration
```bash
# Manual mount command
sudo mount -t nfs -o vers=4.2,proto=tcp 150.136.225.57:/hub /mnt/hub

# Mount options
- vers=4.2: Use NFS version 4.2
- hard: Hard mount (retry on failure)
- intr: Allow interruptible system calls
- proto=tcp: Use TCP protocol
```

#### 2. MinIO Object Storage
- **Image**: minio/minio:latest
- **Service**: minio (ClusterIP: 10.233.54.117)
- **Ports**: 9000 (API), 9001 (Console)
- **Purpose**: Object storage for Milvus and application data

##### MinIO Configuration
```yaml
# MinIO Deployment
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

# MinIO Service
apiVersion: v1
kind: Service
metadata:
  name: minio
spec:
  type: ClusterIP
  ports:
  - port: 9000
    targetPort: 9000
    protocol: TCP
  - port: 9001
    targetPort: 9001
    protocol: TCP
  selector:
    app: minio
```

#### 3. Milvus Vector Database Storage
- **Image**: milvusdb/milvus:v2.4.13
- **Service**: milvus (ClusterIP: 10.233.53.224)
- **Ports**: 19530 (API), 9091 (Metrics)
- **Purpose**: Vector storage and similarity search

##### Milvus Storage Configuration
```yaml
# Milvus Deployment
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
        volumeMounts:
        - name: milvus-data
          mountPath: /var/lib/milvus
      volumes:
      - name: milvus-data
        persistentVolumeClaim:
          claimName: milvus-pvc
```

### Data Flow Architecture

#### 1. Data Ingestion Flow
```
Source Files (/mnt/anvil/hub/case-*) 
    ↓
folder-ingest Jobs (scan directories)
    ↓
ingestor-server (process files)
    ↓
nv-ingest Services (create embeddings)
    ↓
Milvus (store vectors)
    ↓
MinIO (store objects)
```

#### 2. Query Flow
```
RAG Server (receive query)
    ↓
nemoretriever-embedding-ms (embed query)
    ↓
Milvus (vector similarity search)
    ↓
nemoretriever-reranking-ms (rerank results)
    ↓
RAG Server (generate response)
```

### Persistent Volume Configuration

#### Volume Types
- **NFS Volumes**: Hammerspace hub access
- **Local Volumes**: MinIO and Milvus data
- **EmptyDir**: Temporary processing data

#### Volume Claims
```yaml
# MinIO PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: minio-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi

# Milvus PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: milvus-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 200Gi
```

### Storage Performance Configuration

#### MinIO Optimization
```yaml
# MinIO Performance Settings
env:
- name: MINIO_CACHE_DRIVES
  value: "/tmp/cache"
- name: MINIO_CACHE_EXCLUDE
  value: "*.pdf,*.txt"
- name: MINIO_CACHE_QUOTA
  value: "80"
- name: MINIO_CACHE_AFTER
  value: "3"
- name: MINIO_CACHE_WATERMARK_LOW
  value: "70"
- name: MINIO_CACHE_WATERMARK_HIGH
  value: "90"
```

#### Milvus Storage Optimization
```yaml
# Milvus Storage Settings
env:
- name: MILVUS_DATA_PATH
  value: "/var/lib/milvus"
- name: MILVUS_LOG_LEVEL
  value: "INFO"
- name: MILVUS_CHANNEL_PREFIX
  value: "milvus"
```

### Backup and Recovery

#### Data Backup Strategy
1. **Source Data**: Hammerspace NFS (external backup)
2. **Vector Data**: Milvus snapshots
3. **Object Data**: MinIO backup
4. **Configuration**: Kubernetes manifests

#### Backup Commands
```bash
# Milvus backup
kubectl exec -it milvus-pod -- milvus-backup create --collection-name case_1000230

# MinIO backup
kubectl exec -it minio-pod -- mc mirror /data s3://backup-bucket/

# Configuration backup
kubectl get all -o yaml > cluster-backup.yaml
```

### Storage Monitoring

#### Key Metrics
- **NFS Mount Status**: Check mount availability
- **MinIO Usage**: Monitor object storage capacity
- **Milvus Performance**: Track vector operations
- **Disk Usage**: Monitor persistent volume usage

#### Monitoring Commands
```bash
# Check NFS mount
kubectl run nfs-check --rm -i --restart=Never --image=alpine -- mount | grep nfs

# Check MinIO status
kubectl exec -it minio-pod -- mc admin info local

# Check Milvus collections
kubectl exec -it milvus-pod -- milvus-cli collection list

# Check storage usage
kubectl top nodes
kubectl top pods
```

### Storage Troubleshooting

#### Common Issues
1. **NFS Mount Failures**
   - Check network connectivity to 150.136.225.57
   - Verify NFS server availability
   - Check mount options compatibility

2. **MinIO Connection Issues**
   - Verify MinIO service status
   - Check credentials configuration
   - Test bucket access permissions

3. **Milvus Storage Problems**
   - Check persistent volume status
   - Verify MinIO connectivity
   - Monitor disk space usage

#### Troubleshooting Commands
```bash
# Test NFS connectivity
kubectl run nfs-test --rm -i --restart=Never --image=alpine -- ping 150.136.225.57

# Test MinIO connectivity
kubectl run minio-test --rm -i --restart=Never --image=minio/mc -- mc ls minio

# Test Milvus connectivity
kubectl run milvus-test --rm -i --restart=Never --image=milvusdb/milvus -- milvus-cli collection list
```

### Storage Security

#### Access Control
- **NFS**: Network-based access control
- **MinIO**: Username/password authentication
- **Milvus**: Internal service authentication
- **Kubernetes**: RBAC-based access control

#### Security Configuration
```yaml
# MinIO Security
env:
- name: MINIO_ROOT_USER
  valueFrom:
    secretKeyRef:
      name: minio-credentials
      key: username
- name: MINIO_ROOT_PASSWORD
  valueFrom:
    secretKeyRef:
      name: minio-credentials
      key: password
```

### Storage Scaling

#### Horizontal Scaling
- **MinIO**: Multi-node cluster (not implemented)
- **Milvus**: Distributed deployment (not implemented)
- **NFS**: External scaling via Hammerspace

#### Vertical Scaling
- **MinIO**: Increase PVC size
- **Milvus**: Increase PVC size
- **NFS**: External capacity management

### Storage Best Practices

#### Performance Optimization
1. **Use appropriate access modes**: ReadWriteMany for shared data
2. **Optimize mount options**: Use hard mounts for reliability
3. **Monitor disk usage**: Prevent storage exhaustion
4. **Regular backups**: Maintain data integrity

#### Data Management
1. **Organize data by collections**: Use case-based naming
2. **Implement retention policies**: Clean up old data
3. **Monitor storage costs**: Optimize storage usage
4. **Test recovery procedures**: Ensure data recoverability

This storage configuration provides a robust, scalable storage foundation for the NVIDIA RAG Blueprint deployment with comprehensive data management and monitoring capabilities.
