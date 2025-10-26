#!/bin/bash

# 30-minute ingest performance monitoring script
LOG_FILE="/tmp/ingest-performance-$(date +%Y%m%d-%H%M%S).log"
START_TIME=$(date +%s)
END_TIME=$((START_TIME + 1800)) # 30 minutes

echo "=== INGEST PERFORMANCE MONITORING STARTED ===" | tee $LOG_FILE
echo "Start time: $(date)" | tee -a $LOG_FILE
echo "Monitoring for 30 minutes..." | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

# Function to get current processing stats
get_stats() {
    local timestamp=$(date)
    local current_time=$(date +%s)
    local elapsed=$((current_time - START_TIME))
    
    echo "[$timestamp] Elapsed: ${elapsed}s" | tee -a $LOG_FILE
    
    # Get ingestor-server logs for recent activity
    echo "--- Recent Ingestor Activity ---" | tee -a $LOG_FILE
    kubectl logs deployment/ingestor-server --tail=10 2>/dev/null | grep -E "(Processing|batch|complete|documents)" | tee -a $LOG_FILE
    
    # Get pod resource usage
    echo "--- Resource Usage ---" | tee -a $LOG_FILE
    kubectl top pods | grep -E "(ingestor-server|rag-nv-ingest|nv-ingest-ms-runtime)" | tee -a $LOG_FILE
    
    # Get GPU usage
    echo "--- GPU Usage ---" | tee -a $LOG_FILE
    kubectl get pods -o wide | grep -E "(nv-ingest-ms-runtime|rag-nv-ingest)" | wc -l | xargs echo "Active GPU pods:" | tee -a $LOG_FILE
    
    echo "" | tee -a $LOG_FILE
}

# Monitor every 2 minutes
while [ $(date +%s) -lt $END_TIME ]; do
    get_stats
    sleep 120  # 2 minutes
done

# Final stats
echo "=== FINAL PERFORMANCE SUMMARY ===" | tee -a $LOG_FILE
echo "End time: $(date)" | tee -a $LOG_FILE
echo "Total monitoring time: 30 minutes" | tee -a $LOG_FILE

# Analyze logs for performance metrics
echo "--- Performance Analysis ---" | tee -a $LOG_FILE
echo "Processing times from logs:" | tee -a $LOG_FILE
kubectl logs deployment/ingestor-server --since=30m 2>/dev/null | grep -E "Time taken:" | tail -20 | tee -a $LOG_FILE

echo "=== MONITORING COMPLETED ===" | tee -a $LOG_FILE
echo "Log file: $LOG_FILE" | tee -a $LOG_FILE
