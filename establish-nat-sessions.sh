#!/bin/bash

# =============================================================================
# NVIDIA RAG Blueprint - Establish All NAT Sessions
# =============================================================================
# This script establishes all NAT port forwarding sessions for the NVIDIA RAG
# Blueprint services running on your Kubernetes cluster.
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
LOG_FILE="${SCRIPT_DIR}/nat-sessions.log"
PID_FILE="${SCRIPT_DIR}/nat-sessions.pid"

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

kill_existing_forwards() {
    log "INFO" "Stopping existing port forwards..."
    
    # Kill existing kubectl port-forward processes
    pkill -f "kubectl port-forward" 2>/dev/null || true
    
    # Remove PID file
    rm -f "$PID_FILE"
    
    log "INFO" "Existing port forwards stopped"
}

# =============================================================================
# NAT Session Establishment
# =============================================================================

establish_nat_session() {
    local service_name="$1"
    local local_port="$2"
    local remote_port="$3"
    local description="$4"
    
    log "INFO" "Establishing NAT session: $description"
    log "DEBUG" "Service: $service_name, Local: $local_port, Remote: $remote_port"
    
    # Check if service exists
    if ! kubectl get service "$service_name" &> /dev/null; then
        log "WARN" "Service $service_name not found, skipping..."
        return 1
    fi
    
    # Start port forward
    kubectl port-forward "service/$service_name" "$local_port:$remote_port" --address=0.0.0.0 &
    local pid=$!
    
    # Wait a moment to check if the port forward started successfully
    sleep 2
    if kill -0 "$pid" 2>/dev/null; then
        log "INFO" "✓ $description - PID: $pid, Port: $local_port"
        echo "$pid" >> "$PID_FILE"
        return 0
    else
        log "ERROR" "✗ Failed to start $description"
        return 1
    fi
}

establish_all_nat_sessions() {
    log "INFO" "Establishing all NVIDIA RAG Blueprint NAT sessions..."
    echo ""
    
    # Core RAG Services
    establish_nat_session "clean-rag-frontend" "3000" "3000" "RAG Playground (Document search interface)"
    establish_nat_session "rag-server" "8081" "8081" "RAG Server API (Core RAG processing)"
    establish_nat_session "ingestor-server" "8082" "8082" "RAG Ingestor (Document processing)"
    
    # AI-Q Research Assistant Services
    establish_nat_session "aiq-aira-frontend" "8051" "3000" "AI-Q Frontend (Enterprise AI interface)"
    establish_nat_session "aiq-aira-backend" "3838" "3838" "AI-Q Backend (Research processing)"
    establish_nat_session "aiq-aira-nginx" "8052" "8051" "AI-Q Nginx (Load balancer)"
    establish_nat_session "aiq-phoenix" "6006" "6006" "Phoenix Service (AI-Q component)"
    establish_nat_session "aira-instruct-llm" "8000" "8000" "AI-Q LLM (Language model processing)"
    
    # Vector Database & Management
    establish_nat_session "milvus" "19530" "19530" "Milvus Database (Vector storage)"
    establish_nat_session "milvus" "9091" "9091" "Milvus Metrics (Database performance)"
    establish_nat_session "attu" "3001" "3000" "Attu UI (Milvus management interface)"
    
    # Observability & Monitoring
    establish_nat_session "jaeger-query" "16686" "16686" "Jaeger Tracing (Distributed tracing)"
    establish_nat_session "zipkin" "9411" "9411" "Zipkin Tracing (Request tracing)"
    establish_nat_session "grafana" "30671" "3000" "Grafana Dashboard (Metrics visualization)"
    
    # NeMo Retriever Services
    establish_nat_session "nemoretriever-embedding-ms" "8001" "8000" "NeMo Embedding (Vector embedding generation)"
    establish_nat_session "nemoretriever-reranking-ms" "8002" "8000" "NeMo Reranking (Search result reranking)"
    
    # Data & Cache Services
    establish_nat_session "rag-redis-master" "6379" "6379" "Redis Cache (In-memory data store)"
    establish_nat_session "etcd" "2379" "2379" "etcd Database (Kubernetes state store)"
    
    echo ""
    log "INFO" "All NAT sessions establishment completed"
}

# =============================================================================
# Status and Management Functions
# =============================================================================

show_status() {
    echo -e "${CYAN}=== NVIDIA RAG Blueprint - NAT Sessions Status ===${NC}"
    echo ""
    
    # Check active port forwards
    local active_forwards=$(ps aux | grep "kubectl port-forward" | grep -v grep | wc -l)
    echo -e "${BLUE}Active NAT sessions: $active_forwards${NC}"
    
    if [ "$active_forwards" -gt 0 ]; then
        echo ""
        echo -e "${BLUE}Active port forwards:${NC}"
        ps aux | grep "kubectl port-forward" | grep -v grep | while read line; do
            echo "  $line"
        done
    fi
    
    echo ""
    echo -e "${BLUE}Service Access URLs:${NC}"
    echo -e "  ${GREEN}http://localhost:3000${NC} - RAG Playground (Main interface)"
    echo -e "  ${GREEN}http://localhost:3001${NC} - Attu UI (Milvus management)"
    echo -e "  ${GREEN}http://localhost:8081${NC} - RAG Server API"
    echo -e "  ${GREEN}http://localhost:8082${NC} - RAG Ingestor API"
    echo -e "  ${GREEN}http://localhost:8051${NC} - AI-Q Research Assistant"
    echo -e "  ${GREEN}http://localhost:3838${NC} - AI-Q Backend API"
    echo -e "  ${GREEN}http://localhost:8052${NC} - AI-Q Nginx"
    echo -e "  ${GREEN}http://localhost:6006${NC} - Phoenix Service"
    echo -e "  ${GREEN}http://localhost:8000${NC} - AI-Q LLM API"
    echo -e "  ${GREEN}localhost:19530${NC} - Milvus Database gRPC"
    echo -e "  ${GREEN}http://localhost:9091${NC} - Milvus Metrics"
    echo -e "  ${GREEN}http://localhost:16686${NC} - Jaeger Tracing"
    echo -e "  ${GREEN}http://localhost:9411${NC} - Zipkin Tracing"
    echo -e "  ${GREEN}http://localhost:30671${NC} - Grafana Dashboard"
    echo -e "  ${GREEN}http://localhost:8001${NC} - NeMo Embedding API"
    echo -e "  ${GREEN}http://localhost:8002${NC} - NeMo Reranking API"
    echo -e "  ${GREEN}localhost:6379${NC} - Redis Cache"
    echo -e "  ${GREEN}localhost:2379${NC} - etcd Database"
}

show_help() {
    echo -e "${CYAN}NVIDIA RAG Blueprint - NAT Sessions Manager${NC}"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     - Establish all NAT port forwarding sessions"
    echo "  stop      - Stop all NAT port forwarding sessions"
    echo "  restart   - Restart all NAT port forwarding sessions"
    echo "  status    - Show current NAT sessions status"
    echo "  help      - Show this help message"
    echo ""
    echo "This script establishes NAT port forwarding sessions for all"
    echo "NVIDIA RAG Blueprint services running on your Kubernetes cluster."
}

# =============================================================================
# Main Script Logic
# =============================================================================

main() {
    local command="${1:-help}"
    
    # Initialize log file
    echo "=== NVIDIA RAG Blueprint NAT Sessions Log ===" > "$LOG_FILE"
    echo "Started: $(date)" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    
    case "$command" in
        "start")
            log "INFO" "Starting NVIDIA RAG Blueprint NAT sessions..."
            check_kubectl
            kill_existing_forwards
            establish_all_nat_sessions
            sleep 3
            show_status
            ;;
        "stop")
            log "INFO" "Stopping all NAT sessions..."
            kill_existing_forwards
            log "INFO" "All NAT sessions stopped"
            ;;
        "restart")
            log "INFO" "Restarting NAT sessions..."
            kill_existing_forwards
            sleep 2
            establish_all_nat_sessions
            sleep 3
            show_status
            ;;
        "status")
            show_status
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@"
