#!/bin/bash

# Port-Forward Management Script
# This script manages persistent port-forwards using screen

case "$1" in
    "start")
        echo "🚀 Starting persistent port-forward session..."
        screen -dmS port-forwards bash -c "
            echo 'Starting persistent port-forward session...'
            pkill -f 'kubectl port-forward' 2>/dev/null || true
            sleep 2
            
            echo 'Starting port-forwards:'
            echo '1. RAG Frontend (Playground) - Port 3000'
            kubectl port-forward svc/clean-rag-frontend 3000:3000 --address=0.0.0.0 &
            sleep 1
            
            echo '2. Attu (Milvus GUI) - Port 3001'  
            kubectl port-forward svc/attu 3001:3001 --address=0.0.0.0 &
            sleep 1
            
            echo '3. Milvus Database - Port 19530'
            kubectl port-forward svc/milvus 19530:19530 --address=0.0.0.0 &
            sleep 1
            
            echo '4. RAG Server API - Port 8081'
            kubectl port-forward svc/rag-server 8081:8081 --address=0.0.0.0 &
            sleep 1
            
            echo '5. AI-Q Research Assistant - Port 8051'
            kubectl port-forward svc/aiq-aira-frontend 8051:3000 --address=0.0.0.0 &
            sleep 1
            
            echo ''
            echo 'All port-forwards started! Session will persist even if terminal closes.'
            echo 'To reconnect: screen -r port-forwards'
            echo 'To detach: Ctrl+A then D'
            echo ''
            
            while true; do
                sleep 30
                echo \"\$(date): Port-forwards active\"
            done
        "
        echo "✅ Port-forward session started in screen 'port-forwards'"
        ;;
        
    "status")
        echo "📊 Port-Forward Status:"
        echo "======================"
        echo ""
        echo "Screen sessions:"
        screen -list
        echo ""
        echo "Active port-forwards:"
        ps aux | grep "kubectl port-forward" | grep -v grep
        echo ""
        echo "Port mappings:"
        echo "  🌐 RAG Playground:     http://localhost:3000"
        echo "  🗄️  Attu (Milvus GUI):  http://localhost:3001" 
        echo "  💾 Milvus Database:    localhost:19530"
        echo "  🔌 RAG Server API:     localhost:8081"
        echo "  🤖 AI-Q Assistant:     http://localhost:8051"
        ;;
        
    "stop")
        echo "🛑 Stopping all port-forwards..."
        pkill -f 'kubectl port-forward'
        screen -S port-forwards -X quit 2>/dev/null || true
        echo "✅ All port-forwards stopped"
        ;;
        
    "restart")
        echo "🔄 Restarting port-forwards..."
        $0 stop
        sleep 2
        $0 start
        ;;
        
    "connect")
        echo "🔗 Connecting to port-forward session..."
        echo "Use Ctrl+A then D to detach from session"
        screen -r port-forwards
        ;;
        
    *)
        echo "Port-Forward Management Script"
        echo "=============================="
        echo ""
        echo "Usage: $0 {start|stop|restart|status|connect}"
        echo ""
        echo "Commands:"
        echo "  start   - Start persistent port-forwards in screen session"
        echo "  stop    - Stop all port-forwards and screen session"
        echo "  restart - Restart all port-forwards"
        echo "  status  - Show current status and port mappings"
        echo "  connect - Connect to the port-forward screen session"
        echo ""
        echo "The screen session ensures port-forwards persist even if terminal closes."
        echo "All port-forwards are backgrounded with & for reliability."
        ;;
esac
