# AI-Q Research Assistant Guide

## 🎯 Overview

The AI-Q Research Assistant is an enterprise-grade AI research agent that provides advanced document analysis, research synthesis, and intelligent query capabilities. Built on NVIDIA's AgentIQ framework, it offers sophisticated reasoning and planning capabilities for complex research tasks.

## 🚀 Features

### Core Capabilities
- **Advanced Research Synthesis**: Automatically analyzes and synthesizes information from multiple sources
- **Intelligent Query Generation**: Creates targeted research questions based on document content
- **Multi-Modal Analysis**: Processes text, PDFs, and other document formats
- **Enterprise Integration**: Seamlessly integrates with existing data sources and workflows
- **Real-time Processing**: Fast document ingestion and analysis capabilities

### AI Models
- **Primary LLM**: Llama 3.3 Nemotron Super (70B parameters)
- **Embedding Model**: NVIDIA NeMo Retriever
- **Vector Database**: Milvus with GPU acceleration
- **Reasoning Engine**: Advanced planning and reflection capabilities

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI-Q Research Assistant                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Frontend  │  │   Backend    │  │   Nginx     │            │
│  │  (Next.js)  │  │  (FastAPI)   │  │  (Proxy)   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Milvus    │  │   NIM        │  │   Redis    │            │
│  │  Vector DB  │  │  (LLM)       │  │  (Cache)   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Deployment

### Prerequisites
- Kubernetes cluster with GPU support
- NVIDIA GPU Operator installed
- Milvus vector database running
- Redis for caching and message queuing

### Helm Chart Deployment

```bash
# Deploy AI-Q Research Assistant
helm install aiq ./charts/aiq-research-assistant

# Check deployment status
kubectl get pods -l app.kubernetes.io/name=aiq-research-assistant
```

### Port-Forwarding Setup

```bash
# Access AI-Q Research Assistant
kubectl port-forward service/aiq-aira-nginx 8051:8051

# Access in browser
open http://localhost:8051
```

## 📊 Configuration

### Environment Variables

#### Backend Configuration
```yaml
backend:
  env:
    TAVILY_API_KEY: "your-tavily-api-key"
    OPENAI_API_KEY: "NVIDIA_API_KEY"
    OPENAI_BASE_URL: "http://nim-llm:8000/v1"
    OPENAI_MODEL: "meta/llama-3.3-70b-instruct"
    AIRA_HOSTED_NIMS: "true"
```

#### Frontend Configuration
```yaml
frontend:
  env:
    NVWB_TRIM_PREFIX: "true"
    INFERENCE_ORIGIN: "http://localhost:8051"
    NODE_ENV: "production"
    NEXT_PUBLIC_APP_ENV: "production"
    NEXT_PUBLIC_APP_URL: "http://localhost:8051"
```

### Custom Collections

Create custom collections for specific research domains:

```yaml
# aiq-custom-config.yaml
general:
  use_uvloop: true
  front_end:
    _type: fastapi
    endpoints:
      - path: /generate_query
        method: POST
        description: Creates the query
        function_name: generate_query
      - path: /generate_summary
        method: POST
        description: Generates the summary
        function_name: generate_summary
      - path: /artifact_qa
        method: POST
        description: Q/A or chat about a previously generated artifact
        function_name: artifact_qa

functions:
  generate_query:
    _type: generate_queries
  generate_summary:
    _type: generate_summaries
    rag_url: http://rag-server:8081/v1
  artifact_qa:
    _type: artifact_qa
    llm_name: instruct_llm
    rag_url: http://rag-server:8081/v1

default_collections:
  collections:
    - name: "Biomedical_Dataset"
      topic: "Biomedical"
      report_organization: "You are a medical researcher who specializes in cystic fibrosis..."
    - name: "Financial_Dataset"
      topic: "Financial"
      report_organization: "You are a financial analyst who specializes in financial statement analysis..."
```

## 🎯 Usage

### Accessing the Interface

1. **Open the AI-Q Research Assistant**: Navigate to `http://localhost:8051`
2. **Select a Collection**: Choose from available research collections
3. **Configure Reasoning Model**: Select "Llama Nemotron Super" for best results
4. **Begin Research**: Click "Begin Researching" to start your research session

### Research Workflow

1. **Collection Selection**: Choose the appropriate research domain
2. **Query Generation**: The system automatically generates research questions
3. **Document Analysis**: AI analyzes relevant documents and sources
4. **Synthesis**: Information is synthesized into comprehensive reports
5. **Refinement**: Results can be refined through iterative questioning

### API Endpoints

#### Collections
```bash
# Get available collections
curl http://localhost:8051/collections

# Response:
{
  "value": [
    {
      "name": "Biomedical_Dataset",
      "topic": "Biomedical",
      "report_organization": "You are a medical researcher..."
    }
  ]
}
```

#### Health Check
```bash
# Check system health
curl http://localhost:8051/health

# Response:
{
  "value": {
    "status": "OK"
  }
}
```

## 🔍 Troubleshooting

### Common Issues

#### Frontend White Screen
**Problem**: AI-Q frontend shows white screen with "Application error"
**Solution**: Check environment variables for consistency:
```bash
# Ensure all environment variables are set to production
NODE_ENV=production
NEXT_PUBLIC_APP_ENV=production
```

#### Backend Connection Issues
**Problem**: Frontend cannot connect to backend
**Solution**: Verify nginx proxy configuration:
```bash
# Check nginx logs
kubectl logs -l app=aiq-aira-nginx

# Verify backend is running
kubectl get pods -l app=aiq-aira-backend
```

#### Collections Not Loading
**Problem**: No collections available in dropdown
**Solution**: Check backend configuration and custom config:
```bash
# Check backend logs
kubectl logs -l app=aiq-aira-backend

# Verify custom config is applied
kubectl get configmap aiq-custom-config
```

### Health Checks

```bash
# Check all AI-Q components
kubectl get pods -l app.kubernetes.io/name=aiq-research-assistant

# Check services
kubectl get svc -l app.kubernetes.io/name=aiq-research-assistant

# Check logs
kubectl logs -l app=aiq-aira-backend
kubectl logs -l app=aiq-aira-nginx
kubectl logs -l app=aiq-frontend
```

## 📈 Performance Optimization

### GPU Utilization
- Ensure GPU resources are properly allocated
- Monitor GPU memory usage during research tasks
- Scale NIM instances based on workload

### Memory Management
- Configure appropriate memory limits for backend
- Monitor Redis memory usage
- Optimize vector database performance

### Network Optimization
- Use high-bandwidth connections for large document uploads
- Configure appropriate timeouts for long-running research tasks
- Monitor network latency between components

## 🔒 Security Considerations

### API Security
- Implement authentication for production deployments
- Use HTTPS for all communications
- Configure CORS policies appropriately

### Data Privacy
- Ensure sensitive documents are properly secured
- Implement data retention policies
- Monitor access logs for compliance

### Network Security
- Use network policies to restrict access
- Implement proper RBAC for Kubernetes resources
- Monitor for unauthorized access attempts

## 📚 Additional Resources

- [NVIDIA AgentIQ Documentation](https://github.com/NVIDIA/AgentIQ)
- [Milvus Vector Database](https://milvus.io/docs)
- [NVIDIA NIM Documentation](https://docs.nvidia.com/nim/)
- [Kubernetes Port-Forwarding](https://kubernetes.io/docs/tasks/access-application-cluster/port-forward-access-application-cluster/)

## 🆘 Support

For issues specific to AI-Q Research Assistant:
1. Check the troubleshooting section above
2. Review component logs for error messages
3. Verify all prerequisites are met
4. Check network connectivity between components
5. Open an issue with detailed logs and configuration
