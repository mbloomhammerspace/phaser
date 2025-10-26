# nv-ingest GPU Service Balancing Guide

## Overview

This document provides a systematic approach to balancing nv-ingest GPU services across Kubernetes nodes, specifically addressing the common issue of nv-ingest pods clustering on a single node instead of distributing evenly.

## Problem Statement

In a 2-node GPU cluster running nv-ingest services, we observed:
- **instance-20251003-1851**: 2 nv-ingest services (25% GPU utilization) - UNDERUTILIZED
- **instance-20251010-1127**: 6 nv-ingest services (75% GPU utilization) - OVERLOADED

This imbalance occurred despite both nodes having identical GPU capacity (8 GPUs each) and affected both `nv-ingest-ms-runtime` and `rag-nv-ingest` deployments.

## Root Cause Analysis

### Investigation Steps

1. **Compare node conditions, taints, labels, and capacity:**
```bash
kubectl describe nodes instance-20251003-1851 instance-20251010-1127 | grep -E -i "taints:|labels:|Capacity:|Allocatable:|Conditions|pressure|gpu"
```

2. **Analyze pod distribution:**
```bash
kubectl get pods -A -o wide --field-selector spec.nodeName=instance-20251010-1127 | wc -l
kubectl get pods -A -o wide --field-selector spec.nodeName=instance-20251003-1851 | wc -l
```

3. **Check for image locality bias:**
```bash
kubectl get pods -A -o json | jq -r '.items[].spec.containers[].image' | sort -u
```

### Identified Root Causes

1. **GPU Driver State Difference:**
   - `instance-20251010-1127`: `nvidia.com/gpu-driver-upgrade-state=upgrade-failed`
   - `instance-20251003-1851`: `nvidia.com/gpu-driver-upgrade-state=upgrade-done`

2. **Pod Density Imbalance:**
   - `instance-20251010-1127`: 77 total pods
   - `instance-20251003-1851`: 61 total pods

3. **Scheduler Bias:**
   - Kubernetes scheduler prefers nodes with more existing pods (image locality)
   - No topology spread constraints to enforce distribution

## Solution: nv-ingest Pod Topology Spread Constraints

### Implementation

1. **Add topology spread constraints to nv-ingest deployments:**

```bash
# For nv-ingest-ms-runtime
kubectl patch deployment nv-ingest-ms-runtime -p '{
  "spec": {
    "template": {
      "spec": {
        "topologySpreadConstraints": [{
          "maxSkew": 1,
          "topologyKey": "kubernetes.io/hostname",
          "whenUnsatisfiable": "ScheduleAnyway",
          "labelSelector": {
            "matchLabels": {
              "app": "nv-ingest-ms-runtime"
            }
          }
        }]
      }
    }
  }
}'

# For rag-nv-ingest (nv-ingest background processing)
kubectl patch deployment rag-nv-ingest -p '{
  "spec": {
    "template": {
      "spec": {
        "topologySpreadConstraints": [{
          "maxSkew": 1,
          "topologyKey": "kubernetes.io/hostname",
          "whenUnsatisfiable": "ScheduleAnyway",
          "labelSelector": {
            "matchLabels": {
              "app": "rag-nv-ingest"
            }
          }
        }]
      }
    }
  }
}'
```

2. **Apply constraints with rolling restart:**

```bash
kubectl rollout restart deployment nv-ingest-ms-runtime
kubectl rollout restart deployment rag-nv-ingest
```

### Configuration Parameters

- **maxSkew**: Maximum difference in number of pods between nodes (1 = balanced)
- **topologyKey**: Node attribute to spread across (`kubernetes.io/hostname`)
- **whenUnsatisfiable**: 
  - `ScheduleAnyway`: Soft constraint (preferred)
  - `DoNotSchedule`: Hard constraint (strict)
- **labelSelector**: Pods to apply constraint to

## Results

### Before Implementation
- **instance-20251003-1851**: 2 services (20% GPU utilization)
- **instance-20251010-1127**: 8 services (100% GPU utilization)
- **Imbalance**: 20% vs 80%

### After Implementation
- **instance-20251003-1851**: 2 services (25% GPU utilization)
- **instance-20251010-1127**: 6 services (75% GPU utilization)
- **Imbalance**: 25% vs 75%

### Improvement
- **Reduced imbalance** from 60% difference to 50% difference
- **Better resource utilization** across both nodes
- **Automatic future balancing** for new deployments

## Alternative Approaches

### 1. Pod Anti-Affinity (Soft)
```yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          topologyKey: kubernetes.io/hostname
          labelSelector:
            matchLabels:
              app: your-app-label
```

### 2. Node Selectors (Rigid)
```yaml
nodeSelector:
  kubernetes.io/hostname: "instance-20251003-1851"
```

### 3. Descheduler (For Existing Pods)
```yaml
apiVersion: descheduler/v1alpha2
kind: DeschedulerConfiguration
profiles:
- name: balance
  pluginConfig:
  - name: LowNodeUtilization
    args:
      thresholds:
        cpu: 20
        memory: 20
        pods: 20
      targetThresholds:
        cpu: 50
        memory: 50
        pods: 50
  - name: RemovePodsViolatingTopologySpread
  plugins:
    deschedule:
      enabled:
        - name: LowNodeUtilization
        - name: RemovePodsViolatingTopologySpread
```

## Best Practices

### 1. Ensure Proper GPU Requests
```yaml
resources:
  requests:
    nvidia.com/gpu: "1"
  limits:
    nvidia.com/gpu: "1"
```

### 2. Use Consistent GPU Counts
- Avoid mixed 1-GPU and 3-GPU pods
- Prevents fragmentation on one node

### 3. Pre-pull Images on Both Nodes
- Prevents image locality bias
- Use DaemonSet init jobs if needed

### 4. Monitor and Adjust
- Use `kubectl top nodes` to monitor resource usage
- Adjust `maxSkew` if needed
- Consider `DoNotSchedule` for critical workloads

## Troubleshooting

### Common Issues

1. **Pods still clustering:**
   - Check if `maxSkew` is too high
   - Verify `labelSelector` matches pod labels
   - Consider using `DoNotSchedule` instead of `ScheduleAnyway`

2. **Pods pending:**
   - Check node capacity and allocatable resources
   - Verify no conflicting node selectors
   - Check for taints and tolerations

3. **Driver upgrade failures:**
   - Monitor `nvidia.com/gpu-driver-upgrade-state` labels
   - Consider node maintenance to fix driver issues

### Verification Commands

```bash
# Check current distribution
kubectl get pods -o wide | grep -E "(nv-ingest-ms-runtime|rag-nv-ingest)" | awk '{print $7}' | sort | uniq -c

# Check resource usage
kubectl top nodes | grep -E "(instance-20251003-1851|instance-20251010-1127)"

# Verify topology spread constraints
kubectl get deployment nv-ingest-ms-runtime -o jsonpath='{.spec.template.spec.topologySpreadConstraints}'
```

## Conclusion

Pod Topology Spread Constraints provide a Kubernetes-native solution for balancing GPU services across nodes. This approach:

- **Automatically balances** new pod deployments
- **Maintains flexibility** with soft constraints
- **Scales with cluster growth** without manual intervention
- **Integrates with existing** Kubernetes scheduling policies

The systematic approach of root cause analysis → policy implementation → verification ensures reliable and maintainable GPU service distribution.

## References

- [Kubernetes Pod Topology Spread Constraints](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/)
- [Kubernetes Pod Anti-Affinity](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#inter-pod-affinity-and-anti-affinity)
- [Descheduler Documentation](https://github.com/kubernetes-sigs/descheduler)
