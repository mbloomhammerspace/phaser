#!/bin/bash

# =============================================================================
# NVIDIA RAG Blueprint - Service Health Polling Script
# =============================================================================
# This script polls all Kubernetes services to check their health and
# establish port forwards for workstation access.
#
# Generated: October 23, 2025
# Author: AI Assistant
# =============================================================================

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/service-health.log"
HEALTH_CHECK_INTERVAL=30

# Service definitions
SERVICES=(
    "clean-rag-frontend:3000:RAG Playground"
    "rag-server:8081:RAG Server API"
    "ingestor-server:8082:RAG Ingestor"
    "aiq-aira-frontend:3000:AI-Q Frontend"
    "aiq-aira-backend:3838:AI-Q Backend"
    "aiq-aira-nginx:8051:AI-Q Nginx"
    "aiq-phoenix:6006:Phoenix Service"
    "aira-instruct-llm:8000:AI-Q LLM"
    "milvus:19530:Milvus Database"
    "milvus:9091:Milvus Metrics"
    "attu:3000:Attu UI"
    "jaeger-query:16686:Jaeger Tracing"
    "zipkin:9411:Zipkin Tracing"
    "grafana:3000:Grafana Dashboard"
    "nemoretriever-embedding-ms:8000:NeMo Embedding"
    "nemoretriever-reranking-ms:8000:NeMo Reranking"
    "rag-redis-master:6379:Redis Cache"
    "etcd:2379:etcd Database"
)

# =============================================================================
# Utility Functions
# =============================================================================

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")  echo -e "${GREEN}[INFO]${NC}  $message" | tee -a "$LOG_FILE" ;;
        "WARN")  echo -e "${YELLOW}[WARN]${NC}  $message" | tee -a "$LOG_FILE" ;;
        "ERROR") echo -e "${RED}[ERROR]${NC} $message" | tee -a "$LOG_FILE" ;;
        "DEBUG") echo -e "${BLUE}[DEBUG]${NC} $message" | tee -a "$LOG_FILE" ;;
    esac
}

check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        log "ERROR" "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    if ! kubectl cluster-info &> /dev/null; then
        log "ERROR" "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    log "INFO" "Kubernetes cluster connection verified"
}

# =============================================================================
# Service Health Functions
# =============================================================================

check_service_exists() {
    local service_name="$1"
    local namespace="${2:-default}"
    
    if kubectl get service "$service_name" -n "$namespace" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

check_pod_health() {
    local service_name="$1"
    local namespace="${2:-default}"
    
    # Get pods for the service
    local pods=$(kubectl get pods -n "$namespace" -l app="$service_name" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null)
    
    if [ -z "$pods" ]; then
        # Try alternative label selectors
        pods=$(kubectl get pods -n "$namespace" --field-selector metadata.name="$service_name" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null)
    fi
    
    if [ -z "$pods" ]; then
        return 1
    fi
    
    # Check if any pod is running
    for pod in $pods; do
        local status=$(kubectl get pod "$pod" -n "$namespace" -o jsonpath='{.status.phase}' 2>/dev/null)
        if [ "$status" = "Running" ]; then
            return 0
        fi
    done
    
    return 1
}

check_service_endpoint() {
    local service_name="$1"
    local port="$2"
    local namespace="${3:-default}"
    
    # Check if service has endpoints
    local endpoints=$(kubectl get endpoints "$service_name" -n "$namespace" -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null)
    
    if [ -n "$endpoints" ]; then
        return 0
    else
        return 1
    fi
}

poll_service() {
    local service_config="$1"
    IFS=':' read -r service_name port description <<< "$service_config"
    
    log "DEBUG" "Checking service: $service_name"
    
    # Check if service exists
    if ! check_service_exists "$service_name"; then
        log "WARN" "Service $service_name not found"
        return 1
    fi
    
    # Check pod health
    if ! check_pod_health "$service_name"; then
        log "WARN" "No healthy pods found for $service_name"
        return 1
    fi
    
    # Check service endpoints
    if ! check_service_endpoint "$service_name" "$port"; then
        log "WARN" "No endpoints found for $service_name"
        return 1
    fi
    
    log "INFO" "✓ $description ($service_name:$port) - Healthy"
    return 0
}

poll_all_services() {
    log "INFO" "Polling all NVIDIA RAG Blueprint services..."
    echo ""
    
    local healthy_count=0
    local total_count=${#SERVICES[@]}
    
    for service_config in "${SERVICES[@]}"; do
        if poll_service "$service_config"; then
            ((healthy_count++))
        fi
        echo ""
    done
    
    log "INFO" "Service health summary: $healthy_count/$total_count services healthy"
    
    if [ "$healthy_count" -eq "$total_count" ]; then
        log "INFO" "🎉 All services are healthy!"
        return 0
    else
        log "WARN" "⚠️  Some services are not healthy"
        return 1
    fi
}

# =============================================================================
# Port Forward Functions
# =============================================================================

establish_port_forwards() {
    log "INFO" "Establishing port forwards for healthy services..."
    
    # Start the main port forward script
    if [ -f "${SCRIPT_DIR}/setup-workstation-port-forwards.sh" ]; then
        log "INFO" "Starting port forwards using setup script..."
        "${SCRIPT_DIR}/setup-workstation-port-forwards.sh" start
    else
        log "ERROR" "Port forward setup script not found"
        return 1
    fi
}

# =============================================================================
# Main Functions
# =============================================================================

show_help() {
    echo -e "${CYAN}NVIDIA RAG Blueprint - Service Health Polling${NC}"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  poll      - Poll all services and check health"
    echo "  setup     - Poll services and establish port forwards"
    echo "  monitor   - Continuously monitor service health"
    echo "  help      - Show this help message"
    echo ""
    echo "This script checks the health of all NVIDIA RAG Blueprint services"
    echo "and can establish port forwards for workstation access."
}

monitor_services() {
    log "INFO" "Starting continuous service monitoring (interval: ${HEALTH_CHECK_INTERVAL}s)"
    echo "Press Ctrl+C to stop monitoring"
    echo ""
    
    while true; do
        echo -e "${CYAN}=== Service Health Check - $(date) ===${NC}"
        poll_all_services
        echo ""
        echo "Next check in ${HEALTH_CHECK_INTERVAL} seconds..."
        sleep "$HEALTH_CHECK_INTERVAL"
    done
}

# =============================================================================
# Main Script Logic
# =============================================================================

main() {
    local command="${1:-help}"
    
    # Initialize log file
    echo "=== NVIDIA RAG Blueprint Service Health Log ===" > "$LOG_FILE"
    echo "Started: $(date)" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    
    case "$command" in
        "poll")
            check_kubectl
            poll_all_services
            ;;
        "setup")
            check_kubectl
            if poll_all_services; then
                establish_port_forwards
            else
                log "ERROR" "Cannot establish port forwards - some services are unhealthy"
                exit 1
            fi
            ;;
        "monitor")
            check_kubectl
            monitor_services
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@"
