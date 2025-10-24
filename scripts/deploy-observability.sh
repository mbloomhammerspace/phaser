#!/bin/bash

# Observability Deployment Script
# This script deploys OpenTelemetry, Zipkin, Grafana, and Prometheus
# for comprehensive monitoring of the RAG Blueprint and AI-Q Research Assistant

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create monitoring namespace
create_namespace() {
    log_info "Creating monitoring namespace..."
    
    kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "Monitoring namespace created"
}

# Deploy OpenTelemetry Collector
deploy_otel_collector() {
    log_info "Deploying OpenTelemetry Collector..."
    
    # Create OTel Collector ConfigMap
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

    # Deploy OTel Collector
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
        - containerPort: 8889
          name: prometheus
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

    log_success "OpenTelemetry Collector deployed"
}

# Deploy Prometheus
deploy_prometheus() {
    log_info "Deploying Prometheus..."
    
    # Create Prometheus ConfigMap
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

    log_success "Prometheus deployed"
}

# Deploy Grafana
deploy_grafana() {
    log_info "Deploying Grafana..."
    
    # Create Grafana datasources ConfigMap
    kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-datasources
  namespace: monitoring
data:
  datasources.yaml: |
    apiVersion: 1
    datasources:
    - name: Prometheus
      type: prometheus
      access: proxy
      url: http://prometheus:9090
      isDefault: true
      editable: true
EOF

    # Deploy Grafana
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

    log_success "Grafana deployed"
}

# Deploy Jaeger
deploy_jaeger() {
    log_info "Deploying Jaeger..."
    
    kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger-collector
  labels:
    app: jaeger-collector
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jaeger-collector
  template:
    metadata:
      labels:
        app: jaeger-collector
    spec:
      containers:
      - name: jaeger-collector
        image: jaegertracing/jaeger-collector:1.45
        args:
          - --collector.grpc.host-port=0.0.0.0:14250
          - --collector.http.host-port=0.0.0.0:14268
        ports:
        - containerPort: 14250
          name: grpc
        - containerPort: 14268
          name: http
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
---
apiVersion: v1
kind: Service
metadata:
  name: jaeger-collector
  labels:
    app: jaeger-collector
spec:
  ports:
  - port: 14250
    targetPort: 14250
    name: grpc
  - port: 14268
    targetPort: 14268
    name: http
  selector:
    app: jaeger-collector
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger-query
  labels:
    app: jaeger-query
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jaeger-query
  template:
    metadata:
      labels:
        app: jaeger-query
    spec:
      containers:
      - name: jaeger-query
        image: jaegertracing/jaeger-query:1.45
        args:
          - --query.base-path=/
          - --query.static-files=/etc/jaeger/static
          - --collector.host-port=jaeger-collector:14250
        ports:
        - containerPort: 16686
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
---
apiVersion: v1
kind: Service
metadata:
  name: jaeger-query
  labels:
    app: jaeger-query
spec:
  ports:
  - port: 16686
    targetPort: 16686
  selector:
    app: jaeger-query
  type: NodePort
  nodePort: 30668
EOF

    log_success "Jaeger deployed"
}

# Wait for deployments to be ready
wait_for_deployments() {
    log_info "Waiting for deployments to be ready..."
    
    # Wait for OTel Collector
    kubectl wait --for=condition=available --timeout=300s deployment/otel-collector
    
    # Wait for Prometheus
    kubectl wait --for=condition=available --timeout=300s deployment/prometheus -n monitoring
    
    # Wait for Grafana
    kubectl wait --for=condition=available --timeout=300s deployment/grafana -n monitoring
    
    # Wait for Jaeger
    kubectl wait --for=condition=available --timeout=300s deployment/jaeger-collector
    kubectl wait --for=condition=available --timeout=300s deployment/jaeger-query
    
    log_success "All deployments are ready"
}

# Display access information
display_access_info() {
    log_info "Observability stack deployed successfully!"
    echo ""
    echo "Access URLs:"
    echo "============"
    echo "Grafana:     http://$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}'):30671 (admin/admin)"
    echo "Jaeger:      http://$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}'):30668"
    echo "Zipkin:      http://$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}'):30669"
    echo ""
    echo "Port-forward commands:"
    echo "======================"
    echo "Grafana:     kubectl port-forward -n monitoring service/grafana 30671:3000"
    echo "Jaeger:      kubectl port-forward service/jaeger-query 30668:16686"
    echo "Prometheus:  kubectl port-forward -n monitoring service/prometheus 9090:9090"
    echo ""
    echo "Next steps:"
    echo "==========="
    echo "1. Access Grafana and import dashboards"
    echo "2. Configure service instrumentation"
    echo "3. Set up custom metrics and alerting"
    echo "4. Review the observability implementation plan for detailed next steps"
}

# Main execution
main() {
    log_info "Starting observability stack deployment..."
    
    check_prerequisites
    create_namespace
    deploy_otel_collector
    deploy_prometheus
    deploy_grafana
    deploy_jaeger
    wait_for_deployments
    display_access_info
    
    log_success "Observability deployment completed!"
}

# Run main function
main "$@"
