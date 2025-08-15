# Observability Stack Documentation

## Overview

The Kubernetes RAG Installer includes a comprehensive observability stack that provides monitoring, tracing, and management capabilities for the entire RAG pipeline.

## Components

### 🔍 **OpenTelemetry Collector**

**Purpose**: Distributed tracing and metrics collection across all services

**Features**:
- Collects traces, metrics, and logs from all RAG components
- Supports OTLP (OpenTelemetry Protocol) for data ingestion
- Batches data for efficient transmission
- Routes data to appropriate backends (Jaeger, Prometheus)

**Configuration**:
```yaml
mode: daemonset
receivers:
  otlp:
    protocols:
      grpc: 0.0.0.0:4317
      http: 0.0.0.0:4318
```

**Access**: Internal service, no direct external access

---

### 🕵️ **Jaeger - Distributed Tracing**

**Purpose**: Visualize and analyze distributed traces across the RAG pipeline

**Features**:
- Trace visualization and analysis
- Service dependency mapping
- Performance bottleneck identification
- Error tracking across services

**Key Capabilities**:
- **Trace Search**: Find traces by service, operation, or tags
- **Service Graph**: Visualize service dependencies
- **Trace Details**: View detailed trace spans and timing
- **Error Analysis**: Identify and debug distributed errors

**Access**: `http://<master-ip>:30668`

**Usage Examples**:
```bash
# View traces in Jaeger UI
open http://<master-ip>:30668

# Search for traces from RAG services
# In Jaeger UI: Service = "rag-server", Operation = "generate"
```

---

### 📊 **Zipkin - Alternative Tracing**

**Purpose**: Alternative distributed tracing solution with different UI and features

**Features**:
- Lightweight tracing solution
- RESTful API for trace ingestion
- Web-based trace visualization
- Service dependency analysis

**Key Capabilities**:
- **Trace Collection**: Collect traces via HTTP API
- **Trace Visualization**: Web-based trace viewer
- **Service Dependencies**: Map service relationships
- **Performance Analysis**: Analyze request flows

**Access**: `http://<master-ip>:30669`

**API Endpoints**:
```bash
# Send traces to Zipkin
curl -X POST http://<master-ip>:30669/api/v2/spans \
  -H "Content-Type: application/json" \
  -d '[{"traceId":"...","id":"...","name":"rag-query"}]'
```

---

### 🎛️ **Attu - Milvus Management UI**

**Purpose**: Web-based management interface for Milvus vector database

**Features**:
- Collection management and monitoring
- Data insertion and query interface
- Performance metrics and statistics
- Cluster health monitoring

**Key Capabilities**:
- **Collection Management**: Create, delete, and manage collections
- **Data Operations**: Insert, search, and delete vectors
- **Performance Monitoring**: View query performance and statistics
- **Cluster Health**: Monitor Milvus cluster status

**Access**: `http://<master-ip>:30670`

**Usage Examples**:
```bash
# Access Attu UI
open http://<master-ip>:30670

# Create a new collection
# In Attu UI: Collections → Create Collection → Define schema

# Insert test data
# In Attu UI: Collections → Select Collection → Insert Data
```

---

### 📈 **Prometheus + Grafana - Metrics & Monitoring**

**Purpose**: Comprehensive metrics collection and visualization

**Features**:
- Time-series metrics collection
- Custom dashboards for RAG components
- Alerting and notification system
- Performance trend analysis

#### **Prometheus**
- Collects metrics from all services
- Stores time-series data
- Provides query language (PromQL)
- Supports service discovery

#### **Grafana**
- Rich visualization dashboards
- Pre-configured dashboards for:
  - **Milvus**: Vector database metrics
  - **Kubernetes**: Cluster and pod metrics
  - **NVIDIA GPU**: GPU utilization and performance

**Access**: `http://<master-ip>:30671` (admin/admin)

**Pre-configured Dashboards**:
1. **Milvus Dashboard** (ID: 13332)
   - Collection metrics
   - Query performance
   - Storage utilization

2. **Kubernetes Cluster** (ID: 315)
   - Node metrics
   - Pod resource usage
   - Service health

3. **NVIDIA GPU** (ID: 14574)
   - GPU utilization
   - Memory usage
   - Temperature monitoring

## Integration Points

### RAG Services Integration

All RAG services are instrumented to send observability data:

```yaml
# RAG Server with OpenTelemetry
env:
  - name: OTEL_EXPORTER_OTLP_ENDPOINT
    value: "http://otel-collector:4317"
  - name: OTEL_SERVICE_NAME
    value: "rag-server"
```

### Milvus Integration

Milvus automatically exports metrics to Prometheus:

```yaml
# Milvus metrics endpoint
metrics:
  enabled: true
  path: /metrics
  port: 9091
```

### GPU Operator Integration

NVIDIA GPU Operator provides GPU metrics:

```yaml
# DCGM Exporter for GPU metrics
dcgmExporter:
  enabled: true
  service:
    type: ClusterIP
```

## Monitoring Workflows

### 1. **Performance Monitoring**

```bash
# Check RAG query performance
# 1. Open Grafana: http://<master-ip>:30671
# 2. Navigate to Milvus Dashboard
# 3. Monitor query latency and throughput

# Check GPU utilization
# 1. Open Grafana: http://<master-ip>:30671
# 2. Navigate to NVIDIA GPU Dashboard
# 3. Monitor GPU utilization and memory
```

### 2. **Troubleshooting Workflow**

```bash
# 1. Check service health in Grafana
# 2. Identify slow queries in Jaeger
# 3. Analyze trace spans for bottlenecks
# 4. Check Milvus status in Attu
# 5. Verify GPU metrics in Prometheus
```

### 3. **Capacity Planning**

```bash
# 1. Monitor resource usage trends
# 2. Analyze query patterns
# 3. Plan scaling based on metrics
# 4. Optimize based on performance data
```

## Configuration

### Environment Variables

```bash
# OpenTelemetry Configuration
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
OTEL_SERVICE_NAME=rag-server
OTEL_RESOURCE_ATTRIBUTES=service.version=1.0.0

# Jaeger Configuration
JAEGER_AGENT_HOST=jaeger-agent
JAEGER_AGENT_PORT=6831
```

### Custom Dashboards

Create custom Grafana dashboards:

```json
{
  "dashboard": {
    "title": "RAG Pipeline Overview",
    "panels": [
      {
        "title": "Query Latency",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rag_query_duration_seconds_bucket)"
          }
        ]
      }
    ]
  }
}
```

## Troubleshooting

### Common Issues

#### 1. **Jaeger Not Collecting Traces**
```bash
# Check Jaeger collector status
kubectl get pods -n observability -l app.kubernetes.io/name=jaeger

# Check OpenTelemetry collector logs
kubectl logs -n observability -l app.kubernetes.io/name=opentelemetry-collector
```

#### 2. **Grafana Dashboard Not Loading**
```bash
# Check Prometheus connectivity
kubectl port-forward -n observability svc/prometheus-kube-prometheus-prometheus 9090:9090

# Verify data source configuration
# In Grafana: Configuration → Data Sources → Prometheus
```

#### 3. **Attu Connection Issues**
```bash
# Check Milvus service
kubectl get svc -n milvus

# Verify Attu configuration
kubectl get configmap -n milvus attu-config -o yaml
```

### Performance Optimization

#### 1. **Storage Optimization**
```yaml
# Configure retention policies
prometheus:
  retention: 7d  # Reduce retention for cost savings
  storage:
    size: 50Gi   # Adjust based on metrics volume
```

#### 2. **Sampling Configuration**
```yaml
# Configure trace sampling
opentelemetry:
  sampling:
    probability: 0.1  # Sample 10% of traces
```

#### 3. **Resource Limits**
```yaml
# Set appropriate resource limits
resources:
  limits:
    memory: 2Gi
    cpu: 1000m
  requests:
    memory: 1Gi
    cpu: 500m
```

## Security Considerations

### Access Control
- Grafana: admin/admin (change default password)
- Jaeger: No authentication by default
- Zipkin: No authentication by default
- Attu: No authentication by default

### Network Security
- All services use NodePort for external access
- Consider using Ingress with TLS for production
- Implement network policies for service-to-service communication

### Data Privacy
- Traces may contain sensitive information
- Implement trace sampling to reduce data volume
- Configure data retention policies
- Sanitize logs and metrics

## Best Practices

### 1. **Monitoring Strategy**
- Set up alerts for critical metrics
- Use dashboards for operational visibility
- Implement log aggregation
- Regular capacity planning reviews

### 2. **Tracing Strategy**
- Instrument all service boundaries
- Use consistent span naming
- Add business context to traces
- Monitor trace sampling rates

### 3. **Performance Optimization**
- Monitor resource usage
- Optimize query patterns
- Scale based on metrics
- Regular performance reviews

## Future Enhancements

### Planned Features
- **Alerting**: Configure alerts for critical metrics
- **Log Aggregation**: Centralized log collection
- **Custom Dashboards**: RAG-specific monitoring dashboards
- **APM Integration**: Application performance monitoring
- **Cost Optimization**: Resource usage optimization

### Integration Opportunities
- **ELK Stack**: Log aggregation and analysis
- **PagerDuty**: Incident management
- **Slack**: Notifications and alerts
- **Custom Metrics**: Business-specific monitoring
