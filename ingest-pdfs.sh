#!/bin/bash
set -e

# NVIDIA RAG Blueprint PDF Ingestion Script
INGESTOR_URL="http://localhost:8082"
COLLECTION_NAME="hammerspace_docs"

echo "===NVIDIA RAG Blueprint PDF Ingestion==="
echo "Ingesting PDFs into collection: $COLLECTION_NAME"
echo ""

# Get the minio pod to access PDFs
MINIO_POD=$(kubectl --insecure-skip-tls-verify get pods -l app=minio -o jsonpath='{.items[0].metadata.name}')

# Get list of PDFs (excluding macOS metadata files)
echo "Fetching PDF list from storage..."
PDF_LIST=$(kubectl --insecure-skip-tls-verify exec $MINIO_POD -- sh -c "cd /data/pdf-test && for f in *.pdf; do case \$f in ._*) ;; *) echo /data/pdf-test/\$f ;; esac; done" 2>/dev/null)

if [ -z "$PDF_LIST" ]; then
    echo "ERROR: No PDFs found in /data/pdf-test"
    exit 1
fi

PDF_COUNT=$(echo "$PDF_LIST" | wc -l)
echo "Found $PDF_COUNT PDF files to ingest"
echo ""

# Process each PDF
COUNTER=0
TASK_IDS=()

while IFS= read -r PDF_PATH; do
    COUNTER=$((COUNTER + 1))
    PDF_NAME=$(basename "$PDF_PATH")
    
    echo "[$COUNTER/$PDF_COUNT] Ingesting: $PDF_NAME"
    
    # Copy PDF from minio pod to local temp (handle spaces in filenames)
    kubectl --insecure-skip-tls-verify exec $MINIO_POD -- sh -c "cat '$PDF_PATH'" > "/tmp/$PDF_NAME"
    
    # Upload to ingestor using NVIDIA Blueprint API
    DATA_JSON="{\"collection_name\": \"$COLLECTION_NAME\", \"blocking\": false, \"split_options\": {\"chunk_size\": 512, \"chunk_overlap\": 150}, \"generate_summary\": false}"
    
    RESPONSE=$(curl -s -X POST "$INGESTOR_URL/documents" \
        -F "documents=@/tmp/$PDF_NAME" \
        -F "data=$DATA_JSON")
    
    TASK_ID=$(echo "$RESPONSE" | jq -r '.task_id // empty')
    
    if [ -n "$TASK_ID" ]; then
        echo "  ✓ Task ID: $TASK_ID"
        TASK_IDS+=("$TASK_ID")
    else
        echo "  ✗ Failed: $RESPONSE"
    fi
    
    # Cleanup temp file
    rm -f "/tmp/$PDF_NAME"
    
    # Small delay to avoid overwhelming the API
    sleep 1
done <<< "$PDF_LIST"

echo ""
echo "===Ingestion Tasks Submitted==="
echo "Total tasks: ${#TASK_IDS[@]}"
echo ""

# Monitor task completion
echo "===Monitoring Ingestion Progress==="
ALL_COMPLETE=false
CHECK_COUNT=0
MAX_CHECKS=120  # 10 minutes max

while [ "$ALL_COMPLETE" = false ] && [ $CHECK_COUNT -lt $MAX_CHECKS ]; do
    CHECK_COUNT=$((CHECK_COUNT + 1))
    sleep 5
    
    PENDING=0
    COMPLETED=0
    FAILED=0
    
    for TASK_ID in "${TASK_IDS[@]}"; do
        STATUS_RESPONSE=$(curl -s "$INGESTOR_URL/status?task_id=$TASK_ID")
        STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status // "unknown"')
        
        case "$STATUS" in
            "completed")
                COMPLETED=$((COMPLETED + 1))
                ;;
            "failed")
                FAILED=$((FAILED + 1))
                ;;
            *)
                PENDING=$((PENDING + 1))
                ;;
        esac
    done
    
    echo "[Check $CHECK_COUNT] Completed: $COMPLETED, Pending: $PENDING, Failed: $FAILED"
    
    if [ $PENDING -eq 0 ]; then
        ALL_COMPLETE=true
    fi
done

echo ""
echo "===Ingestion Complete==="
echo "Completed: $COMPLETED"
echo "Failed: $FAILED"
echo ""

# Get final collection stats
echo "===Collection Statistics==="
DOCS_RESPONSE=$(curl -s "$INGESTOR_URL/documents?collection_name=$COLLECTION_NAME")
DOC_COUNT=$(echo "$DOCS_RESPONSE" | jq '.documents | length')
echo "Documents in collection: $DOC_COUNT"

# Get collection info from Milvus
echo ""
echo "===Verifying Milvus Collection==="
kubectl --insecure-skip-tls-verify exec $(kubectl --insecure-skip-tls-verify get pods -l app=milvus-gpu -o jsonpath='{.items[0].metadata.name}') -- \
    python3 -c "
from pymilvus import connections, Collection
connections.connect(host='localhost', port='19530')
try:
    collection = Collection('$COLLECTION_NAME')
    collection.load()
    print(f'Collection: $COLLECTION_NAME')
    print(f'Total entities (chunks): {collection.num_entities}')
    print('✓ Collection loaded and accessible')
except Exception as e:
    print(f'Error: {e}')
" 2>/dev/null || echo "Could not verify Milvus collection (pymilvus may not be installed)"

echo ""
echo "===Sending Pushover Notification==="

# Send Pushover notification
if [ -n "$PUSHOVER_TOKEN" ] && [ -n "$PUSHOVER_USER" ]; then
    MESSAGE="NVIDIA RAG Blueprint: Successfully ingested $COMPLETED PDFs into collection '$COLLECTION_NAME'. Total chunks/embeddings in Milvus ready for retrieval."
    
    curl -s \
      --form-string "token=$PUSHOVER_TOKEN" \
      --form-string "user=$PUSHOVER_USER" \
      --form-string "title=RAG Ingestion Complete" \
      --form-string "message=$MESSAGE" \
      --form-string "priority=0" \
      https://api.pushover.net/1/messages.json > /dev/null
    
    echo "✓ Pushover notification sent"
else
    echo "⚠ Pushover credentials not set (PUSHOVER_TOKEN, PUSHOVER_USER)"
    echo "  Set these environment variables to receive notifications"
fi

echo ""
echo "===Done==="

