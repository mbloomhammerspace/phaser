#!/bin/bash

# Performance analysis script
echo "=== INGEST PERFORMANCE ANALYSIS ==="
echo "Analysis time: $(date)"
echo ""

# Get current processing statistics
echo "--- Current Processing Stats ---"
echo "Active GPU pods:"
kubectl get pods | grep -E "(nv-ingest-ms-runtime|rag-nv-ingest)" | grep Running | wc -l

echo ""
echo "--- Recent Processing Times (last 20 entries) ---"
kubectl logs ingestor-server-84697ff646-ksbtr --tail=100 2>/dev/null | grep -E "Time taken:" | tail -20

echo ""
echo "--- Resource Usage ---"
kubectl top pods | grep -E "(ingestor-server|rag-nv-ingest|nv-ingest-ms-runtime)" 2>/dev/null || echo "Metrics not available"

echo ""
echo "--- Processing Activity (last 10 minutes) ---"
kubectl logs ingestor-server-84697ff646-ksbtr --since=10m 2>/dev/null | grep -E "(Processing|batch|complete|documents)" | tail -10

echo ""
echo "=== PERFORMANCE SUMMARY ==="
echo "Monitoring will continue for 30 minutes..."
echo "Check back for final results at: $(date -d '+30 minutes')"
