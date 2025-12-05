"""Network connectivity validation."""

import yaml
import subprocess
import socket
from typing import List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class NetworkValidator:
    """Validates network connectivity."""
    
    def __init__(self, inventory_file: str):
        self.inventory_file = Path(inventory_file)
        self.inventory = self._load_inventory()
    
    def _load_inventory(self) -> Dict[str, Any]:
        """Load Ansible inventory file."""
        if not self.inventory_file.exists():
            return {}
        
        try:
            with open(self.inventory_file) as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Error loading inventory: {e}")
            return {}
    
    def _get_nodes(self) -> List[Dict[str, Any]]:
        """Extract node information from inventory."""
        nodes = []
        
        if not self.inventory:
            return nodes
        
        # Extract from kube_control_plane and kube_node groups
        for group_name in ["kube_control_plane", "kube_node"]:
            if "children" in self.inventory.get("all", {}):
                children = self.inventory["all"]["children"]
                if group_name in children and "hosts" in children[group_name]:
                    for hostname, host_vars in children[group_name]["hosts"].items():
                        nodes.append({
                            "hostname": hostname,
                            "ip": host_vars.get("ansible_host", ""),
                            "user": host_vars.get("ansible_user", "ubuntu"),
                            "ssh_key": host_vars.get("ansible_ssh_private_key_file", "~/.ssh/id_rsa"),
                            "is_master": group_name == "kube_control_plane"
                        })
        
        return nodes
    
    def validate_all(self) -> List[Dict[str, Any]]:
        """Run all network validation checks."""
        results = []
        nodes = self._get_nodes()
        
        if not nodes:
            results.append({
                "name": "Network Validation",
                "status": "fail",
                "message": "No nodes found in inventory file"
            })
            return results
        
        # Test SSH connectivity to all nodes
        for node in nodes:
            ssh_result = self._test_ssh(node)
            results.append({
                "name": f"{node['hostname']} - SSH",
                "status": ssh_result["status"],
                "message": ssh_result["message"]
            })
        
        # Test inter-node connectivity
        if len(nodes) > 1:
            connectivity_result = self._test_inter_node_connectivity(nodes)
            results.extend(connectivity_result)
        
        # Test required ports
        port_result = self._test_ports(nodes)
        results.extend(port_result)
        
        return results
    
    def _test_ssh(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Test SSH connectivity to a node."""
        ssh_key = Path(node["ssh_key"]).expanduser()
        if not ssh_key.exists():
            return {
                "status": "fail",
                "message": f"SSH key not found: {ssh_key}"
            }
        
        try:
            result = subprocess.run(
                [
                    "ssh",
                    "-i", str(ssh_key),
                    "-o", "StrictHostKeyChecking=no",
                    "-o", "ConnectTimeout=5",
                    "-o", "BatchMode=yes",
                    f"{node['user']}@{node['ip']}",
                    "echo 'SSH connection successful'"
                ],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {
                    "status": "pass",
                    "message": f"SSH connection successful to {node['ip']}"
                }
            else:
                return {
                    "status": "fail",
                    "message": f"SSH connection failed: {result.stderr.strip()}"
                }
        except subprocess.TimeoutExpired:
            return {
                "status": "fail",
                "message": "SSH connection timeout"
            }
        except Exception as e:
            return {
                "status": "fail",
                "message": f"SSH test error: {str(e)}"
            }
    
    def _test_inter_node_connectivity(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Test connectivity between nodes."""
        results = []
        
        # Test from first node to others
        if not nodes:
            return results
        
        master_node = next((n for n in nodes if n.get("is_master")), nodes[0])
        
        for node in nodes:
            if node["ip"] == master_node["ip"]:
                continue
            
            result = self._test_ping(master_node, node)
            results.append({
                "name": f"{master_node['hostname']} -> {node['hostname']}",
                "status": result["status"],
                "message": result["message"]
            })
        
        return results
    
    def _test_ping(self, from_node: Dict[str, Any], to_node: Dict[str, Any]) -> Dict[str, Any]:
        """Test ping from one node to another."""
        ssh_key = Path(from_node["ssh_key"]).expanduser()
        if not ssh_key.exists():
            return {
                "status": "fail",
                "message": "SSH key not found"
            }
        
        try:
            result = subprocess.run(
                [
                    "ssh",
                    "-i", str(ssh_key),
                    "-o", "StrictHostKeyChecking=no",
                    "-o", "ConnectTimeout=5",
                    "-o", "BatchMode=yes",
                    f"{from_node['user']}@{from_node['ip']}",
                    f"ping -c 3 -W 2 {to_node['ip']}"
                ],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                return {
                    "status": "pass",
                    "message": f"Ping successful to {to_node['ip']}"
                }
            else:
                return {
                    "status": "fail",
                    "message": f"Ping failed to {to_node['ip']}"
                }
        except Exception as e:
            return {
                "status": "fail",
                "message": f"Ping test error: {str(e)}"
            }
    
    def _test_ports(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Test required ports are accessible."""
        results = []
        
        # Required ports for Kubernetes
        required_ports = {
            6443: "Kubernetes API",
            2379: "etcd",
            2380: "etcd peer",
            10250: "kubelet",
            10256: "kube-proxy"
        }
        
        # Test ports on master nodes
        master_nodes = [n for n in nodes if n.get("is_master")]
        
        for node in master_nodes:
            for port, description in required_ports.items():
                result = self._test_port(node["ip"], port)
                results.append({
                    "name": f"{node['hostname']} - Port {port} ({description})",
                    "status": result["status"],
                    "message": result["message"]
                })
        
        return results
    
    def _test_port(self, host: str, port: int, timeout: int = 3) -> Dict[str, Any]:
        """Test if a port is open."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                return {
                    "status": "pass",
                    "message": f"Port {port} is open"
                }
            else:
                return {
                    "status": "warn",
                    "message": f"Port {port} is not accessible (may be firewalled)"
                }
        except Exception as e:
            return {
                "status": "warn",
                "message": f"Could not test port {port}: {str(e)}"
            }

