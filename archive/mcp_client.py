"""
MCP Client Manager for RAG Playground
Provides MCP client functionality for connecting to MCP servers
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

# MCP imports (will be installed via requirements.txt)
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("MCP libraries not available. Install with: pip install mcp")

class ConnectionStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    name: str
    command: str
    args: List[str]
    env: Dict[str, str]
    description: str
    enabled: bool = True

class MCPClientManager:
    """
    Manages connections to MCP servers and provides a unified interface
    for interacting with them.
    """
    
    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.server_configs: Dict[str, MCPServerConfig] = {}
        self.connection_status: Dict[str, ConnectionStatus] = {}
        self.server_tools: Dict[str, List[Dict]] = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize with default server configurations
        self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """Initialize default MCP server configurations"""
        default_configs = [
            MCPServerConfig(
                name="hammerspace",
                command="python",
                args=["-m", "hammerspace_mcp_server"],
                env={},
                description="HammerSpace MCP Server for tagging and objectives",
                enabled=False  # Disabled until server is available
            ),
            MCPServerConfig(
                name="kubernetes",
                command="k8s-mcp-server",
                args=[],
                env={"KUBECONFIG": "/var/run/secrets/kubernetes.io/serviceaccount"},
                description="Kubernetes MCP Server for job management",
                enabled=False  # Disabled until server is available
            )
        ]
        
        for config in default_configs:
            self.server_configs[config.name] = config
            self.connection_status[config.name] = ConnectionStatus.DISCONNECTED
    
    async def connect_to_server(self, server_name: str) -> bool:
        """
        Connect to an MCP server
        
        Args:
            server_name: Name of the server to connect to
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not MCP_AVAILABLE:
            self.logger.error("MCP libraries not available")
            return False
            
        if server_name not in self.server_configs:
            self.logger.error(f"Unknown server: {server_name}")
            return False
        
        config = self.server_configs[server_name]
        if not config.enabled:
            self.logger.warning(f"Server {server_name} is disabled")
            return False
        
        self.connection_status[server_name] = ConnectionStatus.CONNECTING
        
        try:
            # Create server parameters
            server_params = StdioServerParameters(
                command=config.command,
                args=config.args,
                env=config.env
            )
            
            # Establish connection
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize session
                    await session.initialize()
                    
                    # Store session
                    self.sessions[server_name] = session
                    self.connection_status[server_name] = ConnectionStatus.CONNECTED
                    
                    # Load available tools
                    await self._load_server_tools(server_name)
                    
                    self.logger.info(f"Successfully connected to {server_name}")
                    return True
                    
        except Exception as e:
            self.logger.error(f"Failed to connect to {server_name}: {e}")
            self.connection_status[server_name] = ConnectionStatus.ERROR
            return False
    
    async def disconnect_server(self, server_name: str) -> bool:
        """
        Disconnect from an MCP server
        
        Args:
            server_name: Name of the server to disconnect from
            
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        if server_name not in self.sessions:
            self.logger.warning(f"Server {server_name} not connected")
            return False
        
        try:
            await self.sessions[server_name].close()
            del self.sessions[server_name]
            self.connection_status[server_name] = ConnectionStatus.DISCONNECTED
            
            # Clear tools cache
            if server_name in self.server_tools:
                del self.server_tools[server_name]
            
            self.logger.info(f"Successfully disconnected from {server_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to disconnect from {server_name}: {e}")
            return False
    
    async def _load_server_tools(self, server_name: str):
        """Load available tools from an MCP server"""
        try:
            session = self.sessions[server_name]
            tools_response = await session.list_tools()
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
        if server_name not in self.sessions:
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
        Call a tool on an MCP server
        
        Args:
            server_name: Name of the server
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Tool execution result
        """
        if server_name not in self.sessions:
            raise Exception(f"Server {server_name} not connected")
        
        try:
            session = self.sessions[server_name]
            result = await session.call_tool(tool_name, arguments)
            self.logger.info(f"Successfully called tool {tool_name} on {server_name}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to call tool {tool_name} on {server_name}: {e}")
            raise
    
    def get_connection_status(self) -> Dict[str, str]:
        """
        Get connection status for all servers
        
        Returns:
            Dictionary mapping server names to their connection status
        """
        return {
            server: status.value 
            for server, status in self.connection_status.items()
        }
    
    def get_connected_servers(self) -> List[str]:
        """
        Get list of connected servers
        
        Returns:
            List of connected server names
        """
        return [
            server for server, status in self.connection_status.items()
            if status == ConnectionStatus.CONNECTED
        ]
    
    def get_server_info(self, server_name: str) -> Optional[Dict]:
        """
        Get information about a server
        
        Args:
            server_name: Name of the server
            
        Returns:
            Server information dictionary or None if not found
        """
        if server_name not in self.server_configs:
            return None
        
        config = self.server_configs[server_name]
        return {
            "name": config.name,
            "description": config.description,
            "enabled": config.enabled,
            "status": self.connection_status.get(server_name, ConnectionStatus.DISCONNECTED).value,
            "connected": server_name in self.sessions,
            "tools_count": len(self.server_tools.get(server_name, []))
        }
    
    def get_all_servers_info(self) -> Dict[str, Dict]:
        """
        Get information about all servers
        
        Returns:
            Dictionary mapping server names to their information
        """
        return {
            server: self.get_server_info(server)
            for server in self.server_configs.keys()
        }
    
    def add_server_config(self, config: MCPServerConfig):
        """
        Add a new server configuration
        
        Args:
            config: Server configuration to add
        """
        self.server_configs[config.name] = config
        self.connection_status[config.name] = ConnectionStatus.DISCONNECTED
        self.logger.info(f"Added server configuration: {config.name}")
    
    def remove_server_config(self, server_name: str) -> bool:
        """
        Remove a server configuration
        
        Args:
            server_name: Name of the server to remove
            
        Returns:
            True if removed successfully, False otherwise
        """
        if server_name not in self.server_configs:
            return False
        
        # Disconnect if connected
        if server_name in self.sessions:
            asyncio.create_task(self.disconnect_server(server_name))
        
        # Remove configuration
        del self.server_configs[server_name]
        del self.connection_status[server_name]
        
        if server_name in self.server_tools:
            del self.server_tools[server_name]
        
        self.logger.info(f"Removed server configuration: {server_name}")
        return True
    
    def enable_server(self, server_name: str) -> bool:
        """
        Enable a server configuration
        
        Args:
            server_name: Name of the server to enable
            
        Returns:
            True if enabled successfully, False otherwise
        """
        if server_name not in self.server_configs:
            return False
        
        self.server_configs[server_name].enabled = True
        self.logger.info(f"Enabled server: {server_name}")
        return True
    
    def disable_server(self, server_name: str) -> bool:
        """
        Disable a server configuration
        
        Args:
            server_name: Name of the server to disable
            
        Returns:
            True if disabled successfully, False otherwise
        """
        if server_name not in self.server_configs:
            return False
        
        # Disconnect if connected
        if server_name in self.sessions:
            asyncio.create_task(self.disconnect_server(server_name))
        
        self.server_configs[server_name].enabled = False
        self.logger.info(f"Disabled server: {server_name}")
        return True

# Global MCP client manager instance
mcp_manager = MCPClientManager()
