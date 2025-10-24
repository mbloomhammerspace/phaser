# NeMo Agent Toolkit Helm Chart

This Helm chart deploys the NVIDIA NeMo Agent Toolkit on Kubernetes. The NeMo Agent Toolkit is an open-source library for efficiently connecting and optimizing teams of AI agents.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- NVIDIA API Key (for using NVIDIA NIMs)

## Installation

### 1. Add the chart repository (if published)
```bash
helm repo add nemo-agent-toolkit https://charts.example.com/
helm repo update
```

### 2. Install the chart
```bash
# Basic installation
helm install nemo-agent-toolkit ./charts/nemo-agent-toolkit

# With custom values
helm install nemo-agent-toolkit ./charts/nemo-agent-toolkit \
  --set nemoAgent.nvidiaApiKey="your-api-key-here" \
  --set service.type=NodePort \
  --set service.nodePort=30080
```

### 3. Access the application
```bash
# Port forward to access locally
kubectl port-forward svc/nemo-agent-toolkit 8080:8000

# Or if using NodePort
kubectl get svc nemo-agent-toolkit
```

## Configuration

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `nemoAgent.nvidiaApiKey` | NVIDIA API Key for NIMs | `""` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `8000` |
| `mcp.enabled` | Enable MCP server | `true` |
| `mcp.port` | MCP server port | `8001` |
| `persistence.enabled` | Enable persistent storage | `true` |
| `persistence.size` | Storage size | `10Gi` |

### Workflow Configuration

The chart includes a default workflow configuration that can be customized:

```yaml
nemoAgent:
  workflow:
    config: |
      functions:
        wikipedia_search:
          _type: wiki_search
          max_results: 2
      
      llms:
        nim_llm:
          _type: nim
          model_name: meta/llama-3.1-70b-instruct
          temperature: 0.0
      
      workflow:
        _type: react_agent
        tool_names: [wikipedia_search]
        llm_name: nim_llm
        verbose: true
        parse_agent_response_max_retries: 3
```

## Usage Examples

### 1. Test the installation
```bash
kubectl exec -it deployment/nemo-agent-toolkit -- nat --version
```

### 2. Run a sample workflow
```bash
kubectl exec -it deployment/nemo-agent-toolkit -- nat run --config_file /app/workflows/workflow.yml --input "List five subspecies of Aardvarks"
```

### 3. Access the API
```bash
# Port forward first
kubectl port-forward svc/nemo-agent-toolkit 8080:8000

# Then access the API
curl http://localhost:8080/health
```

## MCP (Model Context Protocol) Support

The chart includes built-in MCP server support:

```yaml
mcp:
  enabled: true
  port: 8001
  config:
    servers:
      - name: "nemo-agent-server"
        command: "nat"
        args: ["run", "--config_file", "/app/workflows/workflow.yml"]
```

## Observability

The chart supports OpenTelemetry integration:

```yaml
observability:
  enabled: true
  otel:
    enabled: true
    endpoint: "http://otel-collector:4317"
  metrics:
    enabled: true
    port: 9090
  tracing:
    enabled: true
    serviceName: "nemo-agent-toolkit"
```

## Persistence

By default, the chart creates a PersistentVolumeClaim for storing workflow data and cache:

```yaml
persistence:
  enabled: true
  storageClass: ""
  accessMode: ReadWriteOnce
  size: 10Gi
```

## Scaling

The chart supports horizontal pod autoscaling:

```yaml
autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

## Uninstalling

```bash
helm uninstall nemo-agent-toolkit
```

## Troubleshooting

### Common Issues

1. **Image pull errors**: Ensure you have access to the Python base image
2. **API key issues**: Verify your NVIDIA API key is correctly set
3. **Resource constraints**: Check if your cluster has sufficient resources

### Debug Commands

```bash
# Check pod status
kubectl get pods -l app.kubernetes.io/name=nemo-agent-toolkit

# View logs
kubectl logs -l app.kubernetes.io/name=nemo-agent-toolkit

# Describe pod for events
kubectl describe pod -l app.kubernetes.io/name=nemo-agent-toolkit
```

## Contributing

To contribute to this Helm chart:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the chart
5. Submit a pull request

## License

This chart is licensed under the Apache 2.0 License.
