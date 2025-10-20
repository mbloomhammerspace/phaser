#!/bin/bash

# Kubernetes Installation Monitor
# This script provides real-time status of the Kubernetes installation

MASTER_HOST="150.136.33.54"
WORKER_HOST="129.213.131.239"
SSH_KEY="~/.ssh/id_ed25519"

echo "=========================================="
echo "Kubernetes 1.31 Installation Monitor"
echo "=========================================="
echo "Timestamp: $(date)"
echo ""

# Function to check if a command is running
check_process() {
    local host=$1
    local process_name=$2
    local description=$3
    
    echo -n "Checking $description on $host... "
    if ssh -i $SSH_KEY -o ConnectTimeout=5 ubuntu@$host "ps aux | grep -v grep | grep '$process_name'" >/dev/null 2>&1; then
        echo "✅ RUNNING"
        return 0
    else
        echo "❌ NOT RUNNING"
        return 1
    fi
}

# Function to check service status
check_service() {
    local host=$1
    local service=$2
    local description=$3
    
    echo -n "Checking $description on $host... "
    if ssh -i $SSH_KEY -o ConnectTimeout=5 ubuntu@$host "sudo systemctl is-active $service" >/dev/null 2>&1; then
        echo "✅ ACTIVE"
        return 0
    else
        echo "❌ INACTIVE"
        return 1
    fi
}

# Function to check if kubectl is available
check_kubectl() {
    local host=$1
    local description=$2
    
    echo -n "Checking $description on $host... "
    if ssh -i $SSH_KEY -o ConnectTimeout=5 ubuntu@$host "ls -la /opt/kubespray/venv/bin/kubectl" >/dev/null 2>&1; then
        echo "✅ AVAILABLE"
        return 0
    else
        echo "❌ NOT AVAILABLE"
        return 1
    fi
}

# Function to check cluster status
check_cluster() {
    local host=$1
    local description=$2
    
    echo -n "Checking $description on $host... "
    if ssh -i $SSH_KEY -o ConnectTimeout=5 ubuntu@$host "/opt/kubespray/venv/bin/kubectl get nodes" >/dev/null 2>&1; then
        echo "✅ CLUSTER READY"
        return 0
    else
        echo "❌ CLUSTER NOT READY"
        return 1
    fi
}

echo "🔍 PROCESS MONITORING:"
echo "----------------------"
check_process $MASTER_HOST "ansible-playbook" "Kubespray Deployment"
check_process $MASTER_HOST "kubeadm" "Kubeadm Process"
check_process $MASTER_HOST "kubelet" "Kubelet Process"

echo ""
echo "🔧 SERVICE STATUS:"
echo "------------------"
check_service $MASTER_HOST "containerd" "Container Runtime"
check_service $MASTER_HOST "kubelet" "Kubelet Service"
check_service $WORKER_HOST "containerd" "Container Runtime"
check_service $WORKER_HOST "kubelet" "Kubelet Service"

echo ""
echo "📦 KUBERNETES COMPONENTS:"
echo "-------------------------"
check_kubectl $MASTER_HOST "Kubectl Binary"
check_cluster $MASTER_HOST "Cluster Status"

echo ""
echo "📊 DETAILED STATUS:"
echo "-------------------"

# Check kubespray logs
echo "Latest kubespray activity:"
ssh -i $SSH_KEY -o ConnectTimeout=5 ubuntu@$MASTER_HOST "tail -5 /opt/kubespray/cluster.yml.log 2>/dev/null || echo 'No log file found'"

echo ""
echo "Kubelet status on master:"
ssh -i $SSH_KEY -o ConnectTimeout=5 ubuntu@$MASTER_HOST "sudo systemctl status kubelet --no-pager -l | head -10"

echo ""
echo "=========================================="
echo "Run this script again to check progress"
echo "=========================================="
