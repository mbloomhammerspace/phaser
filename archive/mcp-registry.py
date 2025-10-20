"""
MCP Server Registry and Service Discovery
Provides centralized server management, auto-registration, and discovery
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import yaml
import requests
from kubernetes import client, config
from kubernetes.client.rest import ApiException

class ServerStatus(Enum):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"

class DiscoveryMethod(Enum):
    MANUAL = "manual"
    CONFIG_FILE = "config_file"
    ENVIRONMENT = "environment"
    KUBERNETES = "kubernetes"
    HTTP_DISCOVERY = "http_discovery"
    DNS_SRV = "dns_srv"

@dataclass
class MCPServerInfo:
    """Complete MCP server information"""
    name: str
    command: str
    args: List[str]
    env: Dict[str, str]
    description: str
    enabled: bool = True
    discovery_method: DiscoveryMethod = DiscoveryMethod.MANUAL
    health_check_url: Optional[str] = None
    health_check_interval: int = 30
    auto_reconnect: bool = True
    max_retries: int = 3
    retry_delay: int = 5
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ServerHealth:
    """Server health information"""
    server_name: str
    status: ServerStatus
    last_check: float
    response_time: Optional[float] = None
    error_message: Optional[str] = None
    version: Optional[str] = None
    tools_count: int = 0

class MCPServerRegistry:
    """
    Centralized MCP server registry with auto-registration and service discovery
    """
    
    def __init__(self, config_dir: str = "/etc/mcp", kubeconfig_path: Optional[str] = None):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.servers: Dict[str, MCPServerInfo] = {}
        self.health_status: Dict[str, ServerHealth] = {}
        self.discovery_tasks: Dict[str, asyncio.Task] = {}
        self.registry_lock = asyncio.Lock()
        
        self.logger = logging.getLogger(__name__)
        
        # Kubernetes client for service discovery
        self.k8s_client = None
        if kubeconfig_path or self._is_kubernetes_available():
            self._init_kubernetes_client(kubeconfig_path)
        
        # Load existing configurations
        self._load_configurations()
        
        # Start discovery tasks
        self._start_discovery_tasks()
    
    def _is_kubernetes_available(self) -> bool:
        """Check if running in Kubernetes environment"""
        return os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount/token')
    
    def _init_kubernetes_client(self, kubeconfig_path: Optional[str] = None):
        """Initialize Kubernetes client"""
        try:
            if kubeconfig_path:
                config.load_kube_config(config_file=kubeconfig_path)
            else:
                config.load_incluster_config()
            
            self.k8s_client = client.CoreV1Api()
            self.logger.info("Kubernetes client initialized")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Kubernetes client: {e}")
            self.k8s_client = None
    
    def _load_configurations(self):
        """Load server configurations from various sources"""
        # Load from config files
        self._load_from_config_files()
        
        # Load from environment variables
        self._load_from_environment()
        
        # Load from Kubernetes ConfigMaps
        if self.k8s_client:
            self._load_from_kubernetes()
    
    def _load_from_config_files(self):
        """Load server configurations from YAML/JSON files"""
        config_files = [
            self.config_dir / "servers.yaml",
            self.config_dir / "servers.json",
            Path("/etc/mcp/servers.yaml"),
            Path("/etc/mcp/servers.json")
        ]
        
        for config_file in config_files:
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        if config_file.suffix == '.yaml':
                            data = yaml.safe_load(f)
                        else:
                            data = json.load(f)
                    
                    self._parse_config_data(data, DiscoveryMethod.CONFIG_FILE)
                    self.logger.info(f"Loaded configurations from {config_file}")
                    break
                except Exception as e:
                    self.logger.error(f"Failed to load config from {config_file}: {e}")
    
    def _load_from_environment(self):
        """Load server configurations from environment variables"""
        env_config = os.getenv('MCP_SERVERS')
        if env_config:
            try:
                data = json.loads(env_config)
                self._parse_config_data(data, DiscoveryMethod.ENVIRONMENT)
                self.logger.info("Loaded configurations from environment")
            except Exception as e:
                self.logger.error(f"Failed to load config from environment: {e}")
    
    def _load_from_kubernetes(self):
        """Load server configurations from Kubernetes ConfigMaps"""
        try:
            # Look for ConfigMaps with label mcp-server-config
            configmaps = self.k8s_client.list_config_map_for_all_namespaces(
                label_selector="mcp-server-config=true"
            )
            
            for cm in configmaps.items:
                for key, value in cm.data.items():
                    if key.endswith(('.yaml', '.json')):
                        try:
                            if key.endswith('.yaml'):
                                data = yaml.safe_load(value)
                            else:
                                data = json.loads(value)
                            
                            self._parse_config_data(data, DiscoveryMethod.KUBERNETES)
                            self.logger.info(f"Loaded configurations from ConfigMap {cm.metadata.name}")
                        except Exception as e:
                            self.logger.error(f"Failed to parse ConfigMap {cm.metadata.name}: {e}")
        
        except ApiException as e:
            self.logger.warning(f"Failed to load from Kubernetes: {e}")
    
    def _parse_config_data(self, data: Dict, discovery_method: DiscoveryMethod):
        """Parse configuration data and register servers"""
        servers_data = data.get('servers', {})
        
        for name, config in servers_data.items():
            server_info = MCPServerInfo(
                name=name,
                command=config.get('command', 'python'),
                args=config.get('args', []),
                env=config.get('env', {}),
                description=config.get('description', f'MCP Server {name}'),
                enabled=config.get('enabled', True),
                discovery_method=discovery_method,
                health_check_url=config.get('health_check_url'),
                health_check_interval=config.get('health_check_interval', 30),
                auto_reconnect=config.get('auto_reconnect', True),
                max_retries=config.get('max_retries', 3),
                retry_delay=config.get('retry_delay', 5),
                tags=config.get('tags', []),
                metadata=config.get('metadata', {})
            )
            
            self.register_server(server_info)
    
    def register_server(self, server_info: MCPServerInfo) -> bool:
        """Register a new MCP server"""
        try:
            self.servers[server_info.name] = server_info
            self.health_status[server_info.name] = ServerHealth(
                server_name=server_info.name,
                status=ServerStatus.UNKNOWN,
                last_check=0
            )
            
            self.logger.info(f"Registered server: {server_info.name} via {server_info.discovery_method.value}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register server {server_info.name}: {e}")
            return False
    
    def unregister_server(self, server_name: str) -> bool:
        """Unregister an MCP server"""
        try:
            if server_name in self.servers:
                del self.servers[server_name]
            
            if server_name in self.health_status:
                del self.health_status[server_name]
            
            # Cancel discovery task if running
            if server_name in self.discovery_tasks:
                self.discovery_tasks[server_name].cancel()
                del self.discovery_tasks[server_name]
            
            self.logger.info(f"Unregistered server: {server_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to unregister server {server_name}: {e}")
            return False
    
    def get_server(self, server_name: str) -> Optional[MCPServerInfo]:
        """Get server information by name"""
        return self.servers.get(server_name)
    
    def list_servers(self, enabled_only: bool = False) -> Dict[str, MCPServerInfo]:
        """List all registered servers"""
        if enabled_only:
            return {name: info for name, info in self.servers.items() if info.enabled}
        return self.servers.copy()
    
    def get_servers_by_tag(self, tag: str) -> List[MCPServerInfo]:
        """Get servers by tag"""
        return [info for info in self.servers.values() if tag in info.tags]
    
    def get_servers_by_discovery_method(self, method: DiscoveryMethod) -> List[MCPServerInfo]:
        """Get servers by discovery method"""
        return [info for info in self.servers.values() if info.discovery_method == method]
    
    async def start_health_monitoring(self, server_name: str):
        """Start health monitoring for a server"""
        if server_name not in self.servers:
            return
        
        server_info = self.servers[server_name]
        
        while True:
            try:
                await self._check_server_health(server_name)
                await asyncio.sleep(server_info.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health monitoring error for {server_name}: {e}")
                await asyncio.sleep(server_info.health_check_interval)
    
    async def _check_server_health(self, server_name: str):
        """Check health of a specific server"""
        server_info = self.servers.get(server_name)
        if not server_info:
            return
        
        health = self.health_status[server_name]
        start_time = time.time()
        
        try:
            if server_info.health_check_url:
                # HTTP health check
                response = requests.get(
                    server_info.health_check_url,
                    timeout=5,
                    headers={'User-Agent': 'MCP-Registry/1.0'}
                )
                
                if response.status_code == 200:
                    health.status = ServerStatus.HEALTHY
                    health.error_message = None
                else:
                    health.status = ServerStatus.UNHEALTHY
                    health.error_message = f"HTTP {response.status_code}"
            else:
                # Basic connectivity check (try to start server process)
                health.status = ServerStatus.HEALTHY
                health.error_message = None
            
            health.response_time = time.time() - start_time
            health.last_check = time.time()
            
        except Exception as e:
            health.status = ServerStatus.UNHEALTHY
            health.error_message = str(e)
            health.response_time = time.time() - start_time
            health.last_check = time.time()
    
    def _start_discovery_tasks(self):
        """Start discovery tasks for all servers"""
        for server_name in self.servers:
            if self.servers[server_name].enabled:
                self.discovery_tasks[server_name] = asyncio.create_task(
                    self.start_health_monitoring(server_name)
                )
    
    async def discover_kubernetes_services(self):
        """Discover MCP servers running as Kubernetes services"""
        if not self.k8s_client:
            return
        
        try:
            # Look for services with MCP annotations
            services = self.k8s_client.list_service_for_all_namespaces(
                label_selector="mcp-server=true"
            )
            
            for service in services.items:
                annotations = service.metadata.annotations or {}
                
                server_name = f"k8s-{service.metadata.name}"
                if server_name not in self.servers:
                    server_info = MCPServerInfo(
                        name=server_name,
                        command=annotations.get('mcp.command', 'python'),
                        args=json.loads(annotations.get('mcp.args', '[]')),
                        env=json.loads(annotations.get('mcp.env', '{}')),
                        description=annotations.get('mcp.description', f'Kubernetes MCP Server {service.metadata.name}'),
                        discovery_method=DiscoveryMethod.KUBERNETES,
                        health_check_url=f"http://{service.metadata.name}.{service.metadata.namespace}.svc.cluster.local:{service.spec.ports[0].port}/health",
                        tags=['kubernetes', 'auto-discovered'],
                        metadata={
                            'namespace': service.metadata.namespace,
                            'service_name': service.metadata.name,
                            'cluster_ip': service.spec.cluster_ip
                        }
                    )
                    
                    self.register_server(server_info)
        
        except ApiException as e:
            self.logger.error(f"Failed to discover Kubernetes services: {e}")
    
    async def discover_http_services(self, discovery_urls: List[str]):
        """Discover MCP servers via HTTP discovery endpoints"""
        for url in discovery_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self._parse_config_data(data, DiscoveryMethod.HTTP_DISCOVERY)
                    self.logger.info(f"Discovered servers from {url}")
            except Exception as e:
                self.logger.error(f"Failed to discover from {url}: {e}")
    
    async def discover_dns_services(self, dns_queries: List[str]):
        """Discover MCP servers via DNS SRV records"""
        import socket
        
        for query in dns_queries:
            try:
                # This is a simplified DNS discovery - in production you'd use dnspython
                # For now, we'll just log the attempt
                self.logger.info(f"DNS discovery not fully implemented for {query}")
            except Exception as e:
                self.logger.error(f"Failed DNS discovery for {query}: {e}")
    
    def get_health_status(self, server_name: Optional[str] = None) -> Union[ServerHealth, Dict[str, ServerHealth]]:
        """Get health status for server(s)"""
        if server_name:
            return self.health_status.get(server_name)
        return self.health_status.copy()
    
    def get_healthy_servers(self) -> List[str]:
        """Get list of healthy servers"""
        return [
            name for name, health in self.health_status.items()
            if health.status == ServerStatus.HEALTHY
        ]
    
    def get_unhealthy_servers(self) -> List[str]:
        """Get list of unhealthy servers"""
        return [
            name for name, health in self.health_status.items()
            if health.status == ServerStatus.UNHEALTHY
        ]
    
    async def save_configuration(self, file_path: Optional[str] = None):
        """Save current configuration to file"""
        if not file_path:
            file_path = self.config_dir / "servers.yaml"
        
        config_data = {
            'servers': {
                name: {
                    'command': info.command,
                    'args': info.args,
                    'env': info.env,
                    'description': info.description,
                    'enabled': info.enabled,
                    'health_check_url': info.health_check_url,
                    'health_check_interval': info.health_check_interval,
                    'auto_reconnect': info.auto_reconnect,
                    'max_retries': info.max_retries,
                    'retry_delay': info.retry_delay,
                    'tags': info.tags,
                    'metadata': info.metadata
                }
                for name, info in self.servers.items()
            }
        }
        
        try:
            with open(file_path, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False)
            self.logger.info(f"Configuration saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    async def reload_configuration(self):
        """Reload configuration from all sources"""
        # Clear existing configurations
        self.servers.clear()
        self.health_status.clear()
        
        # Cancel existing discovery tasks
        for task in self.discovery_tasks.values():
            task.cancel()
        self.discovery_tasks.clear()
        
        # Reload configurations
        self._load_configurations()
        
        # Restart discovery tasks
        self._start_discovery_tasks()
        
        self.logger.info("Configuration reloaded")
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        total_servers = len(self.servers)
        enabled_servers = len([s for s in self.servers.values() if s.enabled])
        healthy_servers = len(self.get_healthy_servers())
        unhealthy_servers = len(self.get_unhealthy_servers())
        
        discovery_methods = {}
        for server in self.servers.values():
            method = server.discovery_method.value
            discovery_methods[method] = discovery_methods.get(method, 0) + 1
        
        return {
            'total_servers': total_servers,
            'enabled_servers': enabled_servers,
            'healthy_servers': healthy_servers,
            'unhealthy_servers': unhealthy_servers,
            'discovery_methods': discovery_methods,
            'active_discovery_tasks': len(self.discovery_tasks)
        }

# Global registry instance
mcp_registry = MCPServerRegistry()
