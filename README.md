# Kubernetes RAG Installer with CSI Storage

A comprehensive installer for deploying a production-ready Kubernetes cluster with NVIDIA RAG (Retrieval Augmented Generation) capabilities, featuring advanced storage management with CSI drivers, NFS servers, and local disk discovery.

## 📋 Product Requirements Document (PRD)

### 🎯 **Product Vision**
Enable organizations to rapidly deploy and operate production-ready RAG (Retrieval Augmented Generation) systems on Kubernetes with enterprise-grade storage, monitoring, and operational capabilities.

### 🎯 **Problem Statement**
Organizations need to deploy complex RAG systems that combine vector databases, AI models, and document processing pipelines. Manual deployment is error-prone, time-consuming, and lacks standardization. Existing solutions don't provide comprehensive storage management, observability, or automated hardware discovery.

### 🎯 **Solution Overview**
An automated, production-ready installer that deploys a complete RAG ecosystem on Kubernetes with:
- **Automated Infrastructure**: Kubernetes cluster with GPU support
- **Intelligent Storage**: CSI-based storage with automatic disk discovery
- **Complete RAG Stack**: Milvus, NeMo Retriever, and RAG Playground
- **Enterprise Observability**: Comprehensive monitoring and tracing
- **AI-Powered Operations**: Intelligent error handling and diagnostics

### 🎯 **Target Users**
- **DevOps Engineers**: Need to deploy and manage RAG infrastructure
- **ML Engineers**: Require GPU-accelerated AI workloads
- **Data Scientists**: Need vector databases and document processing
- **Platform Teams**: Require standardized, repeatable deployments
- **Enterprise IT**: Need production-ready, monitored systems

### 🎯 **Key Requirements**

#### **Functional Requirements**
1. **Automated Kubernetes Deployment**
   - Production-ready cluster using Kubespray
   - Support for multiple node types (master, worker, GPU worker)
   - Automatic hardware discovery and role assignment
   - GPU operator integration for NVIDIA GPUs

2. **Intelligent Storage Management**
   - Automatic disk discovery and classification
   - NFS server setup with CSI driver integration
   - Multiple storage classes (default, local, fast)
   - Persistent volume management

3. **Complete RAG Stack**
   - Milvus vector database with GPU acceleration
   - NeMo Retriever for document processing
   - RAG Playground for user interaction
   - Ingestor server for data ingestion

4. **Enterprise Observability**
   - Prometheus + Grafana for metrics
   - Jaeger + Zipkin for distributed tracing
   - Attu for Milvus management
   - Pre-configured dashboards

5. **AI-Powered Operations**
   - OpenAI GPT-4 integration for error analysis
   - Automated diagnostics and troubleshooting
   - Intelligent retry mechanisms
   - Comprehensive logging

#### **Non-Functional Requirements**
1. **Performance**
   - Support for high-performance GPU workloads
   - Optimized storage for vector operations
   - Scalable architecture for growth

2. **Reliability**
   - Production-ready error handling
   - Comprehensive validation and health checks
   - Automated recovery mechanisms

3. **Security**
   - SSH key-based authentication
   - Secure storage configuration
   - Network isolation capabilities

4. **Usability**
   - Interactive wizard interface
   - Comprehensive documentation
   - Multiple deployment methods

5. **Maintainability**
   - Modular Ansible playbooks
   - Configuration management
   - Easy updates and upgrades

### 🎯 **Success Metrics**
- **Deployment Time**: < 30 minutes for complete RAG stack
- **Success Rate**: > 95% successful deployments
- **Time to Value**: < 1 hour from start to first RAG query
- **Operational Efficiency**: 90% reduction in manual configuration
- **Error Resolution**: 80% faster troubleshooting with AI assistance

### 🎯 **Technical Constraints**
- **Hardware**: Minimum 4 CPU cores, 8GB RAM per node
- **Network**: 1Gbps+ connectivity between nodes
- **Storage**: 50GB+ per node, NVMe/SSD preferred
- **GPU**: NVIDIA GPUs with 8GB+ VRAM for GPU workloads (A100, H100, V100, RTX 4090/4080, M6000, L40, T4, L4, RTX 6000 Ada)
- **OS**: Ubuntu 20.04+ or CentOS 8+

### 🎯 **Future Roadmap**
- **Multi-Cloud Support**: AWS, Azure, GCP integration
- **Advanced Storage**: Ceph, Longhorn integration
- **Security Enhancements**: RBAC, network policies
- **Auto-Scaling**: Horizontal pod autoscaling
- **Backup/Recovery**: Automated backup solutions
- **CI/CD Integration**: GitOps workflows

## 🚀 Features

- **Automated Kubernetes Deployment**: Production-ready Kubernetes cluster using Kubespray
- **GPU Support**: NVIDIA GPU Operator integration for GPU-accelerated workloads
- **NVIDIA RAG Blueprint**: Complete RAG pipeline with Milvus, NeMo Retriever, and RAG Playground
- **Wizard Interface**: Interactive setup with inventory file support
- **Comprehensive Logging**: Detailed logging and error tracking
- **SSH Key Authentication**: Secure remote host access
- **Preflight Discovery**: Automatic hardware detection and optimal deployment planning
- **AI-Powered Error Handling**: Intelligent troubleshooting with OpenAI integration
- **CSI Storage Integration**: Advanced storage management with NFS and local disk discovery
- **Observability Stack**: Complete monitoring with Prometheus, Grafana, Jaeger, Zipkin, and Attu

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Kubernetes RAG Cluster                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Master    │  │   Worker    │  │ GPU Worker  │            │
│  │   Node      │  │   Node      │  │   Node      │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Storage Layer                            │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │   NFS       │  │   CSI       │  │   Local     │        │ │
│  │  │  Server     │  │  Driver     │  │  Storage    │        │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                  RAG Components                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │   Milvus    │  │   NeMo      │  │   RAG       │        │ │
│  │  │  Vector DB  │  │  Retriever  │  │ Playground  │        │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                Observability Stack                         │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │ Prometheus  │  │   Grafana   │  │   Jaeger    │        │ │
│  │  │ + Grafana   │  │  Dashboards │  │  Tracing    │        │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

> 📖 **For detailed requirements, see [docs/REQUIREMENTS_GUIDE.md](docs/REQUIREMENTS_GUIDE.md)**

### Hardware Requirements
- **Master Node**: 4+ CPU cores, 8GB+ RAM, 50GB+ storage
- **Worker Nodes**: 8+ CPU cores, 16GB+ RAM, 100GB+ storage
- **GPU Worker Nodes**: NVIDIA GPU(s) with 8GB+ VRAM
- **Network**: 1Gbps+ connectivity between nodes

### Software Requirements
- **Operating System**: Ubuntu 20.04+ or CentOS 8+
- **SSH Access**: Key-based authentication to all nodes
- **Python**: 3.8+ with pip
- **Ansible**: 2.12+
- **OpenAI API Key**: For AI-powered error handling (optional)

## 🚀 Quick Start

> 📖 **For detailed installation instructions, see [docs/QUICK_START.md](docs/QUICK_START.md)**

### Method 1: Automatic Discovery (Recommended)

```bash
# Run with automatic hardware discovery
./install.sh --preflight

# Follow the interactive prompts to configure your nodes
```

### Method 2: Manual Configuration

```bash
# Run the wizard interface
./install.sh --wizard

# Or use an existing inventory file
./install.sh --inventory my-inventory.yml
```

### Method 3: Standalone Discovery

```bash
# Run discovery only to generate inventory
./install.sh --discovery-only --nodes nodes.txt

# Then install with generated inventory
./install.sh --inventory discovery/inventory.yml
```

### Access Your RAG System

After installation, access your services at:

- **RAG Playground**: http://MASTER_IP:30081
- **Grafana**: http://MASTER_IP:30671 (admin/admin)
- **Jaeger**: http://MASTER_IP:30668
- **Zipkin**: http://MASTER_IP:30669
- **Attu (Milvus UI)**: http://MASTER_IP:30670

## 🔧 Configuration

> 📖 **For detailed configuration options, see [docs/INSTALLATION_GUIDE.md](docs/INSTALLATION_GUIDE.md)**

### Inventory Format

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
        worker1:
          ansible_host: 192.168.1.11
          ansible_user: ubuntu
          ansible_ssh_private_key_file: ~/.ssh/id_rsa
          gpu_enabled: true
```

### Storage Configuration

> 📖 **For detailed storage configuration, see [docs/STORAGE.md](docs/STORAGE.md)**

The installer automatically discovers and configures storage:

- **NFS Server**: Centralized storage for shared data
- **CSI Driver**: NFS CSI driver for Kubernetes integration
- **Local Storage**: High-performance local storage for GPU workloads
- **Storage Classes**: 
  - `default`: NFS-based storage for general workloads
  - `local-storage`: High-performance local storage
  - `fast-storage`: NVMe/SSD-based storage

## 📦 Components

### Core Components
- **Kubespray**: Production-ready Kubernetes cluster installer
- **NVIDIA GPU Operator**: GPU driver and device plugin management
- **NVIDIA RAG Blueprint**: Complete RAG pipeline implementation
- **Milvus**: Vector database with GPU acceleration
- **NeMo Retriever**: Document processing and embedding services

### Storage Components
- **NFS Server**: Network file system for shared storage
- **CSI Driver**: Container Storage Interface for Kubernetes
- **Local Storage**: High-performance local disk storage
- **Disk Discovery**: Automatic hardware detection and configuration

### Observability Components
- **OpenTelemetry Collector**: Unified data collection
- **Jaeger**: Distributed tracing system
- **Zipkin**: Alternative tracing system
- **Attu**: Web-based Milvus management interface
- **Prometheus + Grafana**: Metrics collection and visualization

## 🛠️ Installation Steps

1. **Kubernetes Cluster**: Deploy production-ready Kubernetes with Kubespray
2. **Storage Setup**: Configure CSI storage with NFS and local disk discovery
3. **GPU Operator**: Install NVIDIA GPU Operator for GPU support
4. **RAG Blueprint**: Deploy NVIDIA RAG Blueprint with all components
5. **Validation**: Comprehensive validation and health checks

## 📊 Monitoring

> 📖 **For detailed monitoring setup, see [docs/OBSERVABILITY.md](docs/OBSERVABILITY.md)**

### Built-in Dashboards
- **Kubernetes Cluster**: Node and pod metrics
- **NVIDIA GPU**: GPU utilization and memory usage
- **Milvus**: Vector database performance metrics
- **Storage**: NFS and local storage usage

### Metrics Collected
- Cluster health and performance
- GPU utilization and memory usage
- Storage usage and performance
- Application-specific metrics
- Distributed tracing data

## 🔍 Troubleshooting

> 📖 **For comprehensive troubleshooting, see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)**

### AI-Powered Error Handling
The installer includes AI-powered error analysis using OpenAI's GPT-4:

```bash
# Enable AI error handling (requires OpenAI API key)
export OPENAI_API_KEY="your-api-key"
./install.sh --wizard
```

### Manual Troubleshooting
```bash
# Check cluster status
kubectl get nodes
kubectl get pods --all-namespaces

# Check storage
kubectl get storageclass
kubectl get pv
kubectl get pvc --all-namespaces

# Check GPU operator
kubectl get pods -n gpu-operator-resources

# Check RAG services
kubectl get pods -n rag-system
```

## 📚 Documentation

> 📖 **Start here: [Documentation Index](docs/README.md)**

### Core Documentation
- [📋 Installation Guide](docs/INSTALLATION_GUIDE.md) - Complete installation instructions
- [📋 Requirements Guide](docs/REQUIREMENTS_GUIDE.md) - Hardware and software requirements
- [🚀 Quick Start Guide](docs/QUICK_START.md) - Get up and running quickly

### Feature Documentation
- [💾 Storage Configuration](docs/STORAGE.md) - CSI storage and NFS setup
- [📊 Observability Guide](docs/OBSERVABILITY.md) - Monitoring and tracing setup
- [🔍 Preflight Discovery](docs/PREFLIGHT_DISCOVERY.md) - Hardware discovery and planning

### Additional Resources
- [🔧 Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Common issues and solutions
- [📖 Documentation Index](docs/README.md) - Complete documentation overview

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- 📖 **Start with the [Documentation Index](docs/README.md)**
- 🔍 **Check the [Troubleshooting Guide](docs/TROUBLESHOOTING.md)**
- 🐛 **Open an issue on [GitHub](https://github.com/mbloomhammerspace/phaser/issues)**

---

**Note**: This installer is designed for production use and includes comprehensive error handling, monitoring, and validation. Always test in a non-production environment first.
