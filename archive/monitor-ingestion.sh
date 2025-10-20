#!/bin/bash

# PDF Ingestion Progress Monitor
# Usage: ./monitor-ingestion.sh

echo "🚀 PDF Ingestion Progress Monitor"
echo "=================================="
echo "Press Ctrl+C to stop monitoring"
echo ""

# Function to get current progress
get_progress() {
    # Get the latest progress line from ingestion logs
    local progress=$(kubectl logs ingest-pdfs-new-collection 2>/dev/null | grep "Progress:" | tail -1)
    
    if [ -n "$progress" ]; then
        echo "$progress"
    else
        echo "⏳ Waiting for ingestion to start..."
    fi
}

# Function to get collection status
get_collection_status() {
    # Try to get collection document count
    local count=$(kubectl run temp-check-$(date +%s) --image=python:3.9-slim --rm --restart=Never --quiet -- python3 -c "
import subprocess
try:
    subprocess.run(['pip', 'install', 'pymilvus', '--quiet'], check=True, capture_output=True)
    from pymilvus import connections, utility, Collection
    connections.connect('default', host='milvus', port='19530')
    if utility.has_collection('pdfs_new_ingestion'):
        c = Collection('pdfs_new_ingestion')
        print(c.num_entities)
    else:
        print('0')
except:
    print('0')
" 2>/dev/null)
    
    if [ -n "$count" ] && [ "$count" != "0" ]; then
        echo "📊 Collection documents: $count"
    else
        echo "📊 Collection status: Not available yet"
    fi
}

# Function to calculate ETA
calculate_eta() {
    local progress_line="$1"
    if [[ $progress_line == *"Progress:"* ]]; then
        # Extract processed count
        local processed=$(echo "$progress_line" | sed 's/.*Progress: \([0-9,]*\) files processed.*/\1/' | tr -d ',')
        local rate=$(echo "$progress_line" | sed 's/.*Rate: \([0-9.]*\) files\/sec.*/\1/')
        
        if [ -n "$processed" ] && [ -n "$rate" ] && [ "$rate" != "0" ]; then
            # Estimate total files (rough estimate based on previous runs)
            local total_files=71825
            local remaining=$((total_files - processed))
            local eta_seconds=$((remaining / ${rate%.*}))
            local eta_hours=$((eta_seconds / 3600))
            local eta_minutes=$(((eta_seconds % 3600) / 60))
            
            echo "⏱️  ETA: ${eta_hours}h ${eta_minutes}m (${remaining} files remaining)"
        fi
    fi
}

# Main monitoring loop
while true; do
    clear
    echo "🚀 PDF Ingestion Progress Monitor - $(date '+%H:%M:%S')"
    echo "=================================================="
    echo ""
    
    # Get current progress
    progress=$(get_progress)
    echo "📈 Latest Progress:"
    echo "   $progress"
    echo ""
    
    # Get collection status
    echo "🗄️  Database Status:"
    get_collection_status
    echo ""
    
    # Calculate ETA if possible
    if [[ $progress == *"Progress:"* ]]; then
        echo "📋 Estimated Completion:"
        calculate_eta "$progress"
        echo ""
    fi
    
    # Show recent activity
    echo "🔄 Recent Activity:"
    kubectl logs ingest-pdfs-new-collection --tail=3 2>/dev/null | grep -E "(Progress:|Flushed|Failed)" | tail -3 | sed 's/^/   /'
    echo ""
    
    echo "Press Ctrl+C to stop monitoring"
    echo "Refreshing in 10 seconds..."
    
    sleep 10
done
