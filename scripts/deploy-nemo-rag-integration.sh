#!/bin/bash

# NeMo Agent Toolkit - RAG Integration Deployment Script
# This script sets up the complete integration between NeMo Agent Toolkit and the RAG pipeline

set -e

JUMPHOST_IP="132.145.204.155"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 NeMo Agent Toolkit - RAG Integration Deployment"
echo "=================================================="
echo ""

# Function to log messages
log_info() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

log_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

log_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1" >&2
}

# Function to check if running on jumphost
check_jumphost() {
    local current_ip=$(curl -s ifconfig.me 2>/dev/null || echo "unknown")
    if [[ "$current_ip" != "$JUMPHOST_IP" ]]; then
        log_error "This script must be run on the jumphost ($JUMPHOST_IP)"
        log_error "Current IP: $current_ip"
        exit 1
    fi
    log_success "Running on jumphost ($JUMPHOST_IP)"
}

# Function to setup port-forwards
setup_port_forwards() {
    log_info "Setting up port-forwards to Kubernetes services..."
    
    # Kill any existing port-forwards
    pkill -f "kubectl port-forward" || true
    sleep 2
    
    # Port-forward Milvus (GRPC and HTTP)
    log_info "Port-forwarding Milvus (GRPC: 19530, HTTP: 9091)..."
    kubectl port-forward svc/milvus 19530:19530 > /dev/null 2>&1 &
    kubectl port-forward svc/milvus 9091:9091 > /dev/null 2>&1 &
    
    # Port-forward RAG Server
    log_info "Port-forwarding RAG Server (8081)..."
    kubectl port-forward svc/rag-server 8081:8081 > /dev/null 2>&1 &
    
    # Port-forward NIM (if available)
    log_info "Port-forwarding NIM (8000)..."
    kubectl port-forward svc/nim-llm 8000:8000 > /dev/null 2>&1 &
    
    # Wait for port-forwards to establish
    sleep 5
    
    # Test connectivity
    log_info "Testing port-forward connectivity..."
    local failed=0
    
    timeout 3 telnet localhost 19530 > /dev/null 2>&1 && log_success "Milvus GRPC (19530) accessible" || { log_error "Milvus GRPC (19530) not accessible"; failed=1; }
    timeout 3 telnet localhost 9091 > /dev/null 2>&1 && log_success "Milvus HTTP (9091) accessible" || { log_error "Milvus HTTP (9091) not accessible"; failed=1; }
    timeout 3 telnet localhost 8081 > /dev/null 2>&1 && log_success "RAG Server (8081) accessible" || { log_error "RAG Server (8081) not accessible"; failed=1; }
    timeout 3 telnet localhost 8000 > /dev/null 2>&1 && log_success "NIM (8000) accessible" || { log_error "NIM (8000) not accessible"; failed=1; }
    
    if [[ $failed -eq 1 ]]; then
        log_error "Some port-forwards failed. Please check Kubernetes services."
        return 1
    fi
    
    log_success "All port-forwards established successfully"
    return 0
}

# Function to deploy NeMo Agent Toolkit
deploy_nemo_agent() {
    log_info "Deploying NeMo Agent Toolkit with RAG integration..."
    
    cd ~
    
    # Stop existing container
    docker-compose -f docker-compose-nemo-agent-rag.yml down || true
    
    # Start new container
    docker-compose -f docker-compose-nemo-agent-rag.yml up -d
    
    # Wait for container to be ready
    log_info "Waiting for NeMo Agent Toolkit to be ready..."
    sleep 30
    
    # Check container status
    if docker ps | grep -q nemo-agent-toolkit-rag; then
        log_success "NeMo Agent Toolkit container is running"
    else
        log_error "NeMo Agent Toolkit container failed to start"
        return 1
    fi
    
    return 0
}

# Function to test integration
test_integration() {
    log_info "Testing NeMo Agent Toolkit - RAG integration..."
    
    # Test NeMo Agent Toolkit version
    if docker exec nemo-agent-toolkit-rag nat --version > /dev/null 2>&1; then
        log_success "NeMo Agent Toolkit is installed and accessible"
    else
        log_error "NeMo Agent Toolkit is not accessible"
        return 1
    fi
    
    # Test workflow file exists
    if docker exec nemo-agent-toolkit-rag test -f /app/workflows/rag-integration-workflow.yml; then
        log_success "RAG integration workflow file created"
    else
        log_error "RAG integration workflow file not found"
        return 1
    fi
    
    # Test Milvus connection from container
    log_info "Testing Milvus connection from NeMo Agent Toolkit..."
    if docker exec nemo-agent-toolkit-rag timeout 5 telnet host.docker.internal 19530 > /dev/null 2>&1; then
        log_success "Milvus connection from NeMo Agent Toolkit successful"
    else
        log_error "Milvus connection from NeMo Agent Toolkit failed"
        return 1
    fi
    
    # Test RAG Server connection from container
    log_info "Testing RAG Server connection from NeMo Agent Toolkit..."
    if docker exec nemo-agent-toolkit-rag timeout 5 telnet host.docker.internal 8081 > /dev/null 2>&1; then
        log_success "RAG Server connection from NeMo Agent Toolkit successful"
    else
        log_error "RAG Server connection from NeMo Agent Toolkit failed"
        return 1
    fi
    
    return 0
}

# Function to show status
show_status() {
    echo ""
    echo "📊 NeMo Agent Toolkit - RAG Integration Status"
    echo "=============================================="
    echo ""
    echo "🌐 Access Information:"
    echo "  - NeMo Agent Toolkit: http://$JUMPHOST_IP:9000"
    echo "  - MCP Server: http://$JUMPHOST_IP:9001"
    echo ""
    echo "🔗 Port-Forwarded Services:"
    echo "  - Milvus GRPC: localhost:19530"
    echo "  - Milvus HTTP: localhost:9091"
    echo "  - RAG Server: localhost:8081"
    echo "  - NIM: localhost:8000"
    echo ""
    echo "📋 Container Status:"
    docker ps | grep nemo-agent-toolkit-rag || echo "  No NeMo Agent Toolkit container running"
    echo ""
    echo "🧪 Test Commands:"
    echo "  - Test workflow: docker exec nemo-agent-toolkit-rag nat run --config_file /app/workflows/rag-integration-workflow.yml --input 'What collections are available?'"
    echo "  - Check logs: docker logs nemo-agent-toolkit-rag"
    echo "  - Access container: docker exec -it nemo-agent-toolkit-rag bash"
    echo ""
}

# Main execution
main() {
    log_info "Starting NeMo Agent Toolkit - RAG Integration deployment..."
    
    # Check if running on jumphost
    check_jumphost
    
    # Setup port-forwards
    if ! setup_port_forwards; then
        log_error "Port-forward setup failed. Exiting."
        exit 1
    fi
    
    # Deploy NeMo Agent Toolkit
    if ! deploy_nemo_agent; then
        log_error "NeMo Agent Toolkit deployment failed. Exiting."
        exit 1
    fi
    
    # Test integration
    if ! test_integration; then
        log_error "Integration test failed. Please check the logs."
        exit 1
    fi
    
    # Show status
    show_status
    
    log_success "NeMo Agent Toolkit - RAG Integration deployment completed successfully!"
    echo ""
    echo "🎉 You can now use the NeMo Agent Toolkit to interact with your RAG pipeline and Milvus collections!"
}

# Run main function
main "$@"
