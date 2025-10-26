# PVC Missing Issue - Root Cause Analysis
## Investigation Date: October 26, 2025

### Executive Summary
Based on comprehensive data collection from the existing Kubernetes cluster, the **hammerspace-hub-pvc is currently operational and bound** to its Persistent Volume. However, there are several storage-related issues that could explain why a PVC might have appeared "missing" or caused problems.

---

## Current Status Assessment

### ✅ **Primary PVC Status - OPERATIONAL**
- **hammerspace-hub-pvc**: BOUND to hammerspace-hub-pv (200Gi, RWX)
- **Active Usage**: 500+ folder-ingest jobs successfully using the PVC
- **NFS Connectivity**: Server 150.136.225.57 reachable (ping + ports 111,2049)
- **Mount Configuration**: NFS v4.2, server: 150.136.225.57:/hub

### ⚠️ **Secondary Issues Identified**

#### 1. **Stuck Terminating PV**
- **hammerspace-hub-test-pv**: Stuck in "Terminating" state for **45+ hours**
- **Impact**: Could cause confusion about PVC availability
- **Root Cause**: Finalizer preventing deletion, likely due to active mounts

#### 2. **Volume Deletion Failures**
- **Multiple PVs**: 4 PVs showing "VolumeFailedDelete" warnings
- **Error Pattern**: "helper-pod-delete-*" pods not found
- **Impact**: Storage cleanup issues, potential resource leaks

#### 3. **Storage Provisioner Issues**
- **local-volume-provisioner**: Pod in CrashLoopBackOff state
- **Impact**: Local storage provisioning problems
- **Frequency**: 333+ restart attempts

---

## Root Cause Analysis

### **Primary Hypothesis: PVC Never Actually Missing**

The data suggests the **hammerspace-hub-pvc was never actually missing**. Instead, the issue was likely one of these scenarios:

#### **Scenario A: Temporary Mount Failures**
- **Cause**: NFS server connectivity issues or network timeouts
- **Evidence**: NFS mount tests failed on macOS (version compatibility)
- **Impact**: Pods couldn't mount the PVC temporarily
- **Resolution**: Automatic retry mechanisms eventually succeeded

#### **Scenario B: Pod Scheduling Issues**
- **Cause**: Pods unable to schedule due to node constraints
- **Evidence**: Multiple failed pods in Error/CrashLoopBackOff states
- **Impact**: PVC appeared "missing" when pods couldn't access it
- **Resolution**: Pod rescheduling resolved the issue

#### **Scenario C: Storage Class Confusion**
- **Cause**: Multiple storage classes available (local-path, nfs-csi, hammerspace-tier0)
- **Evidence**: PVC uses no specific storage class (empty field)
- **Impact**: Potential binding issues during PVC creation
- **Resolution**: Manual PV binding resolved the issue

### **Secondary Issues Contributing to Confusion**

#### **1. Stuck Terminating PV**
```
hammerspace-hub-test-pv: Terminating (45h)
Finalizers: [kubernetes.io/pv-protection]
```
- **Root Cause**: PV protection finalizer preventing deletion
- **Impact**: Could cause confusion about PVC state
- **Resolution**: Manual finalizer removal required

#### **2. Volume Cleanup Failures**
```
VolumeFailedDelete: helper-pod-delete-* not found
```
- **Root Cause**: Kubernetes unable to create cleanup helper pods
- **Impact**: Storage resources not properly cleaned up
- **Resolution**: Manual PV deletion or cluster restart

---

## Evidence Supporting Analysis

### **Positive Evidence (PVC Working)**
1. **500+ Successful Jobs**: folder-ingest jobs completed successfully using hub PVC
2. **NFS Connectivity**: Server reachable, ports 111/2049 open
3. **PV Binding**: hammerspace-hub-pv properly bound to hammerspace-hub-pvc
4. **Recent Activity**: Jobs completing every few minutes with 27-28s processing time

### **Negative Evidence (Potential Issues)**
1. **Mount Failures**: NFS mount tests failed on macOS (version compatibility)
2. **Stuck Resources**: hammerspace-hub-test-pv terminating for 45h
3. **Cleanup Issues**: Multiple PVs with deletion failures
4. **Provisioner Problems**: local-volume-provisioner in CrashLoopBackOff

---

## Recommended Actions

### **Immediate Actions**
1. **Clean Up Stuck PV**: Remove finalizer from hammerspace-hub-test-pv
2. **Fix Provisioner**: Restart or reconfigure local-volume-provisioner
3. **Monitor PVC**: Continue monitoring hammerspace-hub-pvc for stability

### **Preventive Measures**
1. **Storage Monitoring**: Implement alerts for PVC/PV state changes
2. **Cleanup Automation**: Set up automated cleanup for failed PVs
3. **Documentation**: Document proper PVC creation/deletion procedures

### **Long-term Improvements**
1. **Storage Class Standardization**: Use consistent storage classes
2. **NFS Version Compatibility**: Ensure NFS version consistency across platforms
3. **Resource Limits**: Implement proper resource limits for storage operations

---

## Conclusion

The **hammerspace-hub-pvc is currently operational and functioning correctly**. The "missing PVC" issue was likely a temporary problem caused by:

1. **NFS connectivity issues** (most probable)
2. **Pod scheduling problems** 
3. **Storage class binding issues**

The presence of a stuck terminating PV and cleanup failures suggests there may have been previous attempts to recreate or modify the PVC, which could have caused temporary unavailability.

**Recommendation**: Focus on cleaning up the stuck resources and implementing better monitoring rather than recreating the working PVC.

---

## Data Collection Summary

### **Files Collected**
- PVC/PV status and configuration
- NFS connectivity tests
- Storage class information
- Kubernetes events and warnings
- Pod status and job completion data
- Storage provisioner logs

### **Key Metrics**
- **PVC Age**: 45h (hammerspace-hub-pvc)
- **PV Age**: 45h (hammerspace-hub-pv)
- **Stuck PV Age**: 45h+ (hammerspace-hub-test-pv)
- **Successful Jobs**: 500+ using hub PVC
- **NFS Server**: 150.136.225.57 (reachable)

### **Next Steps**
1. Monitor PVC stability over next 24-48 hours
2. Clean up stuck terminating PV
3. Implement storage monitoring alerts
4. Document incident for future reference
