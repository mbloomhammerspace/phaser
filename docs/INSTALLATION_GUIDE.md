# Kubernetes RAG Installer - Installation Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Requirements](#system-requirements)
3. [Network Requirements](#network-requirements)
4. [Installation Methods](#installation-methods)
5. [Step-by-Step Installation](#step-by-step-installation)
6. [Post-Installation Verification](#post-installation-verification)
7. [Troubleshooting](#troubleshooting)
8. [Uninstallation](#uninstallation)

## Prerequisites

### Required Software

Before installing the Kubernetes RAG system, ensure you have the following software installed:

#### **Control Machine (Where you run the installer)**
- **Operating System**: Ubuntu 20.04+, CentOS 8+, RHEL 8+, or macOS 10.15+
- **Python**: 3.8 or higher
- **Git**: Latest version
- **SSH Client**: For remote host access
- **Internet Connection**: For downloading dependencies

#### **Target Hosts (Kubernetes nodes)**
- **Operating System**: Ubuntu 20.04+, CentOS 8+, or RHEL 8+
- **CPU**: Minimum 4 cores per node
- **RAM**: Minimum 8GB per node (16GB+ recommended)
- **Storage**: Minimum 50GB available space per node
- **Network**: Stable network connectivity between nodes

### Required Accounts and Access

- **SSH Key Access**: SSH key-based authentication to all target hosts
- **Sudo Privileges**: Root or sudo access on all target hosts
- **Internet Access**: All nodes need internet access for container images
- **OpenAI API Key**: For AI-powered error handling (optional but recommended)

## System Requirements

### **Minimum Requirements**

| Component | Master Node | Worker Node | GPU Worker Node |
|-----------|-------------|-------------|-----------------|
| **CPU** | 4 cores | 4 cores | 8 cores |
| **RAM** | 8GB | 8GB | 16GB |
| **Storage** | 50GB | 50GB | 100GB |
| **Network** | 1Gbps | 1Gbps | 10Gbps |
| **GPU** | None | None | NVIDIA GPU (A100/H100 recommended) |

### **Recommended Requirements**

| Component | Master Node | Worker Node | GPU Worker Node |
|-----------|-------------|-------------|-----------------|
| **CPU** | 8 cores | 8 cores | 16 cores |
| **RAM** | 16GB | 16GB | 32GB |
| **Storage** | 100GB SSD | 100GB SSD | 500GB NVMe |
| **Network** | 10Gbps | 10Gbps | 25Gbps |
| **GPU** | None | None | NVIDIA A100/H100 |

### **GPU Requirements**

For GPU-enabled nodes:
- **NVIDIA GPU**: A100, H100, V100, or RTX 4090/4080
- **GPU Memory**: Minimum 8GB (24GB+ recommended)
- **NVIDIA Driver**: 535.154.05 or higher
- **CUDA**: 11.8 or higher

## Network Requirements

### **Network Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Control       │    │   Master Node   │    │  Worker Nodes   │
│   Machine       │◄──►│   (K8s API)     │◄──►│   (GPU/CPU)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Port Requirements**

#### **Control Machine → Target Hosts**
- **SSH**: Port 22 (TCP)
- **Kubernetes API**: Port 6443 (TCP)

#### **Inter-Node Communication**
- **Kubernetes API**: Port 6443 (TCP)
- **etcd**: Ports 2379-2380 (TCP)
- **kubelet**: Port 10250 (TCP)
- **kube-proxy**: Port 10256 (TCP)
- **Calico**: Ports 179, 4789 (TCP/UDP)

#### **External Access (NodePort Services)**
- **RAG Playground**: Port 30081 (TCP)
- **RAG API**: Port 30080 (TCP)
- **Ingestor API**: Port 30082 (TCP)
- **Milvus**: Port 30090 (TCP)
- **Attu**: Port 30670 (TCP)
- **Jaeger**: Port 30668 (TCP)
- **Zipkin**: Port 30669 (TCP)
- **Grafana**: Port 30671 (TCP)

### **DNS Requirements**

- All nodes must be able to resolve each other by hostname
- Internet DNS resolution for container image downloads
- Optional: Internal DNS server for production environments

## Installation Methods

### **Method 1: Interactive Wizard (Recommended)**

The easiest way to install the system is using the interactive wizard:

```bash
# Clone the repository
git clone <repository-url>
cd kubernetes-rag-installer

# Run interactive installer
./install.sh
```

### **Method 2: Inventory File**

For automated deployments or repeatable installations:

```bash
# Create inventory file
cp sample-inventory.yml my-cluster.yml
# Edit my-cluster.yml with your node details

# Run installer with inventory
./install.sh --inventory my-cluster.yml
```

### **Method 3: Advanced Configuration**

For custom configurations:

```bash
# Run with verbose logging
./install.sh --verbose

# Run without AI error handling
./install.sh --no-ai

# Combine options
./install.sh --inventory my-cluster.yml --verbose
```

## Step-by-Step Installation

### **Step 1: Prepare Control Machine**

```bash
# 1. Install required packages
sudo apt-get update
sudo apt-get install -y python3 python3-pip git curl wget

# 2. Install Python dependencies
pip3 install -r requirements.txt

# 3. Verify SSH key setup
ls -la ~/.ssh/id_rsa
# If not present, generate SSH key:
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
```

### **Step 2: Prepare Target Hosts**

#### **Ubuntu/Debian Hosts**
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install required packages
sudo apt-get install -y python3 python3-pip curl wget

# Configure SSH (if needed)
sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# Add SSH key to authorized_keys
mkdir -p ~/.ssh
echo "YOUR_PUBLIC_KEY" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

#### **CentOS/RHEL Hosts**
```bash
# Update system
sudo yum update -y

# Install required packages
sudo yum install -y python3 python3-pip curl wget

# Configure SSH (if needed)
sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# Add SSH key to authorized_keys
mkdir -p ~/.ssh
echo "YOUR_PUBLIC_KEY" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### **Step 3: Network Configuration**

#### **Configure Hostnames**
```bash
# On each node, set proper hostname
sudo hostnamectl set-hostname master1  # or worker1, worker2, etc.

# Add to /etc/hosts
echo "192.168.1.10 master1" | sudo tee -a /etc/hosts
echo "192.168.1.11 worker1" | sudo tee -a /etc/hosts
echo "192.168.1.12 worker2" | sudo tee -a /etc/hosts
```

#### **Configure Firewall**
```bash
# Ubuntu/Debian
sudo ufw allow 22/tcp
sudo ufw allow 6443/tcp
sudo ufw allow 10250/tcp
sudo ufw allow 179/tcp
sudo ufw allow 4789/udp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=22/tcp
sudo firewall-cmd --permanent --add-port=6443/tcp
sudo firewall-cmd --permanent --add-port=10250/tcp
sudo firewall-cmd --permanent --add-port=179/tcp
sudo firewall-cmd --permanent --add-port=4789/udp
sudo firewall-cmd --reload
```

### **Step 4: Run Installation**

#### **Interactive Installation**
```bash
# Start the installer
./install.sh

# Follow the wizard prompts:
# 1. Enter SSH key path (default: ~/.ssh/id_rsa)
# 2. Configure master node (hostname, IP, username)
# 3. Configure worker nodes (hostname, IP, GPU status)
# 4. Review configuration and confirm
```

#### **Inventory File Installation**
```bash
# Create inventory file
cat > my-cluster.yml << 'EOF'
all:
  children:
    kube_control_plane:
      hosts:
        master1:
          ansible_host: 192.168.1.10
          ansible_user: ubuntu
          ansible_ssh_private_key_file: ~/.ssh/id_rsa
          ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
    kube_node:
      hosts:
        worker1:
          ansible_host: 192.168.1.11
          ansible_user: ubuntu
          ansible_ssh_private_key_file: ~/.ssh/id_rsa
          ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
          gpu_enabled: true
        worker2:
          ansible_host: 192.168.1.12
          ansible_user: ubuntu
          ansible_ssh_private_key_file: ~/.ssh/id_rsa
          ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
          gpu_enabled: false
    k8s_cluster:
      children:
        kube_control_plane:
        kube_node:
      vars:
        ansible_python_interpreter: /usr/bin/python3
        ansible_user: ubuntu
        ansible_ssh_private_key_file: ~/.ssh/id_rsa
        ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
EOF

# Run installation
./install.sh --inventory my-cluster.yml
```

### **Step 5: Monitor Installation**

The installation process will show real-time progress:

```bash
# Example output:
[INFO] Step 1/4: Deploying Kubernetes cluster with Kubespray...
[INFO] ✓ Kubespray cluster deployment completed successfully

[INFO] Step 2/4: Installing NVIDIA GPU Operator...
[INFO] ✓ NVIDIA GPU Operator installation completed successfully

[INFO] Step 3/4: Deploying NVIDIA RAG Blueprint...
[INFO] ✓ NVIDIA RAG Blueprint deployment completed successfully

[INFO] Step 4/4: Validating installation...
[INFO] ✓ Installation validation completed successfully
```

## Post-Installation Verification

### **Step 1: Verify Cluster Status**

```bash
# Check cluster nodes
kubectl get nodes -o wide

# Check all pods
kubectl get pods --all-namespaces

# Check services
kubectl get svc --all-namespaces
```

### **Step 2: Verify GPU Operator**

```bash
# Check GPU operator pods
kubectl get pods -n gpu-operator-resources

# Check GPU nodes
kubectl get nodes -o custom-columns=NAME:.metadata.name,GPU:.status.allocatable.'nvidia\.com/gpu'

# Test GPU functionality
kubectl run gpu-test --image=nvcr.io/nvidia/cuda:11.8.0-base-ubuntu20.04 --rm -it --restart=Never -- nvidia-smi
```

### **Step 3: Verify RAG Services**

```bash
# Check RAG services
kubectl get pods -n rag-system

# Check Milvus
kubectl get pods -n milvus

# Check NeMo services
kubectl get pods -n nemo-system
```

### **Step 4: Verify Observability**

```bash
# Check observability services
kubectl get pods -n observability

# Check Attu
kubectl get pods -n milvus -l app=attu
```

### **Step 5: Test Access**

```bash
# Get master node IP
MASTER_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')

# Test RAG Playground
curl -I http://$MASTER_IP:30081

# Test RAG API
curl -I http://$MASTER_IP:30080/health

# Test Grafana
curl -I http://$MASTER_IP:30671
```

## Troubleshooting

### **Common Issues**

#### **1. SSH Connection Issues**
```bash
# Test SSH connectivity
ssh -i ~/.ssh/id_rsa ubuntu@192.168.1.10

# Check SSH key permissions
chmod 600 ~/.ssh/id_rsa
chmod 700 ~/.ssh

# Verify SSH configuration
ssh -v -i ~/.ssh/id_rsa ubuntu@192.168.1.10
```

#### **2. Kubernetes Installation Failures**
```bash
# Check Kubespray logs
tail -f /opt/kubespray/cluster.log

# Reset failed installation
cd /opt/kubespray
ansible-playbook -i inventory.yml reset.yml

# Check node connectivity
ansible all -i inventory.yml -m ping
```

#### **3. GPU Operator Issues**
```bash
# Check GPU operator status
kubectl get pods -n gpu-operator-resources

# Check GPU driver installation
kubectl logs -n gpu-operator-resources -l app=nvidia-driver-daemonset

# Verify GPU detection
kubectl run gpu-test --image=nvcr.io/nvidia/cuda:11.8.0-base-ubuntu20.04 --rm -it --restart=Never -- nvidia-smi
```

#### **4. RAG Services Issues**
```bash
# Check RAG service logs
kubectl logs -n rag-system deployment/rag-server

# Check Milvus status
kubectl logs -n milvus deployment/milvus-standalone

# Verify service connectivity
kubectl exec -n rag-system deployment/rag-server -- curl -s http://milvus.milvus.svc.cluster.local:19121/health
```

#### **5. Observability Issues**
```bash
# Check observability services
kubectl get pods -n observability

# Check Jaeger logs
kubectl logs -n observability deployment/jaeger-query

# Check Grafana logs
kubectl logs -n observability deployment/prometheus-grafana
```

### **AI-Powered Troubleshooting**

The installer includes AI-powered error handling:

```bash
# Enable AI error handling (default)
./install.sh

# Disable AI error handling
./install.sh --no-ai

# Get AI analysis for specific error
./utils/error_handler.sh 'kubectl get nodes' 'Check cluster' 'Validation'
```

### **Getting Help**

1. **Check Logs**: Review `install.log` for detailed error information
2. **AI Analysis**: Use the built-in AI error handler for automated troubleshooting
3. **Documentation**: Refer to `docs/TROUBLESHOOTING.md` for common solutions
4. **Validation Report**: Check `/tmp/validation_report.txt` for comprehensive status

## Uninstallation

### **Complete Uninstallation**

```bash
# 1. Delete RAG services
kubectl delete namespace rag-system
kubectl delete namespace milvus
kubectl delete namespace nemo-system
kubectl delete namespace observability

# 2. Delete GPU operator
helm uninstall gpu-operator -n gpu-operator-resources
kubectl delete namespace gpu-operator-resources

# 3. Reset Kubernetes cluster
cd /opt/kubespray
ansible-playbook -i inventory.yml reset.yml

# 4. Clean up local files
rm -rf /opt/kubespray
rm -f kubeconfig
```

### **Partial Uninstallation**

```bash
# Remove only RAG services
kubectl delete namespace rag-system
kubectl delete namespace milvus
kubectl delete namespace nemo-system

# Remove only observability
kubectl delete namespace observability

# Remove only GPU operator
helm uninstall gpu-operator -n gpu-operator-resources
```

## Next Steps

After successful installation:

1. **Access the RAG Playground**: `http://<master-ip>:30081`
2. **Configure Monitoring**: Set up alerts in Grafana
3. **Load Sample Data**: Use the ingestor API to add documents
4. **Customize Configuration**: Modify settings in `config/observability.yml`
5. **Scale the Cluster**: Add more worker nodes as needed
6. **Backup Configuration**: Save your inventory and configuration files

## Support

For additional support:

- **Documentation**: Check the `docs/` directory
- **Issues**: Report problems with detailed logs
- **AI Assistance**: Use the built-in AI error handler
- **Community**: Join the discussion forums
