#!/bin/bash

# Monitor NIMs and send Pushover notification when ready
# Requires: PUSHOVER_USER_KEY and PUSHOVER_API_TOKEN environment variables

echo "📡 Monitoring NIM services until ready..."
echo "Will send Pushover notification when all NIMs are operational"
echo ""

# Check if Pushover credentials are set
if [ -z "$PUSHOVER_USER_KEY" ] || [ -z "$PUSHOVER_API_TOKEN" ]; then
    echo "⚠️  Warning: PUSHOVER_USER_KEY and PUSHOVER_API_TOKEN not set"
    echo "   Set them with:"
    echo "   export PUSHOVER_USER_KEY='your_user_key'"
    echo "   export PUSHOVER_API_TOKEN='your_app_token'"
    echo ""
fi

send_pushover() {
    local message="$1"
    local title="$2"
    
    if [ -n "$PUSHOVER_USER_KEY" ] && [ -n "$PUSHOVER_API_TOKEN" ]; then
        curl -s \
          --form-string "token=$PUSHOVER_API_TOKEN" \
          --form-string "user=$PUSHOVER_USER_KEY" \
          --form-string "title=$title" \
          --form-string "message=$message" \
          https://api.pushover.net/1/messages.json > /dev/null
        echo "📱 Pushover notification sent!"
    else
        echo "📱 Pushover notification skipped (credentials not set)"
    fi
}

check_nim_ready() {
    local pod_label="$1"
    local pod_count=$(kubectl get pods -l "$pod_label" --field-selector=status.phase=Running 2>/dev/null | grep -c "1/1")
    echo $pod_count
}

# Monitor loop
while true; do
    clear
    echo "📡 NIM Services Status - $(date '+%H:%M:%S')"
    echo "======================================================"
    echo ""
    
    # Check NIM LLM
    echo "🤖 NIM LLM Service:"
    kubectl get pods -l app.kubernetes.io/instance=nim-llm-deploy -o wide | tail -1
    NIM_LLM_READY=$(check_nim_ready "app.kubernetes.io/instance=nim-llm-deploy")
    echo ""
    
    # Check if all are ready
    if [ "$NIM_LLM_READY" -ge 1 ]; then
        echo "======================================================"
        echo "🎉 ALL NIM SERVICES ARE READY!"
        echo "======================================================"
        echo ""
        echo "✅ NIM LLM: Operational"
        echo ""
        
        # Test the service
        echo "🧪 Testing NIM LLM endpoint..."
        POD=$(kubectl get pods -l app.kubernetes.io/instance=nim-llm-deploy -o jsonpath='{.items[0].metadata.name}')
        kubectl exec $POD -- sh -c "wget -q -O- http://localhost:8000/v1/models 2>/dev/null | head -c 100" || echo "Testing..."
        
        echo ""
        echo "Sending Pushover notification..."
        send_pushover "NVIDIA RAG Blueprint NIM services are now operational and ready for demo!" "✅ NIMs Ready!"
        
        echo ""
        echo "🌐 Access your RAG Playground at: http://localhost:30082"
        echo "   (via kubectl port-forward svc/nvidia-rag-playground-mcp 30082:3000)"
        exit 0
    else
        echo "⏳ Waiting for NIMs to become ready..."
        echo "   Refreshing in 30 seconds..."
        sleep 30
    fi
done
