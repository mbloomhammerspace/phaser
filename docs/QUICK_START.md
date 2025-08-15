# Kubernetes RAG Installer - Quick Start Guide

## 🚀 Get Started in 10 Minutes

This quick start guide will help you deploy a Kubernetes RAG system with GPU support in under 10 minutes using our fully automated installer.

## Prerequisites Checklist

### ✅ **Control Machine**
- [ ] Ubuntu 20.04+ or macOS 10.15+
- [ ] Python 3.8+
- [ ] SSH key pair
- [ ] Internet connection

### ✅ **Target Hosts**
- [ ] Ubuntu 20.04+ or CentOS 8+ (3 nodes minimum)
- [ ] 4+ CPU cores per node
- [ ] 8GB+ RAM per node
- [ ] 50GB+ storage per node
- [ ] NVIDIA GPU (optional, for GPU workloads)
- [ ] SSH key-based access to all nodes

## Quick Installation

### **Step 1: Clone and Setup**

```bash
# Clone the repository
git clone https://github.com/mbloomhammerspace/phaser.git
cd phaser

# Make installer executable
chmod +x install.sh
```

### **Step 2: Run Fully Automated Installation**

```bash
# Start the automated installer
./install.sh --preflight

# Follow the simple prompts:
# 1. SSH key path (default: ~/.ssh/id_rsa)
# 2. SSH username (default: ubuntu)
# 3. Enter node IP addresses (one per line, press Enter twice when done)
#
# Example:
# ~/.ssh/id_rsa
# ubuntu
# 192.168.1.10
# 192.168.1.11
# 192.168.1.12
# [Enter]
# [Enter]
```

### **What Happens Automatically:**

✅ **Hostname Configuration**: Sets hostnames (master1, worker1, worker2, etc.)
✅ **Package Installation**: Installs Python, pip, curl, wget, git, and other prerequisites
✅ **Hardware Discovery**: Detects CPU, RAM, storage, and GPU capabilities
✅ **Role Assignment**: Intelligently assigns master, GPU worker, and worker roles
✅ **Deployment Planning**: Builds optimal deployment plan based on hardware
✅ **Kubernetes Deployment**: Deploys production-ready Kubernetes cluster
✅ **Storage Setup**: Configures CSI storage with NFS and local disk discovery
✅ **GPU Operator**: Installs NVIDIA GPU Operator for GPU support
✅ **RAG Blueprint**: Deploys complete NVIDIA RAG Blueprint
✅ **Observability**: Configures monitoring and tracing stack

## Access Your RAG System

### **Get Your Access URLs**

```bash
# Get master node IP from generated inventory
MASTER_IP=$(grep -A1 "kube_control_plane:" discovery/inventory.yml | grep "ansible_host" | head -1 | awk '{print $2}')

echo "🎉 Your RAG system is ready!"
echo ""
echo "📋 Access URLs:"
echo "• RAG Playground: http://$MASTER_IP:30081"
echo "• RAG API: http://$MASTER_IP:30080"
echo "• Grafana (Monitoring): http://$MASTER_IP:30671 (admin/admin)"
echo "• Jaeger (Tracing): http://$MASTER_IP:30668"
echo "• Zipkin (Tracing): http://$MASTER_IP:30669"
echo "• Attu (Milvus UI): http://$MASTER_IP:30670"
```
