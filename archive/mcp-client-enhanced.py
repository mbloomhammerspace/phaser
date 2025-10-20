"""
Enhanced MCP Client with Registry Integration
Provides advanced MCP client functionality with server registry, auto-registration, and service discovery
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

# MCP imports
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("MCP libraries not available. Install with: pip install mcp")

from mcp_registry import (
    MCPServerRegistry, MCPServerInfo, ServerStatus, DiscoveryMethod,
    mcp_registry
)

class ConnectionStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RECONNECTING = "reconnecting"

@dataclass
class ConnectionInfo:
    """Information about an active connection"""
    server_name: str
    session: Optional[ClientSession]
    connected_at: float
    last_activity: float
    retry_count: int = 0
    status: ConnectionStatus = ConnectionStatus.DISCONNECTED

class EnhancedMCPClientManager:
    """
    Enhanced MCP client manager with registry integration, auto-reconnection, and service discovery
    """
    
    def __init__(self, registry: Optional[MCPServerRegistry] = None):
        self.registry = registry or mcp_registry
        self.connections: Dict[str, ConnectionInfo] = {}
        self.server_tools: Dict[str, List[Dict]] = {}
        self.connection_callbacks: List[callable] = []
        self.logger = logging.getLogger(__name__)
        
        # Auto-reconnection settings
        self.auto_reconnect_enabled = True
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 5
        
        # Start background tasks
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        # Start auto-reconnection task
        asyncio.create_task(self._auto_reconnect_task())
        
        # Start health monitoring task
        asyncio.create_task(self._health_monitoring_task())
        
        # Start service discovery task
        asyncio.create_task(self._service_discovery_task())
    
    async def _auto_reconnect_task(self):
        """Background task for auto-reconnection"""
        while True:
            try:
                if self.auto_reconnect_enabled:
                    await self._check_and_reconnect()
                await asyncio.sleep(10)  # Check every 10 seconds
            except Exception as e:
                self.logger.error(f"Auto-reconnect task error: {e}")
                await asyncio.sleep(30)
    
    async def _health_monitoring_task(self):
        """Background task for health monitoring"""
        while True:
            try:
                await self._monitor_connections()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                self.logger.error(f"Health monitoring task error: {e}")
                await asyncio.sleep(60)
    
    async def _service_discovery_task(self):
        """Background task for service discovery"""
        while True:
            try:
                await self._discover_new_services()
                await asyncio.sleep(300)  # Discover every 5 minutes
            except Exception as e:
                self.logger.error(f"Service discovery task error: {e}")
                await asyncio.sleep(600)
    
    async def _check_and_reconnect(self):
        """Check for disconnected servers and attempt reconnection"""
        for server_name, connection in self.connections.items():
            if connection.status in [ConnectionStatus.DISCONNECTED, ConnectionStatus.ERROR]:
                server_info = self.registry.get_server(server_name)
                if server_info and server_info.auto_reconnect and server_info.enabled:
                    if connection.retry_count < self.max_reconnect_attempts:
                        self.logger.info(f"Attempting to reconnect to {server_name}")
                        await self.connect_to_server(server_name)
                    else:
                        self.logger.warning(f"Max reconnection attempts reached for {server_name}")
    
    async def _monitor_connections(self):
        """Monitor active connections and update health status"""
        for server_name, connection in self.connections.items():
            if connection.status == ConnectionStatus.CONNECTED:
                try:
                    # Simple health check - try to list tools
                    if connection.session:
                        await connection.session.list_tools()
                        connection.last_activity = time.time()
                except Exception as e:
                    self.logger.warning(f"Health check failed for {server_name}: {e}")
                    connection.status = ConnectionStatus.ERROR
                    await self._notify_connection_change(server_name, ConnectionStatus.ERROR)
    
    async def _discover_new_services(self):
        """Discover new MCP services"""
        try:
            # Discover Kubernetes services
            await self.registry.discover_kubernetes_services()
            
            # Discover HTTP services (if configured)
            discovery_urls = [
                "http://mcp-discovery.default.svc.cluster.local/discover",
                "http://mcp-registry.default.svc.cluster.local/servers"
            ]
            await self.registry.discover_http_services(discovery_urls)
            
        except Exception as e:
            self.logger.error(f"Service discovery error: {e}")
    
    async def connect_to_server(self, server_name: str) -> bool:
        """
        Connect to an MCP server with enhanced error handling and retry logic
        
        Args:
            server_name: Name of the server to connect to
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not MCP_AVAILABLE:
            self.logger.error("MCP libraries not available")
            return False
        
        server_info = self.registry.get_server(server_name)
        if not server_info:
            self.logger.error(f"Server {server_name} not found in registry")
            return False
        
        if not server_info.enabled:
            self.logger.warning(f"Server {server_name} is disabled")
            return False
        
        # Update connection status
        if server_name in self.connections:
            self.connections[server_name].status = ConnectionStatus.CONNECTING
        else:
            self.connections[server_name] = ConnectionInfo(
                server_name=server_name,
                session=None,
                connected_at=0,
                last_activity=0,
                status=ConnectionStatus.CONNECTING
            )
        
        try:
            # Create server parameters
            server_params = StdioServerParameters(
                command=server_info.command,
                args=server_info.args,
                env=server_info.env
            )
            
            # Establish connection
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize session
                    await session.initialize()
                    
                    # Store connection info
                    connection = self.connections[server_name]
                    connection.session = session
                    connection.status = ConnectionStatus.CONNECTED
                    connection.connected_at = time.time()
                    connection.last_activity = time.time()
                    connection.retry_count = 0
                    
                    # Load available tools
                    await self._load_server_tools(server_name)
                    
                    # Notify connection change
                    await self._notify_connection_change(server_name, ConnectionStatus.CONNECTED)
                    
                    self.logger.info(f"Successfully connected to {server_name}")
                    return True
                    
        except Exception as e:
            self.logger.error(f"Failed to connect to {server_name}: {e}")
            
            # Update connection status
            if server_name in self.connections:
                self.connections[server_name].status = ConnectionStatus.ERROR
                self.connections[server_name].retry_count += 1
                await self._notify_connection_change(server_name, ConnectionStatus.ERROR)
            
            return False
    
    async def disconnect_server(self, server_name: str) -> bool:
        """
        Disconnect from an MCP server
        
        Args:
            server_name: Name of the server to disconnect from
            
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        if server_name not in self.connections:
            self.logger.warning(f"Server {server_name} not connected")
            return False
        
        try:
            connection = self.connections[server_name]
            if connection.session:
                await connection.session.close()
            
            connection.status = ConnectionStatus.DISCONNECTED
            connection.session = None
            
            # Clear tools cache
            if server_name in self.server_tools:
                del self.server_tools[server_name]
            
            # Notify connection change
            await self._notify_connection_change(server_name, ConnectionStatus.DISCONNECTED)
            
            self.logger.info(f"Successfully disconnected from {server_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to disconnect from {server_name}: {e}")
            return False
    
    async def _load_server_tools(self, server_name: str):
        """Load available tools from an MCP server"""
        try:
            connection = self.connections.get(server_name)
            if not connection or not connection.session:
                return
            
            tools_response = await connection.session.list_tools()
            self.server_tools[server_name] = tools_response.tools
            self.logger.info(f"Loaded {len(tools_response.tools)} tools from {server_name}")
        except Exception as e:
            self.logger.error(f"Failed to load tools from {server_name}: {e}")
            self.server_tools[server_name] = []
    
    async def list_tools(self, server_name: str) -> List[Dict]:
        """
        List available tools from an MCP server
        
        Args:
            server_name: Name of the server
            
        Returns:
            List of available tools
        """
        if server_name not in self.connections:
            self.logger.error(f"Server {server_name} not connected")
            return []
        
        # Return cached tools if available
        if server_name in self.server_tools:
            return self.server_tools[server_name]
        
        # Load tools if not cached
        await self._load_server_tools(server_name)
        return self.server_tools.get(server_name, [])
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict) -> Any:
        """
        Call a tool on an MCP server with retry logic
        
        Args:
            server_name: Name of the server
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Tool execution result
        """
        if server_name not in self.connections:
            raise Exception(f"Server {server_name} not connected")
        
        connection = self.connections[server_name]
        if not connection.session:
            raise Exception(f"Server {server_name} session not available")
        
        try:
            result = await connection.session.call_tool(tool_name, arguments)
            connection.last_activity = time.time()
            self.logger.info(f"Successfully called tool {tool_name} on {server_name}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to call tool {tool_name} on {server_name}: {e}")
            # Mark connection as potentially unhealthy
            connection.status = ConnectionStatus.ERROR
            raise
    
    def get_connection_status(self) -> Dict[str, str]:
        """
        Get connection status for all servers
        
        Returns:
            Dictionary mapping server names to their connection status
        """
        return {
            server_name: connection.status.value
            for server_name, connection in self.connections.items()
        }
    
    def get_connected_servers(self) -> List[str]:
        """
        Get list of connected servers
        
        Returns:
            List of connected server names
        """
        return [
            server_name for server_name, connection in self.connections.items()
            if connection.status == ConnectionStatus.CONNECTED
        ]
    
    def get_server_info(self, server_name: str) -> Optional[Dict]:
        """
        Get comprehensive information about a server
        
        Args:
            server_name: Name of the server
            
        Returns:
            Server information dictionary or None if not found
        """
        server_info = self.registry.get_server(server_name)
        if not server_info:
            return None
        
        connection = self.connections.get(server_name)
        health = self.registry.get_health_status(server_name)
        
        return {
            "name": server_info.name,
            "description": server_info.description,
            "enabled": server_info.enabled,
            "discovery_method": server_info.discovery_method.value,
            "status": connection.status.value if connection else ConnectionStatus.DISCONNECTED.value,
            "connected": connection and connection.status == ConnectionStatus.CONNECTED,
            "tools_count": len(self.server_tools.get(server_name, [])),
            "health_status": health.status.value if health else ServerStatus.UNKNOWN.value,
            "last_activity": connection.last_activity if connection else 0,
            "retry_count": connection.retry_count if connection else 0,
            "tags": server_info.tags,
            "metadata": server_info.metadata
        }
    
    def get_all_servers_info(self) -> Dict[str, Dict]:
        """
        Get information about all servers (registered and connected)
        
        Returns:
            Dictionary mapping server names to their information
        """
        all_servers = {}
        
        # Add registered servers
        for server_name in self.registry.list_servers():
            all_servers[server_name] = self.get_server_info(server_name)
        
        # Add connected servers that might not be in registry
        for server_name in self.connections:
            if server_name not in all_servers:
                all_servers[server_name] = self.get_server_info(server_name)
        
        return all_servers
    
    def add_connection_callback(self, callback: callable):
        """
        Add a callback function to be called when connection status changes
        
        Args:
            callback: Function to call with (server_name, status) parameters
        """
        self.connection_callbacks.append(callback)
    
    async def _notify_connection_change(self, server_name: str, status: ConnectionStatus):
        """Notify all callbacks of connection status change"""
        for callback in self.connection_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(server_name, status)
                else:
                    callback(server_name, status)
            except Exception as e:
                self.logger.error(f"Connection callback error: {e}")
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the MCP client and registry"""
        client_stats = {
            "total_connections": len(self.connections),
            "connected_servers": len(self.get_connected_servers()),
            "disconnected_servers": len([c for c in self.connections.values() if c.status == ConnectionStatus.DISCONNECTED]),
            "error_servers": len([c for c in self.connections.values() if c.status == ConnectionStatus.ERROR]),
            "total_tools": sum(len(tools) for tools in self.server_tools.values()),
            "auto_reconnect_enabled": self.auto_reconnect_enabled
        }
        
        registry_stats = self.registry.get_registry_stats()
        
        return {
            "client": client_stats,
            "registry": registry_stats,
            "mcp_available": MCP_AVAILABLE
        }
    
    async def discover_and_connect_servers(self, tags: Optional[List[str]] = None) -> List[str]:
        """
        Discover and automatically connect to servers
        
        Args:
            tags: Optional list of tags to filter servers
            
        Returns:
            List of successfully connected server names
        """
        connected_servers = []
        
        # Get servers to connect to
        if tags:
            servers = self.registry.get_servers_by_tag(tags[0])  # Use first tag for now
        else:
            servers = list(self.registry.list_servers(enabled_only=True).values())
        
        # Attempt to connect to each server
        for server_info in servers:
            if server_info.enabled and server_info.name not in self.get_connected_servers():
                success = await self.connect_to_server(server_info.name)
                if success:
                    connected_servers.append(server_info.name)
        
        return connected_servers
    
    async def shutdown(self):
        """Gracefully shutdown the MCP client manager"""
        self.logger.info("Shutting down MCP client manager...")
        
        # Disconnect all servers
        for server_name in list(self.connections.keys()):
            await self.disconnect_server(server_name)
        
        # Cancel background tasks
        tasks = [task for task in asyncio.all_tasks() if not task.done()]
        for task in tasks:
            task.cancel()
        
        self.logger.info("MCP client manager shutdown complete")

# Global enhanced MCP client manager instance
enhanced_mcp_manager = EnhancedMCPClientManager()
