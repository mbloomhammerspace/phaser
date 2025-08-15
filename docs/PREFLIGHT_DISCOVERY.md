# Preflight Discovery - Hardware Auto-Detection

## Overview

The Preflight Discovery system automatically detects hardware capabilities across your infrastructure and builds optimal deployment plans for the Kubernetes RAG system. This eliminates manual configuration and ensures optimal resource allocation.

## Features

### 🔍 **Automatic Hardware Detection**
- **CPU**: Cores, model, frequency
- **Memory**: Total and available RAM
- **Storage**: Device types, sizes, and performance characteristics
- **GPU**: NVIDIA GPU detection, memory, and capabilities
- **Network**: Interface speeds and connectivity
- **OS**: Operating system and kernel information

### 🎯 **Intelligent Role Assignment**
- **Master Nodes**: High-priority nodes with strong CPU/memory
- **GPU Worker Nodes**: Nodes with NVIDIA GPUs for AI workloads
- **Regular Worker Nodes**: Standard compute nodes for general workloads

### 📊 **Comprehensive Reporting**
- Detailed hardware inventory
- Performance recommendations
- Resource utilization analysis
- Deployment optimization suggestions

## Quick Start

### **Method 1: Interactive Discovery**
```bash
# Run the installer with preflight discovery
./install.sh

# The system will automatically:
# 1. Discover your nodes interactively
# 2. Detect hardware capabilities
# 3. Build optimal deployment plan
# 4. Generate inventory file
# 5. Proceed with installation
```

### **Method 2: File-Based Discovery**
```bash
# Create nodes file
cat > my-nodes.txt << EOF
master1:192.168.1.10:ubuntu
worker1:192.168.1.11:ubuntu
worker2:192.168.1.12:ubuntu
EOF

# Run discovery only
./utils/preflight.sh --nodes my-nodes.txt --discover-only

# Run full installation with discovered inventory
./install.sh --inventory discovery/inventory.yml
```

### **Method 3: Standalone Discovery**
```bash
# Run preflight checker directly
./utils/preflight.sh --nodes my-nodes.txt

# This will:
# - Discover hardware capabilities
# - Generate deployment plan
# - Create inventory file
# - Show detailed report
```

## Hardware Discovery Details

### **CPU Detection**
```bash
# Detects:
- Number of CPU cores
- CPU model and architecture
- CPU frequency
- Performance characteristics

# Example output:
CPU: 16 cores, Intel(R) Xeon(R) Gold 6248 @ 2.50GHz
```

### **Memory Detection**
```bash
# Detects:
- Total system memory
- Available memory
- Memory type (if available)
- Memory speed (if available)

# Example output:
Memory: 64.0 GB total, 58.2 GB available
```

### **Storage Detection**
```bash
# Detects:
- All storage devices
- Device types (NVMe, SSD, HDD)
- Storage capacities
- Performance characteristics
- Mount points

# Example output:
Storage: 2.0 TB total, 1.5 TB fast storage (NVMe/SSD)
Devices:
  - nvme0n1: 1.0 TB NVMe
  - sda: 1.0 TB SSD
```

### **GPU Detection**
```bash
# Detects:
- NVIDIA GPU presence
- GPU models and types
- GPU memory capacity
- CUDA compatibility
- Driver status

# Example output:
GPUs: 2 devices, 80.0 GB total
  - GPU 0: NVIDIA A100-SXM4-40GB (40.0 GB)
  - GPU 1: NVIDIA A100-SXM4-40GB (40.0 GB)
```

### **Network Detection**
```bash
# Detects:
- Network interfaces
- Interface speeds
- IP addresses
- Network connectivity

# Example output:
Network: 25.0 Gbps primary interface (eth0)
Interfaces:
  - eth0: 25 Gbps, 192.168.1.10
  - eth1: 10 Gbps, 10.0.1.10
```

## Role Assignment Algorithm

### **Priority Scoring System**
The system uses a sophisticated scoring algorithm to determine optimal node roles:

```python
priority_score = 0

# CPU scoring (0-10 points)
if cpu_cores >= 16: priority_score += 10
elif cpu_cores >= 8: priority_score += 5
elif cpu_cores >= 4: priority_score += 2

# Memory scoring (0-10 points)
if total_memory_gb >= 64: priority_score += 10
elif total_memory_gb >= 32: priority_score += 5
elif total_memory_gb >= 16: priority_score += 2

# Storage scoring (0-10 points)
if fast_storage_gb >= 500: priority_score += 10
elif fast_storage_gb >= 100: priority_score += 5
elif fast_storage_gb >= 50: priority_score += 2

# Network scoring (0-10 points)
if network_speed_gbps >= 25: priority_score += 10
elif network_speed_gbps >= 10: priority_score += 5
elif network_speed_gbps >= 1: priority_score += 2

# GPU scoring (0-35 points)
if gpu_count > 0: priority_score += 20
if total_gpu_memory_gb >= 80: priority_score += 15
elif total_gpu_memory_gb >= 40: priority_score += 10
elif total_gpu_memory_gb >= 16: priority_score += 5
```

### **Role Assignment Rules**
1. **GPU Worker Nodes**: Any node with NVIDIA GPUs
2. **Master Nodes**: Highest priority non-GPU nodes
3. **Regular Worker Nodes**: Remaining nodes

## Output Files

### **Discovery Report** (`discovery_report.md`)
```markdown
# Kubernetes RAG Installer - Hardware Discovery Report
Generated: 2024-01-15 10:30:00

## Summary
- Total Nodes: 5
- Master Nodes: 1
- GPU Worker Nodes: 2
- Regular Worker Nodes: 2
- Total GPUs: 4
- Total GPU Memory: 160.0 GB

## Node Details
### Node 1: master1 (192.168.1.10)
- **Role**: MASTER
- **Priority Score**: 25
- **CPU**: 16 cores, Intel Xeon Gold 6248
- **Memory**: 64.0 GB total
- **Storage**: 1.0 TB fast storage
...
```

### **Deployment Plan** (`deployment_plan.json`)
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "master_node": {
    "hostname": "master1",
    "ip_address": "192.168.1.10",
    "capabilities": {
      "cpu_cores": 16,
      "total_memory_gb": 64.0,
      "gpu_count": 0,
      "recommended_role": "master",
      "recommended_priority": 25
    }
  },
  "gpu_worker_nodes": [
    {
      "hostname": "gpu1",
      "ip_address": "192.168.1.20",
      "capabilities": {
        "gpu_count": 2,
        "total_gpu_memory_gb": 80.0,
        "recommended_role": "gpu_worker"
      }
    }
  ],
  "summary": {
    "total_nodes": 5,
    "total_gpus": 4,
    "total_gpu_memory_gb": 160.0
  }
}
```

### **Ansible Inventory** (`inventory.yml`)
```yaml
all:
  children:
    kube_control_plane:
      hosts:
        master1:
          ansible_host: 192.168.1.10
          ansible_user: ubuntu
          ansible_ssh_private_key_file: ~/.ssh/id_rsa
    kube_node:
      hosts:
        gpu1:
          ansible_host: 192.168.1.20
          ansible_user: ubuntu
          gpu_enabled: true
        worker1:
          ansible_host: 192.168.1.30
          ansible_user: ubuntu
          gpu_enabled: false
```

## Configuration Options

### **Command Line Options**
```bash
# Basic discovery
./utils/preflight.sh

# With custom nodes file
./utils/preflight.sh --nodes my-nodes.txt

# Custom output directory
./utils/preflight.sh --discovery-output ./my-discovery

# Custom SSH key
./utils/preflight.sh --ssh-key ~/.ssh/my-key

# Custom username
./utils/preflight.sh --username admin

# Discovery only (no file generation)
./utils/preflight.sh --discover-only

# Generate files only (requires existing discovery)
./utils/preflight.sh --generate-only
```

### **Environment Variables**
```bash
# SSH configuration
export SSH_KEY_PATH="~/.ssh/id_rsa"
export SSH_USERNAME="ubuntu"

# Discovery configuration
export DISCOVERY_OUTPUT_DIR="./discovery"
export DISCOVERY_TIMEOUT=30

# Logging
export PREFLIGHT_LOG_LEVEL="INFO"
```

## Integration with Installer

### **Automatic Integration**
The preflight discovery is automatically integrated into the main installer:

```bash
# Automatic discovery and installation
./install.sh

# This will:
# 1. Run hardware discovery
# 2. Generate optimal inventory
# 3. Deploy Kubernetes cluster
# 4. Install GPU operator
# 5. Deploy RAG blueprint
```

### **Manual Integration**
```bash
# Step 1: Run discovery
./utils/preflight.sh --nodes my-nodes.txt

# Step 2: Review results
cat discovery/discovery_report.md

# Step 3: Install with discovered inventory
./install.sh --inventory discovery/inventory.yml
```

## Troubleshooting

### **Common Issues**

#### **SSH Connection Failures**
```bash
# Test SSH connectivity
ssh -i ~/.ssh/id_rsa ubuntu@192.168.1.10

# Check SSH key permissions
chmod 600 ~/.ssh/id_rsa
chmod 700 ~/.ssh

# Verify SSH configuration
ssh -v -i ~/.ssh/id_rsa ubuntu@192.168.1.10
```

#### **GPU Detection Issues**
```bash
# Check if nvidia-smi is available
ssh ubuntu@192.168.1.10 "which nvidia-smi"

# Check GPU driver installation
ssh ubuntu@192.168.1.10 "nvidia-smi"

# Check GPU device files
ssh ubuntu@192.168.1.10 "ls -la /dev/nvidia*"
```

#### **Storage Detection Issues**
```bash
# Check lsblk availability
ssh ubuntu@192.168.1.10 "which lsblk"

# Check block device information
ssh ubuntu@192.168.1.10 "lsblk -d -o NAME,SIZE,TYPE,MOUNTPOINT,ROTA"

# Check NVMe devices
ssh ubuntu@192.168.1.10 "ls -la /dev/nvme*"
```

### **Debug Mode**
```bash
# Enable debug logging
export PREFLIGHT_LOG_LEVEL="DEBUG"
./utils/preflight.sh --nodes my-nodes.txt

# Check log file
tail -f preflight.log
```

### **Manual Hardware Check**
```bash
# Run manual hardware check on a node
ssh ubuntu@192.168.1.10 << 'EOF'
echo "=== CPU Information ==="
nproc
cat /proc/cpuinfo | grep "model name" | head -1

echo "=== Memory Information ==="
free -g

echo "=== Storage Information ==="
lsblk -d -o NAME,SIZE,TYPE,MOUNTPOINT,ROTA

echo "=== GPU Information ==="
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits 2>/dev/null || echo "No NVIDIA GPUs found"

echo "=== Network Information ==="
ip -json addr show
EOF
```

## Best Practices

### **Node Preparation**
1. **SSH Access**: Ensure SSH key-based authentication is configured
2. **User Permissions**: Use a user with sudo privileges
3. **Network Connectivity**: Verify all nodes can reach each other
4. **Hardware**: Ensure hardware is properly installed and detected

### **Discovery Process**
1. **Test Connectivity**: Verify SSH access before running discovery
2. **Review Results**: Always review the discovery report before proceeding
3. **Validate Recommendations**: Check that role assignments make sense
4. **Backup Configuration**: Save discovery results for future reference

### **Production Deployment**
1. **Multiple Discovery Runs**: Run discovery multiple times to ensure consistency
2. **Documentation**: Document hardware specifications and role assignments
3. **Monitoring**: Monitor resource utilization after deployment
4. **Scaling**: Use discovery results to plan future scaling

## Advanced Features

### **Custom Role Assignment**
You can override automatic role assignment by modifying the deployment plan:

```bash
# Edit the deployment plan
vim discovery/deployment_plan.json

# Regenerate inventory with custom roles
./utils/preflight.sh --generate-only
```

### **Resource Optimization**
The system automatically optimizes resource allocation based on discovered hardware:

```yaml
# Example: GPU-aware resource allocation
rag_server:
  resources:
    requests:
      nvidia.com/gpu: "1"  # Only on GPU nodes
    limits:
      nvidia.com/gpu: "1"
```

### **Performance Recommendations**
The discovery system provides performance recommendations:

```markdown
## Recommendations
✅ Sufficient GPU resources detected for production RAG workloads.
✅ Sufficient memory resources detected.
⚠️  Limited fast storage (NVMe/SSD). Consider adding NVMe storage for better performance.
```

## Support

For issues with preflight discovery:

1. **Check Logs**: Review `preflight.log` for detailed error information
2. **Test Connectivity**: Verify SSH access to all nodes
3. **Hardware Verification**: Ensure hardware is properly detected by the OS
4. **Documentation**: Refer to this guide for troubleshooting steps
5. **Community**: Report issues with detailed hardware specifications
