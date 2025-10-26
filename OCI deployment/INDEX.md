# OCI Deployment Documentation Index
## Complete Documentation Package for Kubernetes RAG Cluster

### Overview
This documentation package provides comprehensive information for recreating and managing the OCI-based Kubernetes RAG cluster deployed since October 3rd, 2024. The cluster runs NVIDIA's RAG Blueprint with GPU-accelerated AI workloads, vector database (Milvus), and document processing pipelines.

---

## 📋 Documentation Structure

### 1. [README.md](./README.md)
**Main Overview Document**
- Cluster architecture summary
- Hardware specifications overview
- Software stack summary
- Network configuration overview
- Storage configuration overview
- Deployment history summary
- Replication instructions overview
- Monitoring and maintenance guidelines

### 2. [hardware/instance-specifications.md](./hardware/instance-specifications.md)
**Detailed Hardware Information**
- Complete instance specifications
- Node-by-node hardware details
- Resource allocation summary
- Network configuration per node
- Performance characteristics
- Maintenance notes

### 3. [software/software-versions.md](./software/software-versions.md)
**Complete Software Inventory**
- Core infrastructure versions
- NVIDIA RAG Blueprint components
- AI/ML model versions
- Container image inventory
- Service versions and compatibility
- Deployment status overview

### 4. [blueprint/blueprint-configuration.md](./blueprint/blueprint-configuration.md)
**NVIDIA RAG Blueprint Configuration**
- Complete blueprint setup
- Custom configurations applied
- Performance optimizations
- GPU balancing implementation
- Environment variables
- Service configurations

### 5. [network/network-configuration.md](./network/network-configuration.md)
**Network Architecture and Configuration**
- Cluster network setup
- Service network configuration
- External access points
- DNS configuration
- Load balancing setup
- Network troubleshooting

### 6. [storage/storage-configuration.md](./storage/storage-configuration.md)
**Storage Systems and Data Management**
- NFS storage configuration
- MinIO object storage setup
- Milvus vector database storage
- Data flow architecture
- Backup and recovery procedures
- Storage monitoring

### 7. [deployment-history.md](./deployment-history.md)
**Complete Change Log and Timeline**
- Detailed deployment timeline
- Major fixes and optimizations
- Configuration changes
- Performance metrics
- Security updates
- Lessons learned

### 8. [performance-analysis-results.md](./performance-analysis-results.md)
**Final Performance Assessment**
- Performance script execution results
- Current cluster status and metrics
- Processing performance data
- Optimization validation
- Performance comparison (before/after)
- Key performance indicators
- Recommendations for future monitoring

### 9. [hammerspace-tier0-critical-finding.md](./hammerspace-tier0-critical-finding.md)
**Critical Discovery: Missing Hammerspace Tier 0 Installation**
- Playbook gap analysis
- Missing storage class installation
- Resolution and prevention measures
- Verification steps and lessons learned

### 10. [replication-instructions.md](./replication-instructions.md)
**Step-by-Step Replication Guide**
- Prerequisites and requirements
- Infrastructure setup
- Kubernetes installation
- Service deployment
- Configuration verification
- Troubleshooting guide

---

## 🎯 Quick Reference

### Cluster Summary
- **Total Nodes**: 5 (1 master, 2 GPU workers, 2 regular workers)
- **Total GPUs**: 16x NVIDIA GPUs
- **Total CPU**: 454 cores
- **Total Memory**: ~4TB
- **Kubernetes Version**: v1.30.4
- **RAG Blueprint**: v2.2.0-v2.3.0

### Key Access Points
- **RAG Pipeline**: http://10.0.0.236:8081/v1/generate
- **RAG Frontend**: http://<master-ip>:30080
- **Milvus**: http://<master-ip>:30196
- **Attu**: http://<master-ip>:30082
- **Jaeger**: http://<master-ip>:30670
- **Zipkin**: http://<master-ip>:30669

### Performance Metrics
- **Ingest Rate**: 15+ documents/second
- **GPU Utilization**: Balanced across nodes
- **Service Health**: All critical services operational
- **Storage**: NFS + MinIO + Milvus

---

## 🔧 Key Configurations

### GPU Balancing
```yaml
topologySpreadConstraints:
- maxSkew: 1
  topologyKey: kubernetes.io/hostname
  whenUnsatisfiable: ScheduleAnyway
  labelSelector:
    matchLabels:
      app: nv-ingest-ms-runtime
```

### Performance Optimization
```bash
# Ingestor Server
APP_NVINGEST_BATCHSIZE="256"
APP_NVINGEST_CONCURRENCY="128"
APP_NVINGEST_CHUNKSIZE="1024"
APP_NVINGEST_CHUNKOVERLAP="200"
```

### Resource Allocation
```yaml
resources:
  requests:
    nvidia.com/gpu: "1"
    memory: "8Gi"
    cpu: "4"
  limits:
    nvidia.com/gpu: "1"
    memory: "16Gi"
    cpu: "8"
```

---

## 📊 Service Status

### Active Services
- ✅ RAG Server (1 replica)
- ✅ RAG Frontend (1 replica)
- ✅ Ingestor Server (3 replicas)
- ✅ Milvus (1 replica)
- ✅ MinIO (1 replica)
- ✅ NV-Ingest Runtime (4 replicas, balanced)
- ✅ RAG NV-Ingest (4 replicas, balanced)
- ✅ Redis (1 replica)
- ✅ Attu (1 replica)
- ✅ Zipkin (1 replica)

### Failed/Inactive Services
- ❌ AIQ Components (deployment issues)
- ❌ Jaeger Query (resource constraints)
- ❌ Nemo Agent Toolkit (configuration issues)

---

## 🚀 Deployment Commands

### Quick Start
```bash
# Apply all configurations
kubectl apply -f hardware/
kubectl apply -f software/
kubectl apply -f blueprint/
kubectl apply -f network/
kubectl apply -f storage/

# Verify deployment
kubectl get pods -o wide
kubectl get services -o wide
kubectl top nodes
```

### Health Checks
```bash
# Check service health
kubectl get pods | grep -E "(rag|milvus|ingest|nv)"

# Test connectivity
curl http://<master-ip>:30081/health
curl http://<master-ip>:30196/health

# Check GPU allocation
kubectl describe nodes | grep -A 5 "Capacity:"
```

---

## 🔍 Troubleshooting

### Common Issues
1. **DNS Resolution**: Check Calico CNI configuration
2. **NFS Mount**: Verify Hammerspace connectivity
3. **GPU Imbalance**: Use Pod Topology Spread Constraints
4. **Performance**: Monitor ingestor-server scaling

### Debug Commands
```bash
# Cluster status
kubectl cluster-info
kubectl get nodes -o wide

# Service logs
kubectl logs <pod-name> --tail=100

# Resource usage
kubectl top nodes
kubectl top pods
```

---

## 📈 Monitoring

### Key Metrics
- **GPU Utilization**: Monitor across both GPU nodes
- **Ingest Rate**: Target 10+ documents/second
- **Service Health**: Regular health checks
- **Storage Usage**: Monitor NFS and MinIO capacity

### Monitoring Tools
- **Zipkin**: Distributed tracing
- **OpenTelemetry**: Metrics collection
- **Kubectl**: Resource monitoring
- **Custom Scripts**: Performance monitoring

---

## 🔒 Security

### Current Security Status
- **Network**: Default allow-all policies
- **RBAC**: Standard Kubernetes RBAC
- **Secrets**: Basic authentication
- **Images**: NVIDIA NGC images

### Security Recommendations
- Implement network policies
- Configure proper RBAC
- Use Kubernetes secrets
- Scan container images

---

## 📚 Additional Resources

### External Documentation
- [NVIDIA RAG Blueprint](https://github.com/NVIDIA/GenerativeAIExamples)
- [Milvus Documentation](https://milvus.io/docs)
- [Kubernetes Documentation](https://kubernetes.io/docs)
- [Calico CNI](https://projectcalico.org/)

### Internal Documentation
- [GPU Service Balancing Guide](../GPU_Service_Balancing_Guide.md)
- [Port Forwarding Guide](../NAT_PORT_CONFIGURATION_GUIDE.md)
- [Performance Analysis Scripts](../analyze-performance.sh)

---

## 📞 Support

### Contact Information
For questions about this deployment:
1. Review the comprehensive documentation in this package
2. Check the troubleshooting sections
3. Refer to the deployment history for similar issues
4. Use the replication instructions for fresh deployments

### Maintenance Schedule
- **Daily**: Service health checks
- **Weekly**: Performance monitoring
- **Monthly**: Security updates
- **Quarterly**: Full cluster review

---

This documentation package provides everything needed to understand, maintain, and recreate the OCI Kubernetes RAG cluster deployment. Each document is self-contained but cross-references others for comprehensive coverage.
