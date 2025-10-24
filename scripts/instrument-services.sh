#!/bin/bash

# Service Instrumentation Script
# This script adds OpenTelemetry instrumentation to existing services
# without disrupting their operation

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

# Check if OTel Collector is running
check_otel_collector() {
    log_info "Checking OpenTelemetry Collector status..."
    
    if ! kubectl get deployment otel-collector &> /dev/null; then
        log_error "OpenTelemetry Collector is not deployed. Please run deploy-observability.sh first."
        exit 1
    fi
    
    if ! kubectl get pods -l app=otel-collector | grep -q Running; then
        log_error "OpenTelemetry Collector is not running. Please check the deployment."
        exit 1
    fi
    
    log_success "OpenTelemetry Collector is running"
}

# Instrument RAG Server
instrument_rag_server() {
    log_info "Instrumenting RAG Server..."
    
    # Check if RAG Server exists
    if ! kubectl get deployment rag-server &> /dev/null; then
        log_warning "RAG Server deployment not found, skipping..."
        return
    fi
    
    # Add OTel environment variables
    kubectl patch deployment rag-server -p '{
      "spec": {
        "template": {
          "spec": {
            "containers": [{
              "name": "rag-server",
              "env": [
                {"name": "OTEL_EXPORTER_OTLP_ENDPOINT", "value": "http://otel-collector:4317"},
                {"name": "OTEL_SERVICE_NAME", "value": "rag-server"},
                {"name": "OTEL_RESOURCE_ATTRIBUTES", "value": "service.name=rag-server,service.version=1.0.0"},
                {"name": "OTEL_TRACES_EXPORTER", "value": "otlp"},
                {"name": "OTEL_METRICS_EXPORTER", "value": "otlp"}
              ]
            }]
          }
        }
      }
    }'
    
    log_success "RAG Server instrumented"
}

# Instrument AI-Q Backend
instrument_aiq_backend() {
    log_info "Instrumenting AI-Q Backend..."
    
    # Check if AI-Q Backend exists
    if ! kubectl get deployment aiq-aira-backend &> /dev/null; then
        log_warning "AI-Q Backend deployment not found, skipping..."
        return
    fi
    
    # Add OTel environment variables
    kubectl patch deployment aiq-aira-backend -p '{
      "spec": {
        "template": {
          "spec": {
            "containers": [{
              "name": "aiq-aira-backend",
              "env": [
                {"name": "OTEL_EXPORTER_OTLP_ENDPOINT", "value": "http://otel-collector:4317"},
                {"name": "OTEL_SERVICE_NAME", "value": "aiq-backend"},
                {"name": "OTEL_RESOURCE_ATTRIBUTES", "value": "service.name=aiq-backend,service.version=1.0.0"},
                {"name": "OTEL_TRACES_EXPORTER", "value": "otlp"},
                {"name": "OTEL_METRICS_EXPORTER", "value": "otlp"}
              ]
            }]
          }
        }
      }
    }'
    
    log_success "AI-Q Backend instrumented"
}

# Configure Nginx Access Logs
configure_nginx_logging() {
    log_info "Configuring Nginx access logging..."
    
    # Check if AI-Q Nginx exists
    if ! kubectl get configmap aiq-aiq-aira-nginx &> /dev/null; then
        log_warning "AI-Q Nginx ConfigMap not found, skipping..."
        return
    fi
    
    # Get current nginx config
    CURRENT_CONFIG=$(kubectl get configmap aiq-aiq-aira-nginx -o jsonpath='{.data.nginx\.conf}')
    
    # Add access logging to nginx config
    UPDATED_CONFIG=$(echo "$CURRENT_CONFIG" | sed 's/events {}/events {}\nhttp {\n  log_format main '\''$remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent" $request_time'\'';\n  access_log \/var\/log\/nginx\/access.log main;/')
    
    # Update the configmap
    kubectl patch configmap aiq-aiq-aira-nginx -p "{\"data\":{\"nginx.conf\":\"$UPDATED_CONFIG\"}}"
    
    # Restart nginx deployment
    kubectl rollout restart deployment aiq-aira-nginx
    
    log_success "Nginx access logging configured"
}

# Add Prometheus annotations to services
add_prometheus_annotations() {
    log_info "Adding Prometheus annotations to services..."
    
    # Add annotations to RAG Server
    if kubectl get deployment rag-server &> /dev/null; then
        kubectl patch deployment rag-server -p '{
          "spec": {
            "template": {
              "metadata": {
                "annotations": {
                  "prometheus.io/scrape": "true",
                  "prometheus.io/port": "8081",
                  "prometheus.io/path": "/metrics"
                }
              }
            }
          }
        }'
        log_success "Prometheus annotations added to RAG Server"
    fi
    
    # Add annotations to AI-Q Backend
    if kubectl get deployment aiq-aira-backend &> /dev/null; then
        kubectl patch deployment aiq-aira-backend -p '{
          "spec": {
            "template": {
              "metadata": {
                "annotations": {
                  "prometheus.io/scrape": "true",
                  "prometheus.io/port": "3838",
                  "prometheus.io/path": "/metrics"
                }
              }
            }
          }
        }'
        log_success "Prometheus annotations added to AI-Q Backend"
    fi
}

# Wait for deployments to be ready
wait_for_deployments() {
    log_info "Waiting for deployments to be ready..."
    
    # Wait for RAG Server
    if kubectl get deployment rag-server &> /dev/null; then
        kubectl wait --for=condition=available --timeout=300s deployment/rag-server
    fi
    
    # Wait for AI-Q Backend
    if kubectl get deployment aiq-aira-backend &> /dev/null; then
        kubectl wait --for=condition=available --timeout=300s deployment/aiq-aira-backend
    fi
    
    # Wait for AI-Q Nginx
    if kubectl get deployment aiq-aira-nginx &> /dev/null; then
        kubectl wait --for=condition=available --timeout=300s deployment/aiq-aira-nginx
    fi
    
    log_success "All deployments are ready"
}

# Verify instrumentation
verify_instrumentation() {
    log_info "Verifying instrumentation..."
    
    # Check if traces are being sent to OTel Collector
    log_info "Checking OTel Collector logs for traces..."
    kubectl logs -l app=otel-collector --tail=10 | grep -i trace || log_warning "No traces found in OTel Collector logs yet"
    
    # Check if metrics are being scraped by Prometheus
    log_info "Checking Prometheus targets..."
    kubectl exec -n monitoring deployment/prometheus -- wget -qO- http://localhost:9090/api/v1/targets | grep -o '"health":"[^"]*"' || log_warning "Could not check Prometheus targets"
    
    log_success "Instrumentation verification completed"
}

# Display next steps
display_next_steps() {
    log_info "Service instrumentation completed!"
    echo ""
    echo "Next steps:"
    echo "==========="
    echo "1. Access Grafana: http://localhost:30671 (admin/admin)"
    echo "2. Import dashboards for Kubernetes and application metrics"
    echo "3. Check Jaeger for distributed traces: http://localhost:30668"
    echo "4. Monitor Prometheus targets for metric collection"
    echo "5. Set up custom dashboards for RAG and AI-Q specific metrics"
    echo ""
    echo "Useful commands:"
    echo "================"
    echo "kubectl port-forward -n monitoring service/grafana 30671:3000"
    echo "kubectl port-forward service/jaeger-query 30668:16686"
    echo "kubectl port-forward -n monitoring service/prometheus 9090:9090"
    echo "kubectl logs -l app=otel-collector -f"
}

# Main execution
main() {
    log_info "Starting service instrumentation..."
    
    check_otel_collector
    instrument_rag_server
    instrument_aiq_backend
    configure_nginx_logging
    add_prometheus_annotations
    wait_for_deployments
    verify_instrumentation
    display_next_steps
    
    log_success "Service instrumentation completed!"
}

# Run main function
main "$@"
