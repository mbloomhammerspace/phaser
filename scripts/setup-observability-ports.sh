#!/bin/bash

# Observability Port Setup Script
# This script sets up port-forwarding for observability services
# and provides the NAT/port mapping information

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

# Check current observability services
check_current_services() {
    log_info "Checking current observability services..."
    
    echo "=== Current Services ==="
    kubectl get svc --all-namespaces | grep -E "(grafana|jaeger|zipkin|prometheus|otel)" || echo "No observability services found"
    
    echo ""
    echo "=== Current Pods ==="
    kubectl get pods --all-namespaces | grep -E "(grafana|jaeger|zipkin|prometheus|otel)" || echo "No observability pods found"
    
    echo ""
    echo "=== Current Port Usage ==="
    lsof -i :30668 -i :30669 -i :30670 -i :30671 -i :9090 2>/dev/null || echo "No processes using observability ports"
}

# Deploy observability stack with NodePort services
deploy_observability_with_ports() {
    log_info "Deploying observability stack with NodePort services..."
    
    # Create monitoring namespace
    kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f - || true
    
    # Deploy Prometheus with NodePort
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

    # Deploy Prometheus with NodePort
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
  type: NodePort
  nodePort: 30090
EOF

    # Deploy Grafana with NodePort
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

    # Deploy Jaeger with NodePort
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

    # Update Zipkin to use NodePort
    kubectl patch service zipkin -p '{"spec":{"type":"NodePort","ports":[{"port":9411,"targetPort":9411,"nodePort":30669}]}}'

    log_success "Observability stack deployed with NodePort services"
}

# Wait for deployments
wait_for_deployments() {
    log_info "Waiting for deployments to be ready..."
    
    kubectl wait --for=condition=available --timeout=300s deployment/prometheus -n monitoring
    kubectl wait --for=condition=available --timeout=300s deployment/grafana -n monitoring
    kubectl wait --for=condition=available --timeout=300s deployment/jaeger-collector
    kubectl wait --for=condition=available --timeout=300s deployment/jaeger-query
    
    log_success "All deployments are ready"
}

# Display port mapping
display_port_mapping() {
    log_info "Observability Port Mapping:"
    echo ""
    echo "=== NodePort Services ==="
    kubectl get svc --all-namespaces | grep -E "(grafana|jaeger|zipkin|prometheus)" | grep NodePort
    echo ""
    
    # Get node IP
    NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
    
    echo "=== Access URLs (NodePort) ==="
    echo "Grafana:     http://$NODE_IP:30671 (admin/admin)"
    echo "Jaeger:      http://$NODE_IP:30668"
    echo "Zipkin:      http://$NODE_IP:30669"
    echo "Prometheus:  http://$NODE_IP:30090"
    echo ""
    
    echo "=== Port-Forward Commands ==="
    echo "Grafana:     kubectl port-forward -n monitoring service/grafana 30671:3000"
    echo "Jaeger:      kubectl port-forward service/jaeger-query 30668:16686"
    echo "Zipkin:      kubectl port-forward service/zipkin 30669:9411"
    echo "Prometheus:  kubectl port-forward -n monitoring service/prometheus 9090:9090"
    echo ""
    
    echo "=== Current Port Usage ==="
    lsof -i :30668 -i :30669 -i :30670 -i :30671 -i :30090 -i :9090 2>/dev/null || echo "No processes using observability ports"
}

# Main execution
main() {
    log_info "Setting up observability ports and NAT mapping..."
    
    check_current_services
    echo ""
    deploy_observability_with_ports
    wait_for_deployments
    display_port_mapping
    
    log_success "Observability port setup completed!"
}

# Run main function
main "$@"
