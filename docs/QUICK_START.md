# Kubernetes RAG Installer - Quick Start Guide

## 🚀 Get Started in 10 Minutes

This quick start guide will help you deploy a Kubernetes RAG system with GPU support in under 10 minutes.

## Prerequisites Checklist

### ✅ **Control Machine**
- [ ] Ubuntu 20.04+ or macOS 10.15+
- [ ] Python 3.8+
- [ ] SSH key pair
- [ ] Internet connection

### ✅ **Target Hosts**
- [ ] Ubuntu 20.04+ (3 nodes minimum)
- [ ] 4+ CPU cores per node
- [ ] 8GB+ RAM per node
- [ ] 50GB+ storage per node
- [ ] NVIDIA GPU (optional, for GPU workloads)

## Quick Installation

### **Step 1: Clone and Setup**

```bash
# Clone the repository
git clone <repository-url>
cd kubernetes-rag-installer

# Make installer executable
chmod +x install.sh

# Install Python dependencies
pip3 install -r requirements.txt
```

### **Step 2: Prepare Your Nodes**

#### **On each target node (Ubuntu):**
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install required packages
sudo apt-get install -y python3 python3-pip curl wget

# Configure SSH (add your public key)
mkdir -p ~/.ssh
echo "YOUR_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# Set hostnames
sudo hostnamectl set-hostname master1  # or worker1, worker2
```

### **Step 3: Run Interactive Installation**

```bash
# Start the installer
./install.sh

# Follow the prompts:
# 1. SSH key path: ~/.ssh/id_rsa
# 2. Master node: master1, 192.168.1.10, ubuntu
# 3. Worker nodes: worker1 (192.168.1.11, GPU), worker2 (192.168.1.12, no GPU)
# 4. Confirm and wait for installation
```

### **Step 4: Verify Installation**

```bash
# Check cluster status
kubectl get nodes

# Check all services
kubectl get pods --all-namespaces

# Test GPU (if available)
kubectl run gpu-test --image=nvcr.io/nvidia/cuda:11.8.0-base-ubuntu20.04 --rm -it --restart=Never -- nvidia-smi
```

## Access Your RAG System

### **Get Your Access URLs**

```bash
# Get master node IP
MASTER_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')

echo "🎉 Your RAG system is ready!"
echo ""
echo "📋 Access URLs:"
echo "• RAG Playground: http://$MASTER_IP:30081"
echo "• RAG API: http://$MASTER_IP:30080"
echo "• Grafana (Monitoring): http://$MASTER_IP:30671 (admin/admin)"
echo "• Jaeger (Tracing): http://$MASTER_IP:30668"
echo "• Attu (Milvus UI): http://$MASTER_IP:30670"
```

## Quick Test

### **Test RAG API**

```bash
# Test health endpoint
curl http://$MASTER_IP:30080/health

# Test query endpoint
curl -X POST http://$MASTER_IP:30080/generate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the NVIDIA RAG blueprint?",
    "max_tokens": 100
  }'
```

### **Test Document Ingestion**

```bash
# Create test document
echo "This is a test document about Kubernetes and RAG systems." > test_doc.txt

# Ingest document
curl -X POST http://$MASTER_IP:30082/documents \
  -H "Content-Type: application/json" \
  -d '{
    "file": "'$(base64 -w 0 test_doc.txt)'",
    "filename": "test_doc.txt",
    "metadata": {
      "source": "quick_start",
      "category": "test"
    }
  }'
```

## Common Commands

### **Cluster Management**

```bash
# Check cluster status
kubectl get nodes -o wide

# Check all pods
kubectl get pods --all-namespaces

# Check services
kubectl get svc --all-namespaces

# Check GPU resources
kubectl get nodes -o custom-columns=NAME:.metadata.name,GPU:.status.allocatable.'nvidia\.com/gpu'
```

### **Service Management**

```bash
# Check RAG services
kubectl get pods -n rag-system

# Check GPU operator
kubectl get pods -n gpu-operator-resources

# Check observability
kubectl get pods -n observability

# Check Milvus
kubectl get pods -n milvus
```

### **Logs and Debugging**

```bash
# View RAG server logs
kubectl logs -n rag-system deployment/rag-server

# View GPU operator logs
kubectl logs -n gpu-operator-resources deployment/gpu-operator

# View Milvus logs
kubectl logs -n milvus deployment/milvus-standalone

# Get AI-powered error analysis
./utils/error_handler.sh 'kubectl get nodes' 'Check cluster' 'Validation'
```

## Troubleshooting

### **Quick Fixes**

#### **SSH Connection Issues**
```bash
# Test SSH connectivity
ssh -i ~/.ssh/id_rsa ubuntu@192.168.1.10

# Fix SSH key permissions
chmod 600 ~/.ssh/id_rsa
chmod 700 ~/.ssh
```

#### **Installation Failures**
```bash
# Check installation logs
tail -f install.log

# Use AI error handling
./install.sh --verbose

# Reset and retry
cd /opt/kubespray
ansible-playbook -i inventory.yml reset.yml
```

#### **GPU Issues**
```bash
# Check GPU operator status
kubectl get pods -n gpu-operator-resources

# Test GPU functionality
kubectl run gpu-test --image=nvcr.io/nvidia/cuda:11.8.0-base-ubuntu20.04 --rm -it --restart=Never -- nvidia-smi

# Check GPU nodes
kubectl get nodes -o custom-columns=NAME:.metadata.name,GPU:.status.allocatable.'nvidia\.com/gpu'
```

## Next Steps

### **1. Load Your Data**
```bash
# Use the ingestor API to add your documents
curl -X POST http://$MASTER_IP:30082/documents \
  -H "Content-Type: application/json" \
  -d '{
    "file": "'$(base64 -w 0 your_document.pdf)'",
    "filename": "your_document.pdf",
    "metadata": {
      "source": "your_source",
      "category": "your_category"
    }
  }'
```

### **2. Configure Monitoring**
- Access Grafana: `http://$MASTER_IP:30671`
- Set up alerts for critical metrics
- Monitor GPU utilization
- Track RAG query performance

### **3. Scale Your Cluster**
```bash
# Add more worker nodes
# Edit your inventory file and re-run installation
./install.sh --inventory my-cluster.yml
```

### **4. Customize Configuration**
```bash
# Edit observability configuration
vim config/observability.yml

# Edit RAG settings
vim playbooks/03-rag-blueprint.yml
```

## Support

### **Getting Help**

1. **Check Logs**: Review `install.log` for detailed information
2. **AI Assistance**: Use the built-in AI error handler
3. **Documentation**: Read the full guides in `docs/`
4. **Validation**: Run `./install.sh --verbose` for detailed output

### **Useful Resources**

- **Full Installation Guide**: `docs/INSTALLATION_GUIDE.md`
- **Requirements Guide**: `docs/REQUIREMENTS_GUIDE.md`
- **Observability Guide**: `docs/OBSERVABILITY.md`
- **AI Error Handling**: `docs/AI_ERROR_HANDLING.md`

## Success! 🎉

You now have a fully functional Kubernetes RAG system with:
- ✅ Kubernetes cluster with GPU support
- ✅ NVIDIA RAG blueprint deployed
- ✅ Complete observability stack
- ✅ AI-powered error handling
- ✅ Production-ready monitoring

Start exploring your RAG system at `http://$MASTER_IP:30081`!
