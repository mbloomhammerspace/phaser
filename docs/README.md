# Kubernetes RAG Installer - Documentation

Welcome to the comprehensive documentation for the Kubernetes RAG Installer. This documentation will help you understand, deploy, and manage your Kubernetes RAG system with GPU support and AI-powered error handling.

## 📚 Documentation Index

### **🚀 Getting Started**

| Document | Description | Time to Read |
|----------|-------------|--------------|
| **[Quick Start Guide](QUICK_START.md)** | Deploy in 10 minutes | 5 min |
| **[Installation Guide](INSTALLATION_GUIDE.md)** | Complete installation instructions | 15 min |
| **[Requirements Guide](REQUIREMENTS_GUIDE.md)** | Hardware and software requirements | 10 min |

### **🔧 Technical Documentation**

| Document | Description | Time to Read |
|----------|-------------|--------------|
| **[AI-Q Research Assistant](AI_Q_RESEARCH_ASSISTANT.md)** | Enterprise AI research agent setup | 15 min |
| **[Observability Guide](OBSERVABILITY.md)** | Monitoring and tracing setup | 10 min |
| **[AI Error Handling](AI_ERROR_HANDLING.md)** | AI-powered troubleshooting | 8 min |

### **📋 Reference Materials**

| Document | Description | Time to Read |
|----------|-------------|--------------|
| **[Troubleshooting Guide](TROUBLESHOOTING.md)** | Common issues and solutions | 10 min |
| **[Configuration Reference](CONFIGURATION.md)** | Configuration options | 5 min |

## 🎯 Quick Navigation

### **For New Users**
1. Start with **[Quick Start Guide](QUICK_START.md)** for immediate deployment
2. Review **[Requirements Guide](REQUIREMENTS_GUIDE.md)** for system planning
3. Follow **[Installation Guide](INSTALLATION_GUIDE.md)** for detailed setup

### **For Administrators**
1. Read **[Observability Guide](OBSERVABILITY.md)** for monitoring setup
2. Study **[AI Error Handling](AI_ERROR_HANDLING.md)** for advanced troubleshooting
3. Reference **[Configuration Reference](CONFIGURATION.md)** for customization

### **For Developers**
1. Review **[Installation Guide](INSTALLATION_GUIDE.md)** for development setup
2. Check **[Observability Guide](OBSERVABILITY.md)** for debugging tools
3. Use **[Troubleshooting Guide](TROUBLESHOOTING.md)** for common issues

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Control       │    │   Master Node   │    │  Worker Nodes   │
│   Machine       │◄──►│   (K8s API)     │◄──►│   (GPU/CPU)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  RAG Services   │
                       │  + Observability│
                       └─────────────────┘
```

## 🚀 Quick Start Commands

### **1. Clone and Setup**
```bash
git clone <repository-url>
cd kubernetes-rag-installer
chmod +x install.sh
pip3 install -r requirements.txt
```

### **2. Run Installation**
```bash
# Interactive mode (recommended)
./install.sh

# With inventory file
./install.sh --inventory my-cluster.yml

# With verbose logging
./install.sh --verbose
```

### **3. Access Your System**
```bash
# Get master node IP
MASTER_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')

# Access URLs (via port-forward)
echo "RAG Playground: http://localhost:3000"
echo "AI-Q Research Assistant: http://localhost:8051"
echo "Grafana: http://$MASTER_IP:30671 (admin/admin)"
echo "Jaeger: http://$MASTER_IP:30668"
```

## 📊 System Components

### **Core Components**
- **Kubernetes Cluster**: Kubespray-based deployment
- **NVIDIA GPU Operator**: GPU management and monitoring
- **NVIDIA RAG Blueprint**: Complete RAG pipeline
- **AI-Q Research Assistant**: Enterprise-grade AI research agent
- **Milvus**: Vector database with GPU acceleration

### **Observability Stack**
- **OpenTelemetry**: Distributed tracing and metrics
- **Jaeger**: Trace visualization and analysis
- **Zipkin**: Alternative tracing solution
- **Attu**: Milvus management UI
- **Prometheus + Grafana**: Metrics and monitoring

### **AI-Powered Features**
- **Error Analysis**: GPT-4 powered troubleshooting
- **Automated Resolution**: Intelligent fix suggestions
- **Diagnostics**: Comprehensive system health checks
- **Interactive Help**: User-guided problem resolution

## 🔧 Configuration Options

### **Installation Options**
```bash
# Basic installation
./install.sh

# Custom inventory
./install.sh --inventory my-cluster.yml

# Verbose logging
./install.sh --verbose

# Disable AI error handling
./install.sh --no-ai

# Help
./install.sh --help
```

### **Environment Variables**
```bash
# OpenAI API for AI error handling
export OPENAI_API_KEY="your-api-key"

# Debug mode
export DEBUG=true

# Custom log level
export LOG_LEVEL=DEBUG
```

## 📈 Performance Expectations

### **Hardware Requirements**
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Master Node** | 4 cores, 8GB RAM | 8 cores, 16GB RAM |
| **Worker Node** | 4 cores, 8GB RAM | 8 cores, 16GB RAM |
| **GPU Node** | 8 cores, 16GB RAM, 1 GPU | 16 cores, 32GB RAM, 2+ GPUs |

### **Performance Metrics**
| Metric | Target | Notes |
|--------|--------|-------|
| **RAG Query Latency** | < 1s (P95) | End-to-end query time |
| **Document Ingestion** | < 5s per document | Processing time |
| **GPU Utilization** | 70-90% | Optimal performance |
| **Cluster Response** | < 100ms | Kubernetes API |

## 🛠️ Troubleshooting

### **Common Issues**
1. **SSH Connection Problems**: Check key permissions and network connectivity
2. **GPU Detection Issues**: Verify NVIDIA drivers and GPU operator
3. **Service Startup Failures**: Check resource constraints and dependencies
4. **Network Connectivity**: Verify firewall rules and DNS resolution

### **AI-Powered Help**
```bash
# Get AI analysis for errors
./utils/error_handler.sh 'kubectl get nodes' 'Check cluster' 'Validation'

# Run cluster diagnostics
source utils/error_handler.sh
run_cluster_diagnostics

# Interactive error resolution
interactive_error_resolution "Error message" "Context"
```

## 📞 Support

### **Getting Help**
1. **Check Logs**: Review `install.log` for detailed information
2. **AI Assistance**: Use the built-in AI error handler
3. **Documentation**: Refer to the guides in this directory
4. **Validation**: Run comprehensive health checks

### **Useful Commands**
```bash
# Check system status
kubectl get nodes -o wide
kubectl get pods --all-namespaces

# View logs
kubectl logs -n rag-system deployment/rag-server
kubectl logs -n gpu-operator-resources deployment/gpu-operator

# Export debug report
python3 utils/ai_debugger.py export_report
```

## 🔄 Updates and Maintenance

### **System Updates**
```bash
# Update Kubernetes components
kubectl upgrade

# Update GPU operator
helm upgrade gpu-operator nvidia/gpu-operator

# Update RAG blueprint
kubectl apply -f playbooks/03-rag-blueprint.yml
```

### **Backup and Recovery**
```bash
# Backup cluster configuration
kubectl get all --all-namespaces -o yaml > backup.yaml

# Backup persistent data
kubectl get pvc --all-namespaces -o yaml > pvc-backup.yaml

# Restore from backup
kubectl apply -f backup.yaml
```

## 📝 Contributing

### **Development Setup**
```bash
# Install development dependencies
pip3 install -r requirements-dev.txt

# Run tests
pytest tests/

# Code formatting
black .
flake8 .
```

### **Documentation Updates**
- Keep guides up to date with code changes
- Add new troubleshooting scenarios
- Update configuration examples
- Improve clarity and completeness

## 📄 License

This project is licensed under the Apache 2.0 License. See the [LICENSE](../LICENSE) file for details.

## 🤝 Community

- **Issues**: Report bugs and feature requests
- **Discussions**: Share experiences and solutions
- **Contributions**: Submit improvements and fixes
- **Documentation**: Help improve guides and examples

---

**Need help?** Start with the [Quick Start Guide](QUICK_START.md) or use the AI-powered error handler for immediate assistance!
