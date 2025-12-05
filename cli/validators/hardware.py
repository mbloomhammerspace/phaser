"""Hardware requirements validation."""

import yaml
import subprocess
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class HardwareValidator:
    """Validates hardware requirements."""
    
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
                            "is_master": group_name == "kube_control_plane",
                            "has_gpu": host_vars.get("gpu_enabled", False)
                        })
        
        return nodes
    
    def _ssh_execute(self, node: Dict[str, Any], command: str) -> Dict[str, Any]:
        """Execute command on remote node via SSH."""
        ssh_key = Path(node["ssh_key"]).expanduser()
        if not ssh_key.exists():
            return {"success": False, "error": f"SSH key not found: {ssh_key}"}
        
        try:
            result = subprocess.run(
                [
                    "ssh",
                    "-i", str(ssh_key),
                    "-o", "StrictHostKeyChecking=no",
                    "-o", "ConnectTimeout=10",
                    f"{node['user']}@{node['ip']}",
                    command
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "SSH connection timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def validate_all(self) -> List[Dict[str, Any]]:
        """Run all hardware validation checks."""
        results = []
        nodes = self._get_nodes()
        
        if not nodes:
            results.append({
                "name": "Hardware Validation",
                "status": "fail",
                "message": "No nodes found in inventory file"
            })
            return results
        
        # Validate each node
        for node in nodes:
            node_results = self._validate_node(node)
            results.extend(node_results)
        
        return results
    
    def _validate_node(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate hardware for a single node."""
        results = []
        node_name = node["hostname"]
        
        # Check CPU
        cpu_result = self._check_cpu(node)
        results.append({
            "name": f"{node_name} - CPU",
            "status": cpu_result["status"],
            "message": cpu_result["message"]
        })
        
        # Check RAM
        ram_result = self._check_ram(node)
        results.append({
            "name": f"{node_name} - RAM",
            "status": ram_result["status"],
            "message": ram_result["message"]
        })
        
        # Check Storage
        storage_result = self._check_storage(node)
        results.append({
            "name": f"{node_name} - Storage",
            "status": storage_result["status"],
            "message": storage_result["message"]
        })
        
        # Check GPU (if GPU node)
        if node.get("has_gpu"):
            gpu_result = self._check_gpu(node)
            results.append({
                "name": f"{node_name} - GPU",
                "status": gpu_result["status"],
                "message": gpu_result["message"]
            })
        
        return results
    
    def _check_cpu(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Check CPU cores."""
        result = self._ssh_execute(node, "nproc")
        
        if not result["success"]:
            return {
                "status": "fail",
                "message": f"Cannot check CPU: {result.get('error', 'SSH failed')}"
            }
        
        try:
            cpu_count = int(result["stdout"].strip())
            min_cores = 4 if node.get("is_master") else 8
            
            if cpu_count >= min_cores:
                return {
                    "status": "pass",
                    "message": f"{cpu_count} cores (minimum: {min_cores})"
                }
            else:
                return {
                    "status": "warn",
                    "message": f"{cpu_count} cores (minimum: {min_cores} recommended)"
                }
        except ValueError:
            return {
                "status": "fail",
                "message": "Could not parse CPU count"
            }
    
    def _check_ram(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Check RAM."""
        result = self._ssh_execute(node, "free -m | awk '/^Mem:/{print $2}'")
        
        if not result["success"]:
            return {
                "status": "fail",
                "message": f"Cannot check RAM: {result.get('error', 'SSH failed')}"
            }
        
        try:
            ram_mb = int(result["stdout"].strip())
            ram_gb = ram_mb / 1024
            min_ram_gb = 8 if node.get("is_master") else 16
            
            if ram_gb >= min_ram_gb:
                return {
                    "status": "pass",
                    "message": f"{ram_gb:.1f} GB (minimum: {min_ram_gb} GB)"
                }
            else:
                return {
                    "status": "warn",
                    "message": f"{ram_gb:.1f} GB (minimum: {min_ram_gb} GB recommended)"
                }
        except ValueError:
            return {
                "status": "fail",
                "message": "Could not parse RAM"
            }
    
    def _check_storage(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Check available storage."""
        result = self._ssh_execute(node, "df -h / | awk 'NR==2 {print $4}'")
        
        if not result["success"]:
            return {
                "status": "fail",
                "message": f"Cannot check storage: {result.get('error', 'SSH failed')}"
            }
        
        storage_str = result["stdout"].strip()
        min_storage_gb = 50
        
        # Parse storage (handles formats like "50G", "50000M")
        try:
            if storage_str.endswith("G"):
                storage_gb = float(storage_str[:-1])
            elif storage_str.endswith("M"):
                storage_gb = float(storage_str[:-1]) / 1024
            else:
                storage_gb = float(storage_str) / (1024**3)  # Assume bytes
            
            if storage_gb >= min_storage_gb:
                return {
                    "status": "pass",
                    "message": f"{storage_gb:.1f} GB available (minimum: {min_storage_gb} GB)"
                }
            else:
                return {
                    "status": "warn",
                    "message": f"{storage_gb:.1f} GB available (minimum: {min_storage_gb} GB recommended)"
                }
        except (ValueError, AttributeError):
            return {
                "status": "warn",
                "message": f"Storage: {storage_str} (could not parse)"
            }
    
    def _check_gpu(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Check GPU availability."""
        # Check if nvidia-smi is available
        result = self._ssh_execute(node, "which nvidia-smi")
        
        if not result["success"] or not result["stdout"].strip():
            return {
                "status": "warn",
                "message": "nvidia-smi not found (GPU drivers may not be installed)"
            }
        
        # Check GPU count
        gpu_result = self._ssh_execute(node, "nvidia-smi --list-gpus | wc -l")
        
        if gpu_result["success"]:
            try:
                gpu_count = int(gpu_result["stdout"].strip())
                if gpu_count > 0:
                    # Get GPU model
                    model_result = self._ssh_execute(node, "nvidia-smi --query-gpu=name --format=csv,noheader | head -1")
                    gpu_model = model_result["stdout"].strip() if model_result["success"] else "Unknown"
                    
                    return {
                        "status": "pass",
                        "message": f"{gpu_count} GPU(s) detected: {gpu_model}"
                    }
                else:
                    return {
                        "status": "fail",
                        "message": "No GPUs detected"
                    }
            except ValueError:
                pass
        
        return {
            "status": "warn",
            "message": "GPU detected but could not get details"
        }

