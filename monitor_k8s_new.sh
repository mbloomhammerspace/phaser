#!/bin/bash

MASTER_IP="150.136.235.189"
WORKER1_IP="193.122.158.182"
WORKER2_IP="193.122.158.185"
SSH_KEY="~/.ssh/id_ed25519"

echo "=========================================="
echo "Kubernetes 1.30.4 Installation Monitor"
echo "=========================================="
echo "Timestamp: $(date)"
echo ""

echo "🔍 PROCESS MONITORING:"
echo "----------------------"
# Check if ansible-playbook is running on the local machine
if pgrep -f "ansible-playbook -i inventory.yml playbooks/01-kubespray.yml" > /dev/null; then
    echo "Checking Kubespray Deployment on local machine... ✅ RUNNING"
else
    echo "Checking Kubespray Deployment on local machine... ❌ NOT RUNNING"
fi

# Check if kubeadm is running on the master node
if ssh -i "$SSH_KEY" ubuntu@"$MASTER_IP" "pgrep -f kubeadm" > /dev/null 2>/dev/null; then
    echo "Checking Kubeadm Process on $MASTER_IP... ✅ RUNNING"
else
    echo "Checking Kubeadm Process on $MASTER_IP... ❌ NOT RUNNING"
fi

# Check if kubelet is running on the master node
if ssh -i "$SSH_KEY" ubuntu@"$MASTER_IP" "pgrep -f kubelet" > /dev/null 2>/dev/null; then
    echo "Checking Kubelet Process on $MASTER_IP... ✅ RUNNING"
else
    echo "Checking Kubelet Process on $MASTER_IP... ❌ NOT RUNNING"
fi
echo ""

echo "🔧 SERVICE STATUS:"
echo "------------------"
# Check containerd and kubelet service status on master
MASTER_CONTAINERD_STATUS=$(ssh -i "$SSH_KEY" ubuntu@"$MASTER_IP" "sudo systemctl is-active containerd" 2>/dev/null || echo "inactive")
MASTER_KUBELET_STATUS=$(ssh -i "$SSH_KEY" ubuntu@"$MASTER_IP" "sudo systemctl is-active kubelet" 2>/dev/null || echo "inactive")
echo "Checking Container Runtime on $MASTER_IP... $([ "$MASTER_CONTAINERD_STATUS" == "active" ] && echo "✅ ACTIVE" || echo "❌ INACTIVE")"
echo "Checking Kubelet Service on $MASTER_IP... $([ "$MASTER_KUBELET_STATUS" == "active" ] && echo "✅ ACTIVE" || echo "❌ INACTIVE")"

# Check containerd and kubelet service status on worker 1
WORKER1_CONTAINERD_STATUS=$(ssh -i "$SSH_KEY" ubuntu@"$WORKER1_IP" "sudo systemctl is-active containerd" 2>/dev/null || echo "inactive")
WORKER1_KUBELET_STATUS=$(ssh -i "$SSH_KEY" ubuntu@"$WORKER1_IP" "sudo systemctl is-active kubelet" 2>/dev/null || echo "inactive")
echo "Checking Container Runtime on $WORKER1_IP... $([ "$WORKER1_CONTAINERD_STATUS" == "active" ] && echo "✅ ACTIVE" || echo "❌ INACTIVE")"
echo "Checking Kubelet Service on $WORKER1_IP... $([ "$WORKER1_KUBELET_STATUS" == "active" ] && echo "✅ ACTIVE" || echo "❌ INACTIVE")"

# Check containerd and kubelet service status on worker 2
WORKER2_CONTAINERD_STATUS=$(ssh -i "$SSH_KEY" ubuntu@"$WORKER2_IP" "sudo systemctl is-active containerd" 2>/dev/null || echo "inactive")
WORKER2_KUBELET_STATUS=$(ssh -i "$SSH_KEY" ubuntu@"$WORKER2_IP" "sudo systemctl is-active kubelet" 2>/dev/null || echo "inactive")
echo "Checking Container Runtime on $WORKER2_IP... $([ "$WORKER2_CONTAINERD_STATUS" == "active" ] && echo "✅ ACTIVE" || echo "❌ INACTIVE")"
echo "Checking Kubelet Service on $WORKER2_IP... $([ "$WORKER2_KUBELET_STATUS" == "active" ] && echo "✅ ACTIVE" || echo "❌ INACTIVE")"
echo ""

echo "📦 KUBERNETES COMPONENTS:"
echo "-------------------------"
# Check if kubectl binary exists on master
if ssh -i "$SSH_KEY" ubuntu@"$MASTER_IP" "sudo test -f /usr/local/bin/kubectl" 2>/dev/null; then
    echo "Checking Kubectl Binary on $MASTER_IP... ✅ AVAILABLE"
    
    # Check cluster status
    if ssh -i "$SSH_KEY" ubuntu@"$MASTER_IP" "sudo /usr/local/bin/kubectl get nodes" > /dev/null 2>/dev/null; then
        echo "Checking Cluster Status on $MASTER_IP... ✅ CLUSTER READY"
        echo ""
        echo "📊 NODE STATUS:"
        echo "---------------"
        ssh -i "$SSH_KEY" ubuntu@"$MASTER_IP" "sudo /usr/local/bin/kubectl get nodes"
    else
        echo "Checking Cluster Status on $MASTER_IP... ❌ CLUSTER NOT READY"
    fi
else
    echo "Checking Kubectl Binary on $MASTER_IP... ❌ NOT AVAILABLE"
fi
echo ""

echo "📊 DETAILED STATUS:"
echo "-------------------"
echo "Latest kubelet activity on master:"
ssh -i "$SSH_KEY" ubuntu@"$MASTER_IP" "sudo tail -n 10 /var/log/kubelet.log 2>/dev/null || echo 'No log file found'"

echo ""
echo "Kubelet status on master:"
ssh -i "$SSH_KEY" ubuntu@"$MASTER_IP" "sudo systemctl status kubelet --no-pager -l" 2>/dev/null || echo "Service not available"
echo ""
echo "=========================================="
echo "Run this script again to check progress"
echo "=========================================="
