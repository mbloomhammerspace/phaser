#!/usr/bin/env python3
"""
Preflight Checker for Kubernetes RAG Installer
Automatically discovers hardware capabilities and builds optimal deployment plans
"""

import os
import json
import subprocess
import logging
import paramiko
import yaml
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import concurrent.futures
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class NodeCapabilities:
    """Node hardware capabilities and specifications"""
    hostname: str
    ip_address: str
    username: str
    ssh_key_path: str
    
    # CPU Information
    cpu_cores: int = 0
    cpu_model: str = ""
    cpu_frequency: float = 0.0
    
    # Memory Information
    total_memory_gb: float = 0.0
    available_memory_gb: float = 0.0
    
    # Storage Information
    storage_devices: List[Dict[str, Any]] = None
    total_storage_gb: float = 0.0
    fast_storage_gb: float = 0.0  # NVMe/SSD storage
    
    # GPU Information
    gpu_devices: List[Dict[str, Any]] = None
    total_gpu_memory_gb: float = 0.0
    gpu_count: int = 0
    
    # Network Information
    network_interfaces: List[Dict[str, Any]] = None
    primary_interface: str = ""
    network_speed_gbps: float = 0.0
    
    # Operating System
    os_name: str = ""
    os_version: str = ""
    kernel_version: str = ""
    
    # Container Runtime
    docker_installed: bool = False
    containerd_installed: bool = False
    
    # Kubernetes
    kubernetes_installed: bool = False
    
    # Recommendations
    recommended_role: str = "worker"  # master, worker, gpu_worker
    recommended_priority: int = 1  # 1=highest priority
    
    def __post_init__(self):
        if self.storage_devices is None:
            self.storage_devices = []
        if self.gpu_devices is None:
            self.gpu_devices = []
        if self.network_interfaces is None:
            self.network_interfaces = []

class PreflightChecker:
    """Comprehensive preflight checker for Kubernetes RAG deployment"""
    
    def __init__(self, ssh_key_path: str = "~/.ssh/id_rsa"):
        self.ssh_key_path = os.path.expanduser(ssh_key_path)
        self.nodes: List[NodeCapabilities] = []
        self.deployment_plan: Dict[str, Any] = {}
        
    def discover_nodes(self, node_list: List[Dict[str, str]]) -> List[NodeCapabilities]:
        """Discover capabilities for all nodes in parallel"""
        logger.info(f"Starting hardware discovery for {len(node_list)} nodes...")
        
        # Create node objects
        self.nodes = []
        for node_info in node_list:
            node = NodeCapabilities(
                hostname=node_info['hostname'],
                ip_address=node_info['ip_address'],
                username=node_info['username'],
                ssh_key_path=self.ssh_key_path
            )
            self.nodes.append(node)
        
        # Discover capabilities in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(self.nodes), 10)) as executor:
            future_to_node = {
                executor.submit(self._discover_node_capabilities, node): node 
                for node in self.nodes
            }
            
            for future in concurrent.futures.as_completed(future_to_node):
                node = future_to_node[future]
                try:
                    future.result()
                    logger.info(f"✓ Completed discovery for {node.hostname}")
                except Exception as e:
                    logger.error(f"✗ Failed discovery for {node.hostname}: {str(e)}")
        
        return self.nodes
    
    def _discover_node_capabilities(self, node: NodeCapabilities):
        """Discover all capabilities for a single node"""
        try:
            # Test SSH connection
            if not self._test_ssh_connection(node):
                raise Exception("SSH connection failed")
            
            # Discover CPU information
            self._discover_cpu_info(node)
            
            # Discover memory information
            self._discover_memory_info(node)
            
            # Discover storage information
            self._discover_storage_info(node)
            
            # Discover GPU information
            self._discover_gpu_info(node)
            
            # Discover network information
            self._discover_network_info(node)
            
            # Discover OS information
            self._discover_os_info(node)
            
            # Discover container runtime
            self._discover_container_runtime(node)
            
            # Discover Kubernetes installation
            self._discover_kubernetes_info(node)
            
            # Generate recommendations
            self._generate_recommendations(node)
            
        except Exception as e:
            logger.error(f"Error discovering capabilities for {node.hostname}: {str(e)}")
            raise
    
    def _test_ssh_connection(self, node: NodeCapabilities) -> bool:
        """Test SSH connection to node"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                node.ip_address,
                username=node.username,
                key_filename=self.ssh_key_path,
                timeout=10
            )
            ssh.close()
            return True
        except Exception as e:
            logger.error(f"SSH connection failed for {node.hostname}: {str(e)}")
            return False
    
    def _discover_cpu_info(self, node: NodeCapabilities):
        """Discover CPU information"""
        try:
            ssh = self._get_ssh_connection(node)
            
            # Get CPU cores
            _, stdout, _ = ssh.exec_command("nproc")
            node.cpu_cores = int(stdout.read().decode().strip())
            
            # Get CPU model
            _, stdout, _ = ssh.exec_command("cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d: -f2 | xargs")
            node.cpu_model = stdout.read().decode().strip()
            
            # Get CPU frequency
            _, stdout, _ = ssh.exec_command("cat /proc/cpuinfo | grep 'cpu MHz' | head -1 | cut -d: -f2 | xargs")
            freq_str = stdout.read().decode().strip()
            if freq_str:
                node.cpu_frequency = float(freq_str) / 1000.0  # Convert to GHz
            
            ssh.close()
        except Exception as e:
            logger.warning(f"Failed to discover CPU info for {node.hostname}: {str(e)}")
    
    def _discover_memory_info(self, node: NodeCapabilities):
        """Discover memory information"""
        try:
            ssh = self._get_ssh_connection(node)
            
            # Get total memory
            _, stdout, _ = ssh.exec_command("free -g | grep Mem | awk '{print $2}'")
            node.total_memory_gb = float(stdout.read().decode().strip())
            
            # Get available memory
            _, stdout, _ = ssh.exec_command("free -g | grep Mem | awk '{print $7}'")
            node.available_memory_gb = float(stdout.read().decode().strip())
            
            ssh.close()
        except Exception as e:
            logger.warning(f"Failed to discover memory info for {node.hostname}: {str(e)}")
    
    def _discover_storage_info(self, node: NodeCapabilities):
        """Discover storage information"""
        try:
            ssh = self._get_ssh_connection(node)
            
            # Get all block devices
            _, stdout, _ = ssh.exec_command("lsblk -d -o NAME,SIZE,TYPE,MOUNTPOINT,ROTA --json")
            devices_json = stdout.read().decode().strip()
            
            if devices_json:
                devices_data = json.loads(devices_json)
                total_storage = 0.0
                fast_storage = 0.0
                
                for device in devices_data.get('blockdevices', []):
                    device_name = device.get('name', '')
                    device_size = device.get('size', '0G')
                    device_type = device.get('type', '')
                    device_rota = device.get('rota', '1')
                    
                    # Parse size (convert to GB)
                    size_gb = self._parse_size_to_gb(device_size)
                    total_storage += size_gb
                    
                    # Check if it's fast storage (NVMe or SSD)
                    if device_type == 'disk':
                        # Check if it's NVMe
                        if device_name.startswith('nvme'):
                            fast_storage += size_gb
                            device_type = 'nvme'
                        # Check if it's SSD (non-rotational)
                        elif device_rota == '0':
                            fast_storage += size_gb
                            device_type = 'ssd'
                        
                        node.storage_devices.append({
                            'name': device_name,
                            'size_gb': size_gb,
                            'type': device_type,
                            'mountpoint': device.get('mountpoint', ''),
                            'rotational': device_rota == '1'
                        })
                
                node.total_storage_gb = total_storage
                node.fast_storage_gb = fast_storage
            
            ssh.close()
        except Exception as e:
            logger.warning(f"Failed to discover storage info for {node.hostname}: {str(e)}")
    
    def _discover_gpu_info(self, node: NodeCapabilities):
        """Discover GPU information"""
        try:
            ssh = self._get_ssh_connection(node)
            
            # Check if nvidia-smi is available
            _, stdout, stderr = ssh.exec_command("which nvidia-smi")
            if stdout.read().decode().strip():
                # Get GPU information
                _, stdout, _ = ssh.exec_command("nvidia-smi --query-gpu=name,memory.total,index --format=csv,noheader,nounits")
                gpu_info = stdout.read().decode().strip()
                
                if gpu_info:
                    total_gpu_memory = 0.0
                    gpu_count = 0
                    
                    for line in gpu_info.split('\n'):
                        if line.strip():
                            parts = line.split(', ')
                            if len(parts) >= 2:
                                gpu_name = parts[0].strip()
                                gpu_memory = float(parts[1].strip())
                                gpu_index = int(parts[2].strip()) if len(parts) > 2 else gpu_count
                                
                                node.gpu_devices.append({
                                    'index': gpu_index,
                                    'name': gpu_name,
                                    'memory_gb': gpu_memory,
                                    'type': self._classify_gpu(gpu_name)
                                })
                                
                                total_gpu_memory += gpu_memory
                                gpu_count += 1
                    
                    node.total_gpu_memory_gb = total_gpu_memory
                    node.gpu_count = gpu_count
            
            ssh.close()
        except Exception as e:
            logger.warning(f"Failed to discover GPU info for {node.hostname}: {str(e)}")
    
    def _discover_network_info(self, node: NodeCapabilities):
        """Discover network information"""
        try:
            ssh = self._get_ssh_connection(node)
            
            # Get network interfaces
            _, stdout, _ = ssh.exec_command("ip -json addr show")
            interfaces_json = stdout.read().decode().strip()
            
            if interfaces_json:
                interfaces_data = json.loads(interfaces_json)
                
                for interface in interfaces_data:
                    ifname = interface.get('ifname', '')
                    if ifname and ifname != 'lo':  # Skip loopback
                        # Get interface speed
                        _, stdout, _ = ssh.exec_command(f"cat /sys/class/net/{ifname}/speed 2>/dev/null || echo '1000'")
                        speed_str = stdout.read().decode().strip()
                        speed_gbps = float(speed_str) / 1000.0 if speed_str.isdigit() else 1.0
                        
                        # Get IP addresses
                        addr_info = interface.get('addr_info', [])
                        ip_addresses = [addr.get('local', '') for addr in addr_info if addr.get('local')]
                        
                        node.network_interfaces.append({
                            'name': ifname,
                            'speed_gbps': speed_gbps,
                            'ip_addresses': ip_addresses,
                            'state': interface.get('operstate', 'unknown')
                        })
                        
                        # Set primary interface (first non-loopback with IP)
                        if not node.primary_interface and ip_addresses:
                            node.primary_interface = ifname
                            node.network_speed_gbps = speed_gbps
            
            ssh.close()
        except Exception as e:
            logger.warning(f"Failed to discover network info for {node.hostname}: {str(e)}")
    
    def _discover_os_info(self, node: NodeCapabilities):
        """Discover operating system information"""
        try:
            ssh = self._get_ssh_connection(node)
            
            # Get OS name and version
            _, stdout, _ = ssh.exec_command("cat /etc/os-release | grep -E '^(NAME|VERSION_ID)'")
            os_info = stdout.read().decode().strip()
            
            for line in os_info.split('\n'):
                if line.startswith('NAME='):
                    node.os_name = line.split('=', 1)[1].strip('"')
                elif line.startswith('VERSION_ID='):
                    node.os_version = line.split('=', 1)[1].strip('"')
            
            # Get kernel version
            _, stdout, _ = ssh.exec_command("uname -r")
            node.kernel_version = stdout.read().decode().strip()
            
            ssh.close()
        except Exception as e:
            logger.warning(f"Failed to discover OS info for {node.hostname}: {str(e)}")
    
    def _discover_container_runtime(self, node: NodeCapabilities):
        """Discover container runtime information"""
        try:
            ssh = self._get_ssh_connection(node)
            
            # Check for Docker
            _, stdout, _ = ssh.exec_command("which docker")
            node.docker_installed = bool(stdout.read().decode().strip())
            
            # Check for containerd
            _, stdout, _ = ssh.exec_command("which containerd")
            node.containerd_installed = bool(stdout.read().decode().strip())
            
            ssh.close()
        except Exception as e:
            logger.warning(f"Failed to discover container runtime for {node.hostname}: {str(e)}")
    
    def _discover_kubernetes_info(self, node: NodeCapabilities):
        """Discover Kubernetes installation information"""
        try:
            ssh = self._get_ssh_connection(node)
            
            # Check for kubectl
            _, stdout, _ = ssh.exec_command("which kubectl")
            node.kubernetes_installed = bool(stdout.read().decode().strip())
            
            ssh.close()
        except Exception as e:
            logger.warning(f"Failed to discover Kubernetes info for {node.hostname}: {str(e)}")
    
    def _generate_recommendations(self, node: NodeCapabilities):
        """Generate role recommendations based on hardware capabilities"""
        priority_score = 0
        
        # CPU scoring
        if node.cpu_cores >= 16:
            priority_score += 10
        elif node.cpu_cores >= 8:
            priority_score += 5
        elif node.cpu_cores >= 4:
            priority_score += 2
        
        # Memory scoring
        if node.total_memory_gb >= 64:
            priority_score += 10
        elif node.total_memory_gb >= 32:
            priority_score += 5
        elif node.total_memory_gb >= 16:
            priority_score += 2
        
        # Storage scoring
        if node.fast_storage_gb >= 500:
            priority_score += 10
        elif node.fast_storage_gb >= 100:
            priority_score += 5
        elif node.fast_storage_gb >= 50:
            priority_score += 2
        
        # Network scoring
        if node.network_speed_gbps >= 25:
            priority_score += 10
        elif node.network_speed_gbps >= 10:
            priority_score += 5
        elif node.network_speed_gbps >= 1:
            priority_score += 2
        
        # GPU scoring (heavily weighted)
        if node.gpu_count > 0:
            priority_score += 20
            if node.total_gpu_memory_gb >= 80:
                priority_score += 15
            elif node.total_gpu_memory_gb >= 48:
                priority_score += 12
            elif node.total_gpu_memory_gb >= 40:
                priority_score += 10
            elif node.total_gpu_memory_gb >= 24:
                priority_score += 8
            elif node.total_gpu_memory_gb >= 16:
                priority_score += 5
            elif node.total_gpu_memory_gb >= 8:
                priority_score += 3
        
        # Determine role
        if node.gpu_count > 0:
            node.recommended_role = "gpu_worker"
        elif priority_score >= 15:
            node.recommended_role = "master"
        else:
            node.recommended_role = "worker"
        
        node.recommended_priority = priority_score
    
    def build_deployment_plan(self) -> Dict[str, Any]:
        """Build optimal deployment plan based on discovered capabilities"""
        logger.info("Building deployment plan based on discovered capabilities...")
        
        # Sort nodes by priority
        sorted_nodes = sorted(self.nodes, key=lambda x: x.recommended_priority, reverse=True)
        
        # Select master node (highest priority non-GPU node)
        master_node = None
        for node in sorted_nodes:
            if node.recommended_role == "master":
                master_node = node
                break
        
        if not master_node:
            # Fallback: select highest priority node as master
            master_node = sorted_nodes[0]
            master_node.recommended_role = "master"
        
        # Select GPU worker nodes
        gpu_workers = [node for node in sorted_nodes if node.recommended_role == "gpu_worker"]
        
        # Select regular worker nodes
        regular_workers = [node for node in sorted_nodes 
                          if node.recommended_role == "worker" and node != master_node]
        
        # Build deployment plan
        self.deployment_plan = {
            'timestamp': datetime.now().isoformat(),
            'master_node': {
                'hostname': master_node.hostname,
                'ip_address': master_node.ip_address,
                'capabilities': self._node_to_dict(master_node)
            },
            'gpu_worker_nodes': [
                {
                    'hostname': node.hostname,
                    'ip_address': node.ip_address,
                    'capabilities': self._node_to_dict(node)
                }
                for node in gpu_workers
            ],
            'worker_nodes': [
                {
                    'hostname': node.hostname,
                    'ip_address': node.ip_address,
                    'capabilities': self._node_to_dict(node)
                }
                for node in regular_workers
            ],
            'summary': {
                'total_nodes': len(self.nodes),
                'master_nodes': 1,
                'gpu_worker_nodes': len(gpu_workers),
                'worker_nodes': len(regular_workers),
                'total_gpus': sum(node.gpu_count for node in self.nodes),
                'total_gpu_memory_gb': sum(node.total_gpu_memory_gb for node in self.nodes),
                'total_cpu_cores': sum(node.cpu_cores for node in self.nodes),
                'total_memory_gb': sum(node.total_memory_gb for node in self.nodes),
                'total_storage_gb': sum(node.total_storage_gb for node in self.nodes)
            },
            'recommendations': self._generate_recommendations_summary()
        }
        
        return self.deployment_plan
    
    def generate_inventory(self, username: str) -> str:
        """Generate Ansible inventory file based on deployment plan"""
        inventory = {
            'all': {
                'children': {
                    'kube_control_plane': {
                        'hosts': {
                            self.deployment_plan['master_node']['hostname']: {
                                'ansible_host': self.deployment_plan['master_node']['ip_address'],
                                'ansible_user': username,
                                'ansible_ssh_private_key_file': self.ssh_key_path,
                                'ansible_ssh_common_args': '-o StrictHostKeyChecking=no'
                            }
                        }
                    },
                    'kube_node': {
                        'hosts': {}
                    },
                    'k8s_cluster': {
                        'children': ['kube_control_plane', 'kube_node'],
                        'vars': {
                            'ansible_python_interpreter': '/usr/bin/python3',
                            'ansible_user': username,
                            'ansible_ssh_private_key_file': self.ssh_key_path,
                            'ansible_ssh_common_args': '-o StrictHostKeyChecking=no'
                        }
                    }
                }
            }
        }
        
        # Add GPU worker nodes
        for gpu_node in self.deployment_plan['gpu_worker_nodes']:
            inventory['all']['children']['kube_node']['hosts'][gpu_node['hostname']] = {
                'ansible_host': gpu_node['ip_address'],
                'ansible_user': username,
                'ansible_ssh_private_key_file': self.ssh_key_path,
                'ansible_ssh_common_args': '-o StrictHostKeyChecking=no',
                'gpu_enabled': True
            }
        
        # Add regular worker nodes
        for worker_node in self.deployment_plan['worker_nodes']:
            inventory['all']['children']['kube_node']['hosts'][worker_node['hostname']] = {
                'ansible_host': worker_node['ip_address'],
                'ansible_user': username,
                'ansible_ssh_private_key_file': self.ssh_key_path,
                'ansible_ssh_common_args': '-o StrictHostKeyChecking=no',
                'gpu_enabled': False
            }
        
        return yaml.dump(inventory, default_flow_style=False, sort_keys=False)
    
    def generate_report(self) -> str:
        """Generate comprehensive discovery report"""
        report = []
        report.append("# Kubernetes RAG Installer - Hardware Discovery Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        report.append("## Summary")
        report.append(f"- Total Nodes: {len(self.nodes)}")
        report.append(f"- Master Nodes: 1")
        report.append(f"- GPU Worker Nodes: {len([n for n in self.nodes if n.recommended_role == 'gpu_worker'])}")
        report.append(f"- Regular Worker Nodes: {len([n for n in self.nodes if n.recommended_role == 'worker'])}")
        report.append(f"- Total GPUs: {sum(n.gpu_count for n in self.nodes)}")
        report.append(f"- Total GPU Memory: {sum(n.total_gpu_memory_gb for n in self.nodes):.1f} GB")
        report.append(f"- Total CPU Cores: {sum(n.cpu_cores for n in self.nodes)}")
        report.append(f"- Total Memory: {sum(n.total_memory_gb for n in self.nodes):.1f} GB")
        report.append(f"- Total Storage: {sum(n.total_storage_gb for n in self.nodes):.1f} GB")
        report.append("")
        
        # Node details
        for i, node in enumerate(sorted(self.nodes, key=lambda x: x.recommended_priority, reverse=True), 1):
            report.append(f"## Node {i}: {node.hostname} ({node.ip_address})")
            report.append(f"- **Role**: {node.recommended_role.upper()}")
            report.append(f"- **Priority Score**: {node.recommended_priority}")
            report.append(f"- **OS**: {node.os_name} {node.os_version}")
            report.append(f"- **Kernel**: {node.kernel_version}")
            report.append(f"- **CPU**: {node.cpu_cores} cores, {node.cpu_model}")
            report.append(f"- **Memory**: {node.total_memory_gb:.1f} GB total, {node.available_memory_gb:.1f} GB available")
            report.append(f"- **Storage**: {node.total_storage_gb:.1f} GB total, {node.fast_storage_gb:.1f} GB fast storage")
            
            if node.gpu_devices:
                report.append(f"- **GPUs**: {node.gpu_count} devices, {node.total_gpu_memory_gb:.1f} GB total")
                for gpu in node.gpu_devices:
                    report.append(f"  - GPU {gpu['index']}: {gpu['name']} ({gpu['memory_gb']:.1f} GB)")
            
            if node.network_interfaces:
                report.append(f"- **Network**: {node.network_speed_gbps:.1f} Gbps primary interface")
            
            report.append(f"- **Container Runtime**: Docker={node.docker_installed}, Containerd={node.containerd_installed}")
            report.append(f"- **Kubernetes**: {node.kubernetes_installed}")
            report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        recommendations = self._generate_recommendations_summary()
        for rec in recommendations:
            report.append(f"- {rec}")
        report.append("")
        
        return "\n".join(report)
    
    def _get_ssh_connection(self, node: NodeCapabilities) -> paramiko.SSHClient:
        """Get SSH connection to node"""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            node.ip_address,
            username=node.username,
            key_filename=self.ssh_key_path,
            timeout=10
        )
        return ssh
    
    def _parse_size_to_gb(self, size_str: str) -> float:
        """Parse size string to GB"""
        try:
            size_str = size_str.strip().upper()
            if size_str.endswith('G'):
                return float(size_str[:-1])
            elif size_str.endswith('T'):
                return float(size_str[:-1]) * 1024
            elif size_str.endswith('M'):
                return float(size_str[:-1]) / 1024
            else:
                return float(size_str) / (1024**3)  # Assume bytes
        except:
            return 0.0
    
    def _classify_gpu(self, gpu_name: str) -> str:
        """Classify GPU type based on name"""
        gpu_name = gpu_name.lower()
        if 'a100' in gpu_name:
            return 'A100'
        elif 'h100' in gpu_name:
            return 'H100'
        elif 'v100' in gpu_name:
            return 'V100'
        elif 'rtx 4090' in gpu_name:
            return 'RTX4090'
        elif 'rtx 4080' in gpu_name:
            return 'RTX4080'
        elif 'm6000' in gpu_name:
            return 'M6000'
        elif 'l40' in gpu_name:
            return 'L40'
        elif 't4' in gpu_name:
            return 'T4'
        elif 'l4' in gpu_name:
            return 'L4'
        elif 'rtx 6000' in gpu_name:
            return 'RTX6000'
        else:
            return 'Other'
    
    def _node_to_dict(self, node: NodeCapabilities) -> Dict[str, Any]:
        """Convert node to dictionary for JSON serialization"""
        return {
            'cpu_cores': node.cpu_cores,
            'cpu_model': node.cpu_model,
            'cpu_frequency': node.cpu_frequency,
            'total_memory_gb': node.total_memory_gb,
            'available_memory_gb': node.available_memory_gb,
            'storage_devices': node.storage_devices,
            'total_storage_gb': node.total_storage_gb,
            'fast_storage_gb': node.fast_storage_gb,
            'gpu_devices': node.gpu_devices,
            'total_gpu_memory_gb': node.total_gpu_memory_gb,
            'gpu_count': node.gpu_count,
            'network_interfaces': node.network_interfaces,
            'primary_interface': node.primary_interface,
            'network_speed_gbps': node.network_speed_gbps,
            'os_name': node.os_name,
            'os_version': node.os_version,
            'kernel_version': node.kernel_version,
            'docker_installed': node.docker_installed,
            'containerd_installed': node.containerd_installed,
            'kubernetes_installed': node.kubernetes_installed,
            'recommended_role': node.recommended_role,
            'recommended_priority': node.recommended_priority
        }
    
    def _generate_recommendations_summary(self) -> List[str]:
        """Generate summary recommendations"""
        recommendations = []
        
        total_gpus = sum(node.gpu_count for node in self.nodes)
        total_memory = sum(node.total_memory_gb for node in self.nodes)
        total_storage = sum(node.total_storage_gb for node in self.nodes)
        
        if total_gpus == 0:
            recommendations.append("⚠️  No GPUs detected. RAG performance will be limited to CPU-only operations.")
        elif total_gpus < 2:
            recommendations.append("⚠️  Limited GPU resources. Consider adding more GPU nodes for production workloads.")
        else:
            recommendations.append("✅ Sufficient GPU resources detected for production RAG workloads.")
        
        if total_memory < 64:
            recommendations.append("⚠️  Limited memory resources. Consider adding more RAM for optimal performance.")
        else:
            recommendations.append("✅ Sufficient memory resources detected.")
        
        if total_storage < 500:
            recommendations.append("⚠️  Limited storage resources. Consider adding more storage for large datasets.")
        else:
            recommendations.append("✅ Sufficient storage resources detected.")
        
        # Check for fast storage
        fast_storage = sum(node.fast_storage_gb for node in self.nodes)
        if fast_storage < 100:
            recommendations.append("⚠️  Limited fast storage (NVMe/SSD). Consider adding NVMe storage for better performance.")
        else:
            recommendations.append("✅ Sufficient fast storage detected.")
        
        return recommendations


def main():
    """Command-line interface for preflight checker"""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description='Kubernetes RAG Preflight Checker')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Discover command
    discover_parser = subparsers.add_parser('discover', help='Discover hardware capabilities')
    discover_parser.add_argument('nodes_file', help='JSON file with node information')
    discover_parser.add_argument('ssh_key_path', help='SSH private key path')
    discover_parser.add_argument('output_dir', help='Output directory for results')
    
    # Generate inventory command
    inventory_parser = subparsers.add_parser('generate-inventory', help='Generate Ansible inventory')
    inventory_parser.add_argument('plan_file', help='Deployment plan JSON file')
    inventory_parser.add_argument('username', help='SSH username')
    inventory_parser.add_argument('ssh_key_path', help='SSH private key path')
    
    # Generate Kubespray config command
    kubespray_parser = subparsers.add_parser('generate-kubespray-config', help='Generate Kubespray configuration')
    kubespray_parser.add_argument('plan_file', help='Deployment plan JSON file')
    
    # Generate RAG config command
    rag_parser = subparsers.add_parser('generate-rag-config', help='Generate RAG configuration')
    rag_parser.add_argument('plan_file', help='Deployment plan JSON file')
    
    args = parser.parse_args()
    
    if args.command == 'discover':
        # Load nodes from JSON file
        with open(args.nodes_file, 'r') as f:
            node_list = json.load(f)
        
        # Initialize preflight checker
        checker = PreflightChecker(args.ssh_key_path)
        
        # Discover nodes
        nodes = checker.discover_nodes(node_list)
        
        # Build deployment plan
        plan = checker.build_deployment_plan()
        
        # Save results
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Save deployment plan
        plan_file = os.path.join(args.output_dir, 'deployment_plan.json')
        with open(plan_file, 'w') as f:
            json.dump(plan, f, indent=2)
        
        # Save discovery report
        report_file = os.path.join(args.output_dir, 'discovery_report.md')
        with open(report_file, 'w') as f:
            f.write(checker.generate_report())
        
        # Save inventory
        inventory_file = os.path.join(args.output_dir, 'inventory.yml')
        with open(inventory_file, 'w') as f:
            f.write(checker.generate_inventory('ubuntu'))
        
        print(f"Discovery completed. Results saved to {args.output_dir}")
        return 0
    
    elif args.command == 'generate-inventory':
        # Load deployment plan
        with open(args.plan_file, 'r') as f:
            plan = json.load(f)
        
        # Create temporary checker to generate inventory
        checker = PreflightChecker()
        checker.deployment_plan = plan
        
        # Generate and print inventory
        inventory = checker.generate_inventory(args.username)
        print(inventory)
        return 0
    
    elif args.command == 'generate-kubespray-config':
        # Load deployment plan
        with open(args.plan_file, 'r') as f:
            plan = json.load(f)
        
        # Generate Kubespray configuration
        config = generate_kubespray_config(plan)
        print(yaml.dump(config, default_flow_style=False, sort_keys=False))
        return 0
    
    elif args.command == 'generate-rag-config':
        # Load deployment plan
        with open(args.plan_file, 'r') as f:
            plan = json.load(f)
        
        # Generate RAG configuration
        config = generate_rag_config(plan)
        print(yaml.dump(config, default_flow_style=False, sort_keys=False))
        return 0
    
    else:
        parser.print_help()
        return 1


def generate_kubespray_config(plan: Dict[str, Any]) -> Dict[str, Any]:
    """Generate Kubespray configuration based on deployment plan"""
    total_nodes = plan['summary']['total_nodes']
    total_gpus = plan['summary']['total_gpus']
    
    config = {
        'kube_version': 'v1.28.0',
        'container_manager': 'containerd',
        'network_plugin': 'calico',
        'dns_mode': 'coredns',
        'helm_enabled': True,
        'metrics_server_enabled': True,
        'local_path_provisioner_enabled': True,
        'prometheus_enabled': True,
        'grafana_enabled': True,
        'nvidia_gpu_enabled': total_gpus > 0,
        'nvidia_driver_enabled': total_gpus > 0,
        'podsecuritypolicy_enabled': False,
        'rbac_enabled': True,
        'containerd': {
            'version': '1.6.21',
            'systemd_cgroup': True
        },
        'calico': {
            'version': 'v3.26.0',
            'ipip_mode': 'Always',
            'vxlan_mode': 'Never'
        },
        'local_volume_provisioner': {
            'enabled': True,
            'storage_class': 'local-path'
        }
    }
    
    # Adjust configuration based on cluster size
    if total_nodes >= 10:
        config['etcd_deployment_type'] = 'host'
        config['kube_controller_manager_extra_args'] = {
            'node-cidr-mask-size': '24'
        }
    else:
        config['etcd_deployment_type'] = 'host'
    
    return config


def generate_rag_config(plan: Dict[str, Any]) -> Dict[str, Any]:
    """Generate RAG configuration based on deployment plan"""
    total_gpus = plan['summary']['total_gpus']
    total_gpu_memory = plan['summary']['total_gpu_memory_gb']
    gpu_worker_count = len(plan['gpu_worker_nodes'])
    
    config = {
        'rag_system': {
            'enabled': True,
            'namespace': 'rag-system',
            'replicas': {
                'rag_server': max(1, gpu_worker_count),
                'rag_playground': 1,
                'ingestor_server': 1
            },
            'resources': {
                'rag_server': {
                    'requests': {
                        'cpu': '500m',
                        'memory': '2Gi',
                        'nvidia.com/gpu': '1' if total_gpus > 0 else '0'
                    },
                    'limits': {
                        'cpu': '2000m',
                        'memory': '8Gi',
                        'nvidia.com/gpu': '1' if total_gpus > 0 else '0'
                    }
                }
            }
        },
        'milvus': {
            'enabled': True,
            'namespace': 'milvus',
            'gpu_enabled': total_gpus > 0,
            'resources': {
                'requests': {
                    'cpu': '1000m',
                    'memory': '4Gi',
                    'nvidia.com/gpu': '1' if total_gpus > 0 else '0'
                },
                'limits': {
                    'cpu': '4000m',
                    'memory': '16Gi',
                    'nvidia.com/gpu': '1' if total_gpus > 0 else '0'
                }
            }
        },
        'nemo_services': {
            'enabled': True,
            'namespace': 'nemo-system',
            'services': {
                'embedding': {
                    'replicas': max(1, gpu_worker_count),
                    'resources': {
                        'requests': {
                            'cpu': '500m',
                            'memory': '2Gi',
                            'nvidia.com/gpu': '1' if total_gpus > 0 else '0'
                        },
                        'limits': {
                            'cpu': '2000m',
                            'memory': '8Gi',
                            'nvidia.com/gpu': '1' if total_gpus > 0 else '0'
                        }
                    }
                },
                'reranking': {
                    'replicas': max(1, gpu_worker_count),
                    'resources': {
                        'requests': {
                            'cpu': '500m',
                            'memory': '2Gi',
                            'nvidia.com/gpu': '1' if total_gpus > 0 else '0'
                        },
                        'limits': {
                            'cpu': '2000m',
                            'memory': '8Gi',
                            'nvidia.com/gpu': '1' if total_gpus > 0 else '0'
                        }
                    }
                },
                'llm': {
                    'replicas': max(1, gpu_worker_count),
                    'resources': {
                        'requests': {
                            'cpu': '1000m',
                            'memory': '4Gi',
                            'nvidia.com/gpu': '1' if total_gpus > 0 else '0'
                        },
                        'limits': {
                            'cpu': '4000m',
                            'memory': '16Gi',
                            'nvidia.com/gpu': '1' if total_gpus > 0 else '0'
                        }
                    }
                }
            }
        },
        'observability': {
            'enabled': True,
            'namespace': 'observability',
            'components': {
                'opentelemetry': True,
                'jaeger': True,
                'zipkin': True,
                'attu': True,
                'prometheus': True,
                'grafana': True
            }
        }
    }
    
    return config


if __name__ == '__main__':
    sys.exit(main())
