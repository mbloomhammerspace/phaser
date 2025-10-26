#!/bin/bash

# =============================================================================
# Milvus Traffic Monitor
# =============================================================================
# Monitor erratic Milvus traffic patterns during blocking tests
# =============================================================================

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🔍 Monitoring Milvus Traffic Patterns${NC}"
echo "Press Ctrl+C to stop monitoring"
echo ""

# Function to get current timestamp
timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

# Function to check Milvus pod status
check_milvus_status() {
    local status=$(kubectl get pod milvus-56cb6b648d-zxsbj -o jsonpath='{.status.phase}' 2>/dev/null)
    local ready=$(kubectl get pod milvus-56cb6b648d-zxsbj -o jsonpath='{.status.containerStatuses[0].ready}' 2>/dev/null)
    local restarts=$(kubectl get pod milvus-56cb6b648d-zxsbj -o jsonpath='{.status.containerStatuses[0].restartCount}' 2>/dev/null)
    
    if [ "$status" = "Running" ] && [ "$ready" = "true" ]; then
        echo -e "${GREEN}✓${NC} Milvus: Running, Ready, Restarts: $restarts"
    else
        echo -e "${RED}✗${NC} Milvus: $status, Ready: $ready, Restarts: $restarts"
    fi
}

# Function to check resource usage
check_resources() {
    local cpu_mem=$(kubectl top pod milvus-56cb6b648d-zxsbj --no-headers 2>/dev/null)
    if [ -n "$cpu_mem" ]; then
        echo -e "${BLUE}📊${NC} Resources: $cpu_mem"
    else
        echo -e "${YELLOW}⚠️${NC} Resource metrics unavailable"
    fi
}

# Function to check recent logs for errors
check_recent_errors() {
    local errors=$(kubectl logs milvus-56cb6b648d-zxsbj --tail=10 2>/dev/null | grep -i "error\|fail\|exception" | wc -l)
    if [ "$errors" -gt 0 ]; then
        echo -e "${RED}🚨${NC} Recent errors: $errors"
    else
        echo -e "${GREEN}✅${NC} No recent errors"
    fi
}

# Function to check collection operations
check_collection_ops() {
    local collection_errors=$(kubectl logs ingestor-server-bcb6976f-8khrt --tail=20 2>/dev/null | grep -i "collection.*does not exist" | wc -l)
    if [ "$collection_errors" -gt 0 ]; then
        echo -e "${YELLOW}⚠️${NC} Collection errors: $collection_errors"
    else
        echo -e "${GREEN}✅${NC} No collection errors"
    fi
}

# Function to check Redis connectivity
check_redis_connectivity() {
    local redis_errors=$(kubectl logs rag-nv-ingest-56cbbd9776-jqvhw --tail=10 2>/dev/null | grep -i "redis\|connection" | wc -l)
    if [ "$redis_errors" -gt 0 ]; then
        echo -e "${YELLOW}⚠️${NC} Redis connectivity issues detected"
    else
        echo -e "${GREEN}✅${NC} Redis connectivity OK"
    fi
}

# Main monitoring loop
monitor_traffic() {
    while true; do
        clear
        echo -e "${CYAN}=== Milvus Traffic Monitor - $(timestamp) ===${NC}"
        echo ""
        
        # Check Milvus status
        check_milvus_status
        
        # Check resources
        check_resources
        
        # Check for errors
        check_recent_errors
        
        # Check collection operations
        check_collection_ops
        
        # Check Redis connectivity
        check_redis_connectivity
        
        echo ""
        echo -e "${BLUE}📈 Recent Milvus Logs:${NC}"
        kubectl logs milvus-56cb6b648d-zxsbj --tail=3 --since=30s 2>/dev/null | sed 's/^/  /'
        
        echo ""
        echo -e "${BLUE}📈 Recent Ingestor Logs:${NC}"
        kubectl logs ingestor-server-bcb6976f-8khrt --tail=3 --since=30s 2>/dev/null | sed 's/^/  /'
        
        echo ""
        echo -e "${BLUE}📈 Recent NV Ingest Logs:${NC}"
        kubectl logs rag-nv-ingest-56cbbd9776-jqvhw --tail=3 --since=30s 2>/dev/null | sed 's/^/  /'
        
        echo ""
        echo -e "${YELLOW}⏱️  Next update in 5 seconds... (Ctrl+C to stop)${NC}"
        sleep 5
    done
}

# Start monitoring
monitor_traffic
