# Observability Implementation Plan

## 🎯 Current State Assessment

### **Existing Infrastructure**
- ✅ **Zipkin**: Running (zipkin-7d996bcdf7-zc95l)
- ✅ **OTel Collector Service**: Available (otel-collector service exists)
- ❌ **OTel Collector Pod**: Not running (service exists but no pod)
- ❌ **Grafana**: Not deployed
- ❌ **Prometheus**: Not deployed
- ❌ **Jaeger**: Not deployed

### **Services to Instrument**
- **RAG Server**: `rag-server-7f6c9b658-grbt7` (FastAPI)
- **AI-Q Backend**: `aiq-aira-backend-58949648b4-t5pb2` (FastAPI)
- **AI-Q Nginx**: `aiq-aira-nginx-67cf5b6f57-c7pbl` (Nginx proxy)
- **AI-Q Frontend**: `aiq-frontend-6f4bc44f47-zsmzp` (Next.js)
- **RAG Frontend**: `clean-rag-frontend-*` (Next.js)
- **Milvus**: Vector database
- **Redis**: Message broker
- **NVIDIA NIMs**: LLM inference services

## 📊 Effort Assessment

### **Low Effort (1-2 hours)**
- Deploy missing OTel Collector pod
- Deploy Grafana with pre-configured dashboards
- Deploy Prometheus for metrics collection
- Basic service discovery and scraping

### **Medium Effort (3-4 hours)**
- Instrument FastAPI services (RAG Server, AI-Q Backend)
- Configure Nginx access logs and metrics
- Set up custom dashboards for RAG/AI-Q metrics
- Configure alerting rules

### **High Effort (5-6 hours)**
- Instrument Next.js frontends with custom metrics
- Set up distributed tracing across all services
- Configure custom business metrics (query latency, document processing time)
- Set up comprehensive alerting and notification system

## 🚀 Implementation Plan

### **Phase 1: Core Infrastructure (Low Risk, 1-2 hours)**

#### **Step 1.1: Deploy OTel Collector**
```bash
# Create OTel Collector deployment
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: otel-collector
  labels:
    app: otel-collector
spec:
  replicas: 1
  selector:
    matchLabels:
      app: otel-collector
  template:
    metadata:
      labels:
        app: otel-collector
    spec:
      containers:
      - name: otel-collector
        image: otel/opentelemetry-collector-contrib:0.45.0
        args:
          - --config=/etc/otel-collector-config.yaml
        volumeMounts:
        - name: otel-collector-config
          mountPath: /etc/otel-collector-config.yaml
          subPath: otel-collector-config.yaml
        ports:
        - containerPort: 4317
          name: otlp-grpc
        - containerPort: 4318
          name: otlp-http
        - containerPort: 14250
          name: jaeger-grpc
        - containerPort: 14268
          name: jaeger-thrift
        - containerPort: 9411
          name: zipkin
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
      volumes:
      - name: otel-collector-config
        configMap:
          name: otel-collector-config
EOF
```

#### **Step 1.2: Create OTel Collector ConfigMap**
```bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
data:
  otel-collector-config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
          http:
            endpoint: 0.0.0.0:4318
      jaeger:
        protocols:
          grpc:
            endpoint: 0.0.0.0:14250
          thrift_http:
            endpoint: 0.0.0.0:14268
      zipkin:
        endpoint: 0.0.0.0:9411
    
    processors:
      batch:
        timeout: 1s
        send_batch_size: 1024
      memory_limiter:
        limit_mib: 512
    
    exporters:
      jaeger:
        endpoint: jaeger-collector:14250
        tls:
          insecure: true
      zipkin:
        endpoint: http://zipkin:9411/api/v2/spans
      prometheus:
        endpoint: "0.0.0.0:8889"
      logging:
        verbosity: detailed
    
    service:
      pipelines:
        traces:
          receivers: [otlp, jaeger, zipkin]
          processors: [memory_limiter, batch]
          exporters: [jaeger, zipkin, logging]
        metrics:
          receivers: [otlp]
          processors: [memory_limiter, batch]
          exporters: [prometheus, logging]
EOF
```

#### **Step 1.3: Deploy Prometheus**
```bash
# Create Prometheus namespace
kubectl create namespace monitoring

# Deploy Prometheus
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:v2.45.0
        args:
          - --config.file=/etc/prometheus/prometheus.yml
          - --storage.tsdb.path=/prometheus/
          - --web.console.libraries=/etc/prometheus/console_libraries
          - --web.console.templates=/etc/prometheus/consoles
          - --storage.tsdb.retention.time=7d
          - --web.enable-lifecycle
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: prometheus-config
          mountPath: /etc/prometheus
        - name: prometheus-storage
          mountPath: /prometheus
        resources:
          limits:
            memory: "2Gi"
            cpu: "1000m"
          requests:
            memory: "1Gi"
            cpu: "500m"
      volumes:
      - name: prometheus-config
        configMap:
          name: prometheus-config
      - name: prometheus-storage
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: monitoring
spec:
  selector:
    app: prometheus
  ports:
  - port: 9090
    targetPort: 9090
  type: ClusterIP
EOF
```

#### **Step 1.4: Create Prometheus Configuration**
```bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    
    scrape_configs:
    - job_name: 'prometheus'
      static_configs:
      - targets: ['localhost:9090']
    
    - job_name: 'otel-collector'
      static_configs:
      - targets: ['otel-collector:8889']
    
    - job_name: 'rag-server'
      static_configs:
      - targets: ['rag-server:8081']
      metrics_path: '/metrics'
    
    - job_name: 'aiq-backend'
      static_configs:
      - targets: ['aiq-aira-backend:3838']
      metrics_path: '/metrics'
    
    - job_name: 'kubernetes-pods'
      kubernetes_sd_configs:
      - role: pod
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
EOF
```

#### **Step 1.5: Deploy Grafana**
```bash
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:10.0.0
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          value: "admin"
        - name: GF_INSTALL_PLUGINS
          value: "grafana-piechart-panel"
        volumeMounts:
        - name: grafana-storage
          mountPath: /var/lib/grafana
        - name: grafana-datasources
          mountPath: /etc/grafana/provisioning/datasources
        - name: grafana-dashboards
          mountPath: /etc/grafana/provisioning/dashboards
        resources:
          limits:
            memory: "1Gi"
            cpu: "500m"
          requests:
            memory: "512Mi"
            cpu: "250m"
      volumes:
      - name: grafana-storage
        emptyDir: {}
      - name: grafana-datasources
        configMap:
          name: grafana-datasources
      - name: grafana-dashboards
        configMap:
          name: grafana-dashboards
---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: monitoring
spec:
  selector:
    app: grafana
  ports:
  - port: 3000
    targetPort: 3000
  type: NodePort
  nodePort: 30671
EOF
```

### **Phase 2: Service Instrumentation (Medium Risk, 3-4 hours)**

#### **Step 2.1: Instrument RAG Server**
```bash
# Add OTel instrumentation to RAG Server deployment
kubectl patch deployment rag-server -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "rag-server",
          "env": [
            {"name": "OTEL_EXPORTER_OTLP_ENDPOINT", "value": "http://otel-collector:4317"},
            {"name": "OTEL_SERVICE_NAME", "value": "rag-server"},
            {"name": "OTEL_RESOURCE_ATTRIBUTES", "value": "service.name=rag-server,service.version=1.0.0"}
          ]
        }]
      }
    }
  }
}'
```

#### **Step 2.2: Instrument AI-Q Backend**
```bash
# Add OTel instrumentation to AI-Q Backend deployment
kubectl patch deployment aiq-aira-backend -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "aiq-aira-backend",
          "env": [
            {"name": "OTEL_EXPORTER_OTLP_ENDPOINT", "value": "http://otel-collector:4317"},
            {"name": "OTEL_SERVICE_NAME", "value": "aiq-backend"},
            {"name": "OTEL_RESOURCE_ATTRIBUTES", "value": "service.name=aiq-backend,service.version=1.0.0"}
          ]
        }]
      }
    }
  }
}'
```

#### **Step 2.3: Configure Nginx Access Logs**
```bash
# Update AI-Q Nginx ConfigMap for access logging
kubectl patch configmap aiq-aiq-aira-nginx -p '{
  "data": {
    "nginx.conf": "events {}\nhttp {\n  log_format main '\''$remote_addr - $remote_user [$time_local] \"$request\" $status $body_bytes_sent \"$http_referer\" \"$http_user_agent\" $request_time'\'';\n  access_log /var/log/nginx/access.log main;\n  \n  upstream aira_backend { server aiq-aira-backend:3838; }\n  upstream aira_frontend { server aiq-frontend:3001; }\n  \n  server {\n    listen 8051;\n    \n    # Existing configuration...\n  }\n}"
  }
}'
```

### **Phase 3: Advanced Instrumentation (High Value, 5-6 hours)**

#### **Step 3.1: Custom Business Metrics**
```bash
# Create custom metrics for RAG performance
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: custom-metrics-config
data:
  metrics.py: |
    from prometheus_client import Counter, Histogram, Gauge
    import time
    
    # RAG-specific metrics
    rag_queries_total = Counter('rag_queries_total', 'Total RAG queries', ['collection', 'status'])
    rag_query_duration = Histogram('rag_query_duration_seconds', 'RAG query duration', ['collection'])
    rag_documents_processed = Counter('rag_documents_processed_total', 'Documents processed', ['collection', 'status'])
    
    # AI-Q specific metrics
    aiq_research_sessions = Counter('aiq_research_sessions_total', 'AI-Q research sessions', ['collection', 'status'])
    aiq_query_generation_time = Histogram('aiq_query_generation_seconds', 'Query generation time')
    aiq_synthesis_time = Histogram('aiq_synthesis_seconds', 'Document synthesis time')
    
    # System metrics
    active_connections = Gauge('active_connections', 'Active connections')
    memory_usage = Gauge('memory_usage_bytes', 'Memory usage in bytes')
EOF
```

#### **Step 3.2: Distributed Tracing Setup**
```bash
# Create tracing configuration for all services
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: tracing-config
data:
  tracing.yaml: |
    service:
      name: "rag-blueprint"
      version: "1.0.0"
    
    tracing:
      enabled: true
      endpoint: "http://otel-collector:4317"
      sampling_rate: 0.1
      
    metrics:
      enabled: true
      endpoint: "http://otel-collector:4317"
      interval: 30s
EOF
```

## 🔧 Implementation Steps

### **Immediate Actions (No Service Impact)**

1. **Deploy Core Infrastructure** (30 minutes)
   - Deploy OTel Collector
   - Deploy Prometheus
   - Deploy Grafana
   - Configure basic scraping

2. **Test Infrastructure** (15 minutes)
   - Verify all pods are running
   - Test Grafana access
   - Verify Prometheus targets

3. **Configure Basic Dashboards** (30 minutes)
   - Import Kubernetes dashboard
   - Import Milvus dashboard
   - Create basic RAG metrics dashboard

### **Low-Risk Service Updates**

4. **Add Environment Variables** (15 minutes)
   - Add OTel env vars to RAG Server
   - Add OTel env vars to AI-Q Backend
   - Restart deployments

5. **Configure Nginx Logging** (15 minutes)
   - Update Nginx ConfigMap
   - Restart Nginx deployment

6. **Verify Instrumentation** (15 minutes)
   - Check traces in Jaeger
   - Verify metrics in Prometheus
   - Test Grafana dashboards

### **Advanced Features**

7. **Custom Metrics Implementation** (2 hours)
   - Add custom business metrics
   - Create specialized dashboards
   - Set up alerting rules

8. **Distributed Tracing** (2 hours)
   - Configure trace propagation
   - Add custom spans
   - Create trace-based dashboards

## 📊 Expected Outcomes

### **Immediate Benefits**
- **Visibility**: Real-time monitoring of all services
- **Performance**: Query latency and throughput metrics
- **Reliability**: Error rates and success metrics
- **Resource Usage**: CPU, memory, and network utilization

### **Advanced Benefits**
- **Business Metrics**: Document processing rates, research session success
- **Distributed Tracing**: End-to-end request flow visibility
- **Alerting**: Proactive issue detection
- **Capacity Planning**: Resource usage trends and predictions

## 🚨 Risk Mitigation

### **Zero-Downtime Deployment**
- All changes use rolling updates
- Environment variables added without breaking existing functionality
- ConfigMap updates with pod restarts
- No data loss or service interruption

### **Rollback Plan**
- Keep original deployment configurations
- Use `kubectl rollout undo` for quick rollbacks
- Monitor service health during deployment
- Gradual rollout with health checks

### **Testing Strategy**
- Deploy to staging environment first
- Validate all metrics and traces
- Load test with observability enabled
- Monitor for performance impact

## 📈 Success Metrics

### **Technical Metrics**
- **Deployment Time**: < 2 hours for core infrastructure
- **Service Impact**: Zero downtime during deployment
- **Coverage**: 100% of critical services instrumented
- **Performance Impact**: < 5% overhead

### **Operational Metrics**
- **MTTR**: 50% reduction in mean time to resolution
- **Detection Time**: 90% of issues detected within 5 minutes
- **Dashboard Usage**: Daily active users on monitoring dashboards
- **Alert Accuracy**: < 10% false positive rate

## 🎯 Next Steps

1. **Approve Plan**: Review and approve implementation approach
2. **Schedule Deployment**: Plan maintenance window if needed
3. **Prepare Resources**: Ensure adequate cluster resources
4. **Execute Phase 1**: Deploy core infrastructure
5. **Validate and Iterate**: Test and refine based on results

---

**Total Estimated Effort**: 6-8 hours over 2-3 days
**Risk Level**: Low (no service disruption)
**Business Value**: High (comprehensive observability)
**Maintenance**: Minimal (automated dashboards and alerting)
