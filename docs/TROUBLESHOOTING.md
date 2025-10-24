# Troubleshooting Guide

## 🚨 Common Issues and Solutions

### RAG Playground Issues

#### Port-Forwarding Problems
**Problem**: Cannot access RAG Playground at `http://localhost:3000`
**Solution**:
```bash
# Check if port-forward is running
kubectl get pods -l app=rag-frontend

# Start port-forward
kubectl port-forward service/clean-rag-frontend 3000:3000

# Check for port conflicts
lsof -i :3000
```

#### RAG Playground Not Loading
**Problem**: White screen or connection errors
**Solution**:
```bash
# Check pod status
kubectl get pods -l app=rag-frontend

# Check logs
kubectl logs -l app=rag-frontend

# Restart if needed
kubectl rollout restart deployment/clean-rag-frontend
```

### AI-Q Research Assistant Issues

#### Frontend White Screen
**Problem**: AI-Q frontend shows "Application error: a client-side exception has occurred"
**Solution**:
```bash
# Check environment variables consistency
kubectl get deployment aiq-frontend -o yaml | grep -A 20 env:

# Fix environment variables
helm upgrade aiq ./charts/aiq-research-assistant

# Check frontend logs
kubectl logs -l app=aiq-frontend
```

#### Backend Connection Issues
**Problem**: Frontend cannot connect to backend
**Solution**:
```bash
# Check backend status
kubectl get pods -l app=aiq-aira-backend

# Check nginx proxy
kubectl get pods -l app=aiq-aira-nginx

# Check logs
kubectl logs -l app=aiq-aira-backend
kubectl logs -l app=aiq-aira-nginx
```

#### Collections Not Loading
**Problem**: No collections available in AI-Q interface
**Solution**:
```bash
# Test collections endpoint
curl http://localhost:8051/collections

# Check backend configuration
kubectl get configmap aiq-custom-config

# Restart backend
kubectl rollout restart deployment/aiq-aira-backend
```

### Kubernetes Cluster Issues

#### Node Not Ready
**Problem**: `kubectl get nodes` shows nodes as NotReady
**Solution**:
```bash
# Check node status
kubectl describe node <node-name>

# Check kubelet status
systemctl status kubelet

# Restart kubelet
sudo systemctl restart kubelet
```

#### Pod Stuck in Pending
**Problem**: Pods remain in Pending state
**Solution**:
```bash
# Check pod events
kubectl describe pod <pod-name>

# Check resource availability
kubectl top nodes
kubectl top pods

# Check storage classes
kubectl get storageclass
```

#### GPU Not Detected
**Problem**: GPU workloads cannot access GPUs
**Solution**:
```bash
# Check GPU operator
kubectl get pods -n gpu-operator-resources

# Check node labels
kubectl get nodes --show-labels | grep gpu

# Check GPU resources
kubectl describe node <gpu-node> | grep nvidia.com/gpu
```

### Storage Issues

#### PVC Stuck in Pending
**Problem**: PersistentVolumeClaim remains in Pending state
**Solution**:
```bash
# Check PVC status
kubectl describe pvc <pvc-name>

# Check available storage classes
kubectl get storageclass

# Check PV availability
kubectl get pv
```

#### NFS Connection Issues
**Problem**: NFS volumes cannot be mounted
**Solution**:
```bash
# Check NFS server
kubectl get pods -l app=nfs-server

# Check NFS server logs
kubectl logs -l app=nfs-server

# Test NFS connectivity
kubectl run nfs-test --rm -it --image=busybox -- sh
# Inside pod: mount -t nfs <nfs-server-ip>:/exports /mnt
```

### Network Issues

#### DNS Resolution Problems
**Problem**: Pods cannot resolve service names
**Solution**:
```bash
# Check CoreDNS
kubectl get pods -n kube-system -l k8s-app=kube-dns

# Check DNS configuration
kubectl get configmap -n kube-system coredns -o yaml

# Test DNS from pod
kubectl run dns-test --rm -it --image=busybox -- nslookup kubernetes.default
```

#### Service Discovery Issues
**Problem**: Services cannot reach each other
**Solution**:
```bash
# Check service endpoints
kubectl get endpoints

# Check service configuration
kubectl get svc

# Test connectivity
kubectl run network-test --rm -it --image=busybox -- wget -O- <service-name>:<port>
```

### Redis Issues

#### Redis Connection Failures
**Problem**: Services cannot connect to Redis
**Solution**:
```bash
# Check Redis status
kubectl get pods -l app=redis

# Check Redis logs
kubectl logs -l app=redis

# Test Redis connectivity
kubectl run redis-test --rm -it --image=redis -- redis-cli -h <redis-service>
```

#### Redis Memory Issues
**Problem**: Redis running out of memory
**Solution**:
```bash
# Check Redis memory usage
kubectl exec -it <redis-pod> -- redis-cli info memory

# Check Redis configuration
kubectl exec -it <redis-pod> -- redis-cli config get maxmemory
```

### Milvus Issues

#### Milvus Not Starting
**Problem**: Milvus pods in CrashLoopBackOff
**Solution**:
```bash
# Check Milvus logs
kubectl logs -l app=milvus

# Check Milvus configuration
kubectl get configmap milvus-config

# Check storage requirements
kubectl describe pvc milvus-pvc
```

#### Vector Search Issues
**Problem**: Vector search returns no results
**Solution**:
```bash
# Check Milvus status
kubectl exec -it <milvus-pod> -- curl http://localhost:9091/health

# Check collection status
kubectl exec -it <milvus-pod> -- curl http://localhost:9091/collections

# Verify data ingestion
kubectl logs -l app=rag-server
```

## 🔍 Diagnostic Commands

### System Health Check
```bash
# Overall cluster status
kubectl get nodes
kubectl get pods --all-namespaces
kubectl get svc --all-namespaces

# Resource usage
kubectl top nodes
kubectl top pods --all-namespaces

# Storage status
kubectl get pv
kubectl get pvc --all-namespaces
kubectl get storageclass
```

### Service-Specific Checks
```bash
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

### Log Analysis
```bash
# Recent logs
kubectl logs -l app=rag-server --tail=100

# Follow logs
kubectl logs -l app=rag-server -f

# Logs from specific time
kubectl logs -l app=rag-server --since=1h
```

## 🛠️ Recovery Procedures

### Complete System Reset
```bash
# Delete all deployments
kubectl delete deployment --all

# Delete all services
kubectl delete svc --all

# Delete all PVCs (WARNING: Data loss)
kubectl delete pvc --all

# Restart cluster
sudo systemctl restart kubelet
```

### Selective Service Recovery
```bash
# Restart specific service
kubectl rollout restart deployment/<service-name>

# Scale down and up
kubectl scale deployment/<service-name> --replicas=0
kubectl scale deployment/<service-name> --replicas=1

# Delete and recreate
kubectl delete deployment/<service-name>
kubectl apply -f <service-manifest>
```

## 📊 Performance Monitoring

### Resource Monitoring
```bash
# Node resource usage
kubectl top nodes

# Pod resource usage
kubectl top pods --all-namespaces

# GPU usage
kubectl describe node <gpu-node> | grep nvidia.com/gpu
```

### Network Monitoring
```bash
# Service connectivity
kubectl get endpoints

# Network policies
kubectl get networkpolicy

# Ingress status
kubectl get ingress
```

## 🆘 Emergency Procedures

### Critical Service Down
1. **Identify the issue**: Check pod status and logs
2. **Restart the service**: Use `kubectl rollout restart`
3. **Check dependencies**: Ensure all required services are running
4. **Verify configuration**: Check ConfigMaps and Secrets
5. **Test connectivity**: Verify service-to-service communication

### Data Loss Prevention
1. **Backup PVCs**: Create snapshots of critical data
2. **Document state**: Record current configuration
3. **Test recovery**: Verify backup restoration procedures
4. **Monitor storage**: Watch for storage capacity issues

### Performance Degradation
1. **Check resource usage**: Monitor CPU, memory, and GPU
2. **Scale services**: Increase replicas if needed
3. **Optimize configuration**: Tune service parameters
4. **Monitor logs**: Look for error patterns

## 📞 Getting Help

### Before Asking for Help
1. **Check logs**: Review all relevant service logs
2. **Document the issue**: Note error messages and symptoms
3. **Test basic connectivity**: Verify network and DNS
4. **Check resources**: Ensure adequate CPU, memory, and storage
5. **Review configuration**: Verify all settings are correct

### Information to Provide
- **Error messages**: Exact text of any error messages
- **Logs**: Relevant log entries from affected services
- **Configuration**: Current settings and environment
- **Steps to reproduce**: How the issue occurred
- **Expected behavior**: What should happen instead

### Support Channels
- **Documentation**: Check this guide and related docs
- **GitHub Issues**: Open an issue with detailed information
- **Community Forums**: Ask questions in relevant communities
- **Professional Support**: Contact for enterprise deployments
