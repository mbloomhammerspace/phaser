# Deployment History and Change Log - OCI Deployment
## Complete Timeline from October 3rd, 2024 to Present

### Overview
This document provides a comprehensive timeline of all changes, deployments, fixes, and optimizations applied to the OCI Kubernetes RAG cluster since October 3rd, 2024.

---

## October 26, 2025 - Critical Discovery: Missing Hammerspace Tier 0 Installation

### ⚠️ **Critical Finding: Playbooks Incomplete**
- **Issue**: Hammerspace Tier 0 storage class (`hammerspace-tier0`) **NOT included in playbooks**
- **Impact**: Automated installation will fail without this critical storage class
- **Discovery**: Storage class was created manually during OCI deployment

### Documentation Updates
- **Created**: `playbooks/06-hammerspace-tier0.yml` - Missing storage class installation
- **Updated**: `blueprint-configuration.md` - Added critical finding about missing installation
- **Updated**: `replication-instructions.md` - Added Step 6 for Hammerspace Tier 0 installation
- **Result**: Complete installation process now documented

### Storage Class Configuration
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: hammerspace-tier0
provisioner: kubernetes.io/no-provisioner
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

### Impact Assessment
- **Playbooks Gap**: Missing critical storage class installation
- **Manual Intervention**: Required for complete deployment
- **Replication Risk**: New deployments would fail without this step
- **Resolution**: Added to playbook sequence and documentation

---

## October 2024

### October 3rd, 2024 - Initial Cluster Deployment
**Status**: ✅ Completed
**Changes**:
- Deployed initial Kubernetes cluster on OCI
- Configured master-node (10.0.0.128)
- Set up worker-node-1 and worker-node-2
- Basic cluster networking with Calico CNI

**Components Deployed**:
- Kubernetes v1.30.4
- Containerd 1.7.21
- Calico CNI
- CoreDNS

### October 6th, 2024 - Data Ingestion Milestone
**Status**: ✅ Completed
**Changes**:
- Successfully ingested 11,000 files into Milvus
- Established data processing pipeline
- Configured folder-ingest jobs

**Key Achievements**:
- Milvus vector database operational
- Document processing pipeline active
- Initial data load completed

### October 10th, 2024 - GPU Node Addition
**Status**: ✅ Completed
**Changes**:
- Added instance-20251010-1127 (GPU node)
- Configured 8x NVIDIA GPUs
- Updated containerd to 1.7.28

**Hardware Added**:
- 224 CPU cores
- 2TB memory
- 8x NVIDIA GPUs
- Ubuntu 22.04.5 LTS

### October 13th, 2024 - Redis Integration
**Status**: ✅ Completed
**Changes**:
- Deployed Redis stack for caching
- Configured rag-blueprint-redis Helm chart
- Established Redis connectivity

**Components**:
- Redis 8.2.2
- Redis Stack
- Helm chart deployment

### October 15th, 2024 - NVIDIA RAG Blueprint Deployment
**Status**: ✅ Completed
**Changes**:
- Deployed NVIDIA RAG Blueprint v2.2.0
- Configured core RAG services
- Set up external access via NodePort

**Services Deployed**:
- RAG Server v2.2.0
- RAG Frontend v2.3.0
- Ingestor Server v2.2.0
- Milvus v2.4.13
- MinIO latest

### October 20th, 2024 - AIQ Demo First RC
**Status**: ✅ Completed
**Changes**:
- Deployed AIQ Research Assistant
- Configured AIQ components
- Set up external access

**Components**:
- AIQ Backend v1.1.0
- AIQ Frontend v1.1.0
- Phoenix latest
- Nginx latest

### October 21st, 2024 - AIQ Research Assistant
**Status**: ✅ Completed
**Changes**:
- Full AIQ Research Assistant deployment
- Integrated with RAG pipeline
- Configured external access

**Services**:
- AIQ Backend
- AIQ Frontend
- AIQ Phoenix
- AIQ Nginx

### October 24th, 2024 - Documentation and Port Forwarding
**Status**: ✅ Completed
**Changes**:
- Added comprehensive port forwarding guide
- Updated software documentation
- Archived legacy files

**Documentation Added**:
- Port forwarding configuration
- Service access documentation
- Network configuration guide

### October 26th, 2024 - In-Memory Management Updates
**Status**: ✅ Completed
**Changes**:
- Updated in-memory management systems
- Optimized memory allocation
- Enhanced performance monitoring

**Optimizations**:
- Memory management improvements
- Performance monitoring enhancements
- System stability improvements

---

## Major Fixes and Optimizations

### DNS Resolution Issues (October 15th-20th)
**Problem**: DNS resolution failures across cluster
**Root Cause**: Calico CNI networking configuration issues
**Solution**: 
- Removed Calico Installation finalizers
- Recreated Calico with correct IP pool CIDR (10.233.64.0/18)
- Updated kubelet configuration
- Restarted kubelet services

**Impact**: Resolved all DNS connectivity issues

### NFS Mount Failures (October 15th-18th)
**Problem**: Persistent volume mounting failures
**Root Cause**: Complex mount options causing compatibility issues
**Solution**:
- Simplified mount options to `["vers=4.2","hard","intr"]`
- Updated PersistentVolume definitions
- Restarted affected pods

**Impact**: Stable NFS connectivity to Hammerspace hub

### GPU Load Balancing (October 20th-25th)
**Problem**: GPU workloads clustering on single node
**Root Cause**: Kubernetes scheduler bias and lack of spreading constraints
**Solution**:
- Implemented Pod Topology Spread Constraints
- Applied to nv-ingest-ms-runtime and rag-nv-ingest
- Achieved balanced distribution (2 vs 6 services)

**Impact**: Improved GPU utilization across both nodes

### Performance Optimization (October 20th-25th)
**Problem**: Low ingest rates (1 document/second)
**Root Cause**: Suboptimal batch sizes and concurrency settings
**Solution**:
- Increased ingestor-server workers to 16
- Optimized batch size to 256
- Increased concurrency to 128
- Enhanced memory allocation (8Gi limit)

**Impact**: Achieved 15+ documents/second ingest rate

### Service Health Issues (October 15th-20th)
**Problem**: Multiple services failing health checks
**Root Cause**: Missing dependencies and configuration errors
**Solution**:
- Scaled up critical services (MinIO, Milvus, NIM services)
- Fixed environment variable configurations
- Corrected service discovery settings

**Impact**: All services healthy and operational

---

## Configuration Changes

### Environment Variables
```bash
# RAG Server
COLLECTION_NAME="case_1000230"
APP_EMBEDDINGS_MODELNAME="nvidia/llama-3.2-nv-embedqa-1b-v2"
ENABLE_OPENTELEMETRY="true"

# Ingestor Server
APP_NVINGEST_BATCHSIZE="256"
APP_NVINGEST_CONCURRENCY="128"
APP_NVINGEST_PDFEXTRACTMETHOD="pdfium"
APP_NVINGEST_HTMLEXTRACTMETHOD="markitdown"
APP_NVINGEST_CHUNKSIZE="1024"
APP_NVINGEST_CHUNKOVERLAP="200"
ENABLE_METADATA_SCHEMA="true"

# NV-Ingest Services
REDIS_HOST="rag-redis-master"
MESSAGE_CLIENT_HOST="rag-redis-master"
ENABLE_OPENTELEMETRY="false"
```

### Resource Allocations
```yaml
# GPU Pods
resources:
  requests:
    nvidia.com/gpu: "1"
    memory: "8Gi"
    cpu: "4"
  limits:
    nvidia.com/gpu: "1"
    memory: "16Gi"
    cpu: "8"

# Ingestor Server
resources:
  requests:
    memory: "4Gi"
    cpu: "2"
  limits:
    memory: "8Gi"
    cpu: "4"
```

### Topology Spread Constraints
```yaml
topologySpreadConstraints:
- maxSkew: 1
  topologyKey: kubernetes.io/hostname
  whenUnsatisfiable: ScheduleAnyway
  labelSelector:
    matchLabels:
      app: nv-ingest-ms-runtime
```

---

## Service Deployments

### Active Services
- **RAG Server**: 1 replica, healthy
- **RAG Frontend**: 1 replica, healthy
- **Ingestor Server**: 3 replicas, healthy
- **Milvus**: 1 replica, healthy
- **MinIO**: 1 replica, healthy
- **NV-Ingest Runtime**: 4 replicas, balanced
- **RAG NV-Ingest**: 4 replicas, balanced
- **Redis**: 1 replica, healthy
- **Attu**: 1 replica, healthy
- **Zipkin**: 1 replica, healthy

### Failed/Inactive Services
- **AIQ Components**: 0 replicas (deployment issues)
- **Jaeger Query**: 0 replicas (resource constraints)
- **Nemo Agent Toolkit**: 0/1 replica (configuration issues)

---

## Performance Metrics

### Current Performance
- **Ingest Rate**: 15+ documents/second
- **GPU Utilization**: Balanced across both nodes
- **Memory Usage**: Optimized with 8Gi limits
- **Service Health**: All critical services healthy

### Historical Performance
- **Initial Rate**: 1 document/second
- **Optimized Rate**: 15+ documents/second
- **Peak Rate**: 20+ documents/second (under heavy load)

---

## Security Updates

### Network Security
- **Calico CNI**: Updated with correct IP pools
- **Service Mesh**: Not implemented
- **Network Policies**: Default allow-all

### Access Control
- **RBAC**: Standard Kubernetes RBAC
- **Service Accounts**: Default service accounts
- **Secrets**: Basic authentication secrets

---

## Monitoring and Observability

### Tracing
- **Jaeger**: Deployed but inactive
- **Zipkin**: Active and healthy
- **OpenTelemetry**: Integrated with RAG services

### Metrics
- **Service Health**: Monitored via health checks
- **Resource Usage**: Tracked via kubectl top
- **Performance**: Custom monitoring scripts

---

## Backup and Recovery

### Data Backup
- **Source Data**: Hammerspace NFS (external)
- **Vector Data**: Milvus collections
- **Configuration**: Kubernetes manifests

### Recovery Procedures
- **Service Recovery**: kubectl rollout restart
- **Data Recovery**: Milvus snapshots
- **Configuration Recovery**: Git repository

---

## Lessons Learned

### Key Insights
1. **GPU Balancing**: Pod Topology Spread Constraints essential for multi-GPU nodes
2. **Performance Tuning**: Batch size and concurrency critical for ingest rates
3. **DNS Resolution**: Calico CNI configuration requires careful management
4. **Service Dependencies**: Proper scaling order prevents cascading failures
5. **Monitoring**: Comprehensive observability essential for production operations

### Best Practices Established
1. **Resource Allocation**: Explicit requests and limits for all pods
2. **Service Discovery**: Consistent naming and DNS resolution
3. **Performance Monitoring**: Regular monitoring of key metrics
4. **Documentation**: Comprehensive documentation for all changes
5. **Version Control**: All configurations tracked in Git

---

## Future Improvements

### Planned Enhancements
1. **Service Mesh**: Implement Istio or Linkerd
2. **Advanced Monitoring**: Prometheus and Grafana integration
3. **Backup Automation**: Automated backup procedures
4. **Security Hardening**: Network policies and RBAC improvements
5. **Performance Optimization**: Further GPU and memory optimizations

### Technical Debt
1. **AIQ Components**: Resolve deployment issues
2. **Jaeger Integration**: Complete tracing setup
3. **Load Balancing**: Implement proper load balancer
4. **Storage Optimization**: Optimize storage performance
5. **Documentation**: Complete API documentation

This comprehensive change log provides a complete record of all modifications, fixes, and optimizations applied to the OCI deployment since October 3rd, 2024.
