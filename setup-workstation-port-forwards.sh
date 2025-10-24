#!/bin/bash

# =============================================================================
# NVIDIA RAG Blueprint - Workstation Port Forward Setup Script
# =============================================================================
# This script establishes all required port forwards for MacBook workstation
# access to the NVIDIA RAG Blueprint services running on Kubernetes.
#
# Generated: October 23, 2025
# Author: AI Assistant
# =============================================================================

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/port-forward.log"
PID_FILE="${SCRIPT_DIR}/port-forward.pid"
SCREEN_SESSION="rag-port-forwards"

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
    
    # Kill screen session if it exists
    screen -S "$SCREEN_SESSION" -X quit 2>/dev/null || true
    
    # Remove PID file
    rm -f "$PID_FILE"
    
    log "INFO" "Existing port forwards stopped"
}

# =============================================================================
# Port Forward Functions
# =============================================================================

start_all_port_forwards() {
    log "INFO" "Starting all port forwards in screen session..."
    
    # Create screen session with all port forwards
    screen -dmS "$SCREEN_SESSION" bash -c "
        echo 'Starting NVIDIA RAG Blueprint port forwards...'
        echo 'Session: $SCREEN_SESSION'
        echo 'Log file: $LOG_FILE'
        echo ''
        
        # Core RAG Services
        echo 'Starting RAG Playground (3000)...'
        kubectl port-forward service/clean-rag-frontend 3000:3000 --address=0.0.0.0 &
        sleep 1
        
        echo 'Starting RAG Server (8081)...'
        kubectl port-forward service/rag-server 8081:8081 --address=0.0.0.0 &
        sleep 1
        
        echo 'Starting RAG Ingestor (8082)...'
        kubectl port-forward service/ingestor-server 8082:8082 --address=0.0.0.0 &
        sleep 1
        
        # AI-Q Research Assistant
        echo 'Starting AI-Q Frontend (8051)...'
        kubectl port-forward service/aiq-aira-frontend 8051:3000 --address=0.0.0.0 &
        sleep 1
        
        echo 'Starting AI-Q Backend (3838)...'
        kubectl port-forward service/aiq-aira-backend 3838:3838 --address=0.0.0.0 &
        sleep 1
        
        echo 'Starting AI-Q Nginx (8052)...'
        kubectl port-forward service/aiq-aira-nginx 8052:8051 --address=0.0.0.0 &
        sleep 1
        
        echo 'Starting Phoenix Service (6006)...'
        kubectl port-forward service/aiq-phoenix 6006:6006 --address=0.0.0.0 &
        sleep 1
        
        echo 'Starting AI-Q LLM (8000)...'
        kubectl port-forward service/aira-instruct-llm 8000:8000 --address=0.0.0.0 &
        sleep 1
        
        # Vector Database & Management
        echo 'Starting Milvus Database (19530)...'
        kubectl port-forward service/milvus 19530:19530 --address=0.0.0.0 &
        sleep 1
        
        echo 'Starting Milvus Metrics (9091)...'
        kubectl port-forward service/milvus 9091:9091 --address=0.0.0.0 &
        sleep 1
        
        echo 'Starting Attu UI (3001)...'
        kubectl port-forward service/attu 3001:3000 --address=0.0.0.0 &
        sleep 1
        
        # Observability & Monitoring
        echo 'Starting Jaeger Tracing (16686)...'
        kubectl port-forward service/jaeger-query 16686:16686 --address=0.0.0.0 &
        sleep 1
        
        echo 'Starting Zipkin Tracing (9411)...'
        kubectl port-forward service/zipkin 9411:9411 --address=0.0.0.0 &
        sleep 1
        
        echo 'Starting Grafana Dashboard (30671)...'
        kubectl port-forward service/grafana 30671:3000 --address=0.0.0.0 &
        sleep 1
        
        # NeMo Retriever Services
        echo 'Starting NeMo Embedding (8001)...'
        kubectl port-forward service/nemoretriever-embedding-ms 8001:8000 --address=0.0.0.0 &
        sleep 1
        
        echo 'Starting NeMo Reranking (8002)...'
        kubectl port-forward service/nemoretriever-reranking-ms 8002:8000 --address=0.0.0.0 &
        sleep 1
        
        # Data & Cache Services
        echo 'Starting Redis Cache (6379)...'
        kubectl port-forward service/rag-redis-master 6379:6379 --address=0.0.0.0 &
        sleep 1
        
        echo 'Starting etcd Database (2379)...'
        kubectl port-forward service/etcd 2379:2379 --address=0.0.0.0 &
        sleep 1
        
        echo ''
        echo 'All port forwards started!'
        echo 'To reconnect: screen -r $SCREEN_SESSION'
        echo 'To detach: Ctrl+A then D'
        echo ''
        
        # Keep session alive
        while true; do
            sleep 30
            echo \"\$(date): Port forwards active\"
        done
    "
    
    log "INFO" "Port forward session started: $SCREEN_SESSION"
}

# =============================================================================
# Status and Management Functions
# =============================================================================

show_status() {
    echo -e "${CYAN}=== NVIDIA RAG Blueprint - Port Forward Status ===${NC}"
    echo ""
    
    # Check screen session
    if screen -list | grep -q "$SCREEN_SESSION"; then
        echo -e "${GREEN}✓ Screen session active: $SCREEN_SESSION${NC}"
    else
        echo -e "${RED}✗ Screen session not running${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}Active port forwards:${NC}"
    ps aux | grep "kubectl port-forward" | grep -v grep || echo "No active port forwards"
    
    echo ""
    echo -e "${BLUE}Service Access URLs:${NC}"
    echo -e "  ${GREEN}http://localhost:3000${NC} - RAG Playground (Document search interface)"
    echo -e "  ${GREEN}http://localhost:8081${NC} - RAG Server API (Core RAG processing)"
    echo -e "  ${GREEN}http://localhost:8082${NC} - RAG Ingestor (Document processing)"
    echo -e "  ${GREEN}http://localhost:8051${NC} - AI-Q Research Assistant (Enterprise AI)"
    echo -e "  ${GREEN}http://localhost:3838${NC} - AI-Q Backend API (Research processing)"
    echo -e "  ${GREEN}http://localhost:8052${NC} - AI-Q Nginx (Load balancer)"
    echo -e "  ${GREEN}http://localhost:6006${NC} - Phoenix Service (AI-Q component)"
    echo -e "  ${GREEN}http://localhost:8000${NC} - AI-Q LLM (Language model)"
    echo -e "  ${GREEN}localhost:19530${NC} - Milvus Database (Vector storage)"
    echo -e "  ${GREEN}http://localhost:9091${NC} - Milvus Metrics (Database performance)"
    echo -e "  ${GREEN}http://localhost:3001${NC} - Attu UI (Milvus management)"
    echo -e "  ${GREEN}http://localhost:16686${NC} - Jaeger Tracing (Distributed tracing)"
    echo -e "  ${GREEN}http://localhost:9411${NC} - Zipkin Tracing (Alternative tracing)"
    echo -e "  ${GREEN}http://localhost:30671${NC} - Grafana Dashboard (Metrics visualization)"
    echo -e "  ${GREEN}http://localhost:8001${NC} - NeMo Embedding (Vector embedding)"
    echo -e "  ${GREEN}http://localhost:8002${NC} - NeMo Reranking (Search reranking)"
    echo -e "  ${GREEN}localhost:6379${NC} - Redis Cache (In-memory data store)"
    echo -e "  ${GREEN}localhost:2379${NC} - etcd Database (Kubernetes state)"
}

show_help() {
    echo -e "${CYAN}NVIDIA RAG Blueprint - Workstation Port Forward Manager${NC}"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     - Start all port forwards in screen session"
    echo "  stop      - Stop all port forwards and screen session"
    echo "  restart   - Restart all port forwards"
    echo "  status    - Show current status and access URLs"
    echo "  connect   - Connect to port forward screen session"
    echo "  help      - Show this help message"
    echo ""
    echo "Service Access URLs:"
    echo -e "  ${GREEN}http://localhost:3000${NC} - RAG Playground (Main interface)"
    echo -e "  ${GREEN}http://localhost:8051${NC} - AI-Q Research Assistant"
    echo -e "  ${GREEN}http://localhost:3001${NC} - Attu (Milvus Management)"
    echo -e "  ${GREEN}http://localhost:16686${NC} - Jaeger Tracing"
    echo -e "  ${GREEN}http://localhost:9411${NC} - Zipkin Tracing"
    echo -e "  ${GREEN}http://localhost:30671${NC} - Grafana Dashboard"
}

# =============================================================================
# Main Script Logic
# =============================================================================

main() {
    local command="${1:-help}"
    
    # Initialize log file
    echo "=== NVIDIA RAG Blueprint Port Forward Log ===" > "$LOG_FILE"
    echo "Started: $(date)" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    
    case "$command" in
        "start")
            log "INFO" "Starting NVIDIA RAG Blueprint port forwards..."
            check_kubectl
            kill_existing_forwards
            start_all_port_forwards
            sleep 3
            show_status
            ;;
        "stop")
            log "INFO" "Stopping all port forwards..."
            kill_existing_forwards
            log "INFO" "All port forwards stopped"
            ;;
        "restart")
            log "INFO" "Restarting port forwards..."
            kill_existing_forwards
            sleep 2
            start_all_port_forwards
            sleep 3
            show_status
            ;;
        "status")
            show_status
            ;;
        "connect")
            log "INFO" "Connecting to port forward session..."
            echo "Use Ctrl+A then D to detach from session"
            screen -r "$SCREEN_SESSION"
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@"