# Hardware Specifications - OCI Deployment
## Detailed Instance Information

### Instance Summary
| Instance Name | Type | IP Address | CPU | Memory | GPU | OS | Kernel |
|---------------|------|------------|-----|--------|-----|----|---------| 
| master-node | Control Plane | 10.0.0.128 | 2 cores | 16GB | None | Ubuntu 24.04.2 LTS | 6.8.0-1028-oracle |
| instance-20251003-1851 | GPU Worker | 10.0.0.25 | 224 cores | 2TB | 8x NVIDIA | Ubuntu 22.04.5 LTS | 6.8.0-1035-oracle |
| instance-20251010-1127 | GPU Worker | 10.0.0.60 | 224 cores | 2TB | 8x NVIDIA | Ubuntu 22.04.5 LTS | 6.8.0-1037-oracle |
| worker-node-1 | Regular Worker | 10.0.0.167 | 2 cores | 16GB | None | Ubuntu 24.04.2 LTS | 6.14.0-1015-oracle |
| worker-node-2 | Regular Worker | 10.0.0.249 | 2 cores | 16GB | None | Ubuntu 24.04.2 LTS | 6.8.0-1028-oracle |

### GPU Node Details

#### instance-20251003-1851 (Primary GPU Node)
- **Instance ID**: instance-20251003-1851
- **Creation Date**: October 3rd, 2025
- **IP Address**: 10.0.0.25
- **Operating System**: Ubuntu 22.04.5 LTS
- **Kernel Version**: 6.8.0-1035-oracle
- **Architecture**: amd64
- **CPU**: 224 cores
- **Memory**: 2TB (2,113,353,432 KiB)
- **GPU**: 8x NVIDIA GPUs
- **Container Runtime**: containerd://1.7.27
- **Kubernetes Version**: v1.30.4
- **Status**: Ready
- **Pod Distribution**: 32 pods

#### instance-20251010-1127 (Secondary GPU Node)
- **Instance ID**: instance-20251010-1127
- **Creation Date**: October 10th, 2025
- **IP Address**: 10.0.0.60
- **Operating System**: Ubuntu 22.04.5 LTS
- **Kernel Version**: 6.8.0-1037-oracle
- **Architecture**: amd64
- **CPU**: 224 cores
- **Memory**: 2TB (2,113,353,396 KiB)
- **GPU**: 8x NVIDIA GPUs
- **Container Runtime**: containerd://1.7.28
- **Kubernetes Version**: v1.30.4
- **Status**: Ready
- **Pod Distribution**: 483 pods (primary workload node)

### Control Plane Node

#### master-node
- **Instance ID**: master-node
- **IP Address**: 10.0.0.128
- **Operating System**: Ubuntu 24.04.2 LTS
- **Kernel Version**: 6.8.0-1028-oracle
- **Architecture**: amd64
- **CPU**: 2 cores
- **Memory**: 16GB (16,372,216 KiB)
- **GPU**: None
- **Container Runtime**: containerd://1.7.21
- **Kubernetes Version**: v1.30.4
- **Role**: control-plane
- **Status**: Ready

### Regular Worker Nodes

#### worker-node-1
- **Instance ID**: worker-node-1
- **IP Address**: 10.0.0.167
- **Operating System**: Ubuntu 24.04.2 LTS
- **Kernel Version**: 6.14.0-1015-oracle
- **Architecture**: amd64
- **CPU**: 2 cores
- **Memory**: 16GB (16,372,440 KiB)
- **GPU**: None
- **Container Runtime**: containerd://1.7.21
- **Kubernetes Version**: v1.30.4
- **Status**: Ready, SchedulingDisabled
- **Pod Distribution**: 1 pod

#### worker-node-2
- **Instance ID**: worker-node-2
- **IP Address**: 10.0.0.249
- **Operating System**: Ubuntu 24.04.2 LTS
- **Kernel Version**: 6.8.0-1028-oracle
- **Architecture**: amd64
- **CPU**: 2 cores
- **Memory**: 16GB (16,372,216 KiB)
- **GPU**: None
- **Container Runtime**: containerd://1.7.21
- **Kubernetes Version**: v1.30.4
- **Status**: Ready, SchedulingDisabled
- **Pod Distribution**: 1 pod

### Resource Allocation Summary

#### Total Cluster Resources
- **Total CPU**: 454 cores
- **Total Memory**: ~4TB
- **Total GPU**: 16x NVIDIA GPUs
- **Total Nodes**: 5

#### Resource Distribution
- **GPU Nodes**: 448 CPU cores, 4TB memory, 16 GPUs
- **Control Plane**: 2 CPU cores, 16GB memory
- **Regular Workers**: 4 CPU cores, 32GB memory

### Network Configuration
- **Cluster CIDR**: 10.233.0.0/16
- **Service CIDR**: 10.233.0.0/16
- **Pod CIDR**: 10.233.64.0/18 (Calico)
- **CNI**: Calico
- **Load Balancer**: MetalLB (if configured)

### Storage Configuration
- **NFS Server**: 150.136.225.57
- **NFS Path**: /hub
- **Mount Point**: /mnt/anvil/hub
- **Protocol**: NFSv4.2
- **Options**: vers=4.2,hard,intr

### Performance Characteristics
- **High-Performance GPU Nodes**: Optimized for AI/ML workloads
- **Balanced Resource Distribution**: Even split between GPU nodes
- **Network Performance**: High-bandwidth internal networking
- **Storage Performance**: NFS-based shared storage with Hammerspace

### Maintenance Notes
- **worker-node-1** and **worker-node-2** are currently cordoned (SchedulingDisabled)
- **instance-20251010-1127** carries the majority of the workload (483 pods)
- **instance-20251003-1851** is underutilized (32 pods)
- GPU balancing implemented via Pod Topology Spread Constraints
