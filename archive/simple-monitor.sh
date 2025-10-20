#!/bin/bash

# Simple PDF Ingestion Monitor
# Usage: ./simple-monitor.sh

echo "Monitoring PDF ingestion progress..."
echo "Press Ctrl+C to stop"
echo ""

while true; do
    # Get latest progress
    progress=$(kubectl logs ingest-pdfs-new-collection 2>/dev/null | grep "Progress:" | tail -1)
    
    if [ -n "$progress" ]; then
        echo "[$(date '+%H:%M:%S')] $progress"
    else
        echo "[$(date '+%H:%M:%S')] ⏳ Waiting for progress updates..."
    fi
    
    sleep 15
done
