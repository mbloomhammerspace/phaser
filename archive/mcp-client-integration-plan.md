# MCP Client Integration for RAG Playground

## 🎯 **Focused Scope**
Add MCP client capabilities to the existing RAG playground to enable future integration with MCP servers (HammerSpace and Kubernetes) when they're ready.

## 🏗️ **MCP Client Architecture**

### **Current RAG Playground Structure**
```
┌─────────────────────────────────────┐
│           RAG Playground            │
│  ┌─────────────┐  ┌─────────────┐   │
│  │   Flask     │  │   Milvus    │   │
│  │   Server    │  │   Client    │   │
│  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────┘
```

### **Enhanced with MCP Client**
```
┌─────────────────────────────────────────────────────┐
│                RAG Playground                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Flask     │  │   Milvus    │  │   MCP       │  │
│  │   Server    │  │   Client    │  │   Client    │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
        ┌───────────▼──┐  ┌─────▼─────┐  ┌──▼──────────┐
        │ HammerSpace  │  │ Milvus    │  │ Kubernetes  │
        │ MCP Server   │  │ Vector DB │  │ MCP Server  │
        │ (Future)     │  │ (Current) │  │ (Future)    │
        └──────────────┘  └───────────┘  └─────────────┘
```

## 🛠️ **Implementation Plan**

### **Phase 1: MCP Client Foundation (2-3 days)**

#### 1.1 MCP Client Library Integration
- [ ] Add MCP client dependencies to RAG playground
- [ ] Create MCP client manager class
- [ ] Implement connection management
- [ ] Add error handling and retry logic

#### 1.2 Basic MCP Client Interface
- [ ] Create MCP client configuration
- [ ] Implement server discovery
- [ ] Add connection status monitoring
- [ ] Create basic MCP operation framework

### **Phase 2: UI Integration (1-2 days)**

#### 2.1 MCP Client UI Components
- [ ] Add MCP client status panel
- [ ] Create server connection interface
- [ ] Add MCP operation buttons
- [ ] Implement connection status indicators

#### 2.2 Enhanced Playground Interface
- [ ] Integrate MCP client into existing UI
- [ ] Add MCP operation results display
- [ ] Create MCP configuration panel
- [ ] Add MCP operation history

### **Phase 3: Testing & Validation (1 day)**

#### 3.1 MCP Client Testing
- [ ] Test MCP client connection logic
- [ ] Validate error handling
- [ ] Test UI integration
- [ ] Verify configuration management

## 📋 **Technical Implementation**

### **MCP Client Dependencies**
```python
# requirements.txt additions
mcp>=1.0.0
websockets>=11.0.0
asyncio-mqtt>=0.13.0
```

### **MCP Client Manager**
```python
# mcp_client.py
import asyncio
import json
from typing import Dict, List, Optional, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClientManager:
    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.connected_servers: List[str] = []
        self.server_configs: Dict[str, Dict] = {}
    
    async def connect_to_server(self, server_name: str, config: Dict) -> bool:
        """Connect to an MCP server"""
        try:
            # Create server parameters
            server_params = StdioServerParameters(
                command=config.get('command'),
                args=config.get('args', []),
                env=config.get('env', {})
            )
            
            # Establish connection
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize session
                    await session.initialize()
                    
                    # Store session
                    self.sessions[server_name] = session
                    self.connected_servers.append(server_name)
                    self.server_configs[server_name] = config
                    
                    return True
        except Exception as e:
            print(f"Failed to connect to {server_name}: {e}")
            return False
    
    async def disconnect_server(self, server_name: str) -> bool:
        """Disconnect from an MCP server"""
        if server_name in self.sessions:
            try:
                await self.sessions[server_name].close()
                del self.sessions[server_name]
                self.connected_servers.remove(server_name)
                return True
            except Exception as e:
                print(f"Failed to disconnect from {server_name}: {e}")
                return False
        return False
    
    async def list_tools(self, server_name: str) -> List[Dict]:
        """List available tools from an MCP server"""
        if server_name not in self.sessions:
            return []
        
        try:
            session = self.sessions[server_name]
            tools = await session.list_tools()
            return tools.tools
        except Exception as e:
            print(f"Failed to list tools from {server_name}: {e}")
            return []
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict) -> Any:
        """Call a tool on an MCP server"""
        if server_name not in self.sessions:
            raise Exception(f"Server {server_name} not connected")
        
        try:
            session = self.sessions[server_name]
            result = await session.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            print(f"Failed to call tool {tool_name} on {server_name}: {e}")
            raise
    
    def get_connection_status(self) -> Dict[str, bool]:
        """Get connection status for all servers"""
        return {
            server: server in self.sessions 
            for server in self.server_configs.keys()
        }
```

### **Enhanced RAG Playground with MCP Client**
```python
# Enhanced playground.py with MCP client integration
from flask import Flask, request, jsonify, render_template_string
import json
from pymilvus import connections, Collection
import numpy as np
import requests
import asyncio
from mcp_client import MCPClientManager

app = Flask(__name__)

# Initialize MCP client manager
mcp_manager = MCPClientManager()

# MCP server configurations (for future use)
MCP_SERVERS = {
    "hammerspace": {
        "command": "python",
        "args": ["-m", "hammerspace_mcp_server"],
        "env": {},
        "description": "HammerSpace MCP Server for tagging and objectives"
    },
    "kubernetes": {
        "command": "k8s-mcp-server",
        "args": [],
        "env": {"KUBECONFIG": "/path/to/kubeconfig"},
        "description": "Kubernetes MCP Server for job management"
    }
}

@app.route('/mcp/status')
def mcp_status():
    """Get MCP client status"""
    try:
        status = mcp_manager.get_connection_status()
        return jsonify({
            "status": "success",
            "connected_servers": mcp_manager.connected_servers,
            "server_status": status,
            "available_servers": list(MCP_SERVERS.keys())
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/connect', methods=['POST'])
def mcp_connect():
    """Connect to an MCP server"""
    try:
        data = request.get_json()
        server_name = data.get('server_name')
        
        if server_name not in MCP_SERVERS:
            return jsonify({"error": f"Unknown server: {server_name}"}), 400
        
        config = MCP_SERVERS[server_name]
        
        # Run async connection in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(
            mcp_manager.connect_to_server(server_name, config)
        )
        loop.close()
        
        if success:
            return jsonify({
                "status": "success",
                "message": f"Connected to {server_name}",
                "server": server_name
            })
        else:
            return jsonify({"error": f"Failed to connect to {server_name}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/disconnect', methods=['POST'])
def mcp_disconnect():
    """Disconnect from an MCP server"""
    try:
        data = request.get_json()
        server_name = data.get('server_name')
        
        # Run async disconnection in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(
            mcp_manager.disconnect_server(server_name)
        )
        loop.close()
        
        if success:
            return jsonify({
                "status": "success",
                "message": f"Disconnected from {server_name}",
                "server": server_name
            })
        else:
            return jsonify({"error": f"Failed to disconnect from {server_name}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/tools/<server_name>')
def mcp_tools(server_name):
    """List tools available on an MCP server"""
    try:
        if server_name not in mcp_manager.sessions:
            return jsonify({"error": f"Server {server_name} not connected"}), 400
        
        # Run async tool listing in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tools = loop.run_until_complete(
            mcp_manager.list_tools(server_name)
        )
        loop.close()
        
        return jsonify({
            "status": "success",
            "server": server_name,
            "tools": tools
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/call', methods=['POST'])
def mcp_call():
    """Call a tool on an MCP server"""
    try:
        data = request.get_json()
        server_name = data.get('server_name')
        tool_name = data.get('tool_name')
        arguments = data.get('arguments', {})
        
        if server_name not in mcp_manager.sessions:
            return jsonify({"error": f"Server {server_name} not connected"}), 400
        
        # Run async tool call in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            mcp_manager.call_tool(server_name, tool_name, arguments)
        )
        loop.close()
        
        return jsonify({
            "status": "success",
            "server": server_name,
            "tool": tool_name,
            "result": result
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### **Enhanced UI with MCP Client Panel**
```html
<!-- MCP Client Panel HTML -->
<div class="mcp-panel">
    <h3>🔌 MCP Client</h3>
    <div class="mcp-status" id="mcp-status">
        <div class="status-indicator">●</div>
        <span>Checking MCP status...</span>
    </div>
    
    <div class="mcp-servers">
        <h4>Available Servers</h4>
        <div id="mcp-servers-list">
            <!-- Server list will be populated here -->
        </div>
    </div>
    
    <div class="mcp-actions">
        <button onclick="refreshMCPStatus()">Refresh Status</button>
        <button onclick="showMCPConfig()">Configure Servers</button>
    </div>
</div>

<style>
.mcp-panel {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 20px;
    margin: 20px 0;
}

.mcp-status {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
}

.status-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 10px;
    background-color: #dc3545; /* Red for disconnected */
}

.status-indicator.connected {
    background-color: #28a745; /* Green for connected */
}

.mcp-servers {
    margin-bottom: 15px;
}

.server-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    margin: 5px 0;
    background: white;
    border-radius: 4px;
    border: 1px solid #e9ecef;
}

.server-actions button {
    margin-left: 5px;
    padding: 5px 10px;
    border: none;
    border-radius: 3px;
    cursor: pointer;
}

.connect-btn {
    background: #007bff;
    color: white;
}

.disconnect-btn {
    background: #dc3545;
    color: white;
}
</style>

<script>
// MCP Client JavaScript functions
async function refreshMCPStatus() {
    try {
        const response = await fetch('/mcp/status');
        const data = await response.json();
        updateMCPStatus(data);
    } catch (e) {
        console.error('Failed to refresh MCP status:', e);
    }
}

function updateMCPStatus(data) {
    const statusDiv = document.getElementById('mcp-status');
    const indicator = statusDiv.querySelector('.status-indicator');
    const text = statusDiv.querySelector('span');
    
    if (data.connected_servers.length > 0) {
        indicator.classList.add('connected');
        text.textContent = `Connected to ${data.connected_servers.join(', ')}`;
    } else {
        indicator.classList.remove('connected');
        text.textContent = 'No MCP servers connected';
    }
    
    updateServerList(data);
}

function updateServerList(data) {
    const serversList = document.getElementById('mcp-servers-list');
    serversList.innerHTML = '';
    
    data.available_servers.forEach(server => {
        const isConnected = data.server_status[server];
        const serverDiv = document.createElement('div');
        serverDiv.className = 'server-item';
        serverDiv.innerHTML = `
            <div>
                <strong>${server}</strong>
                <span style="color: ${isConnected ? 'green' : 'red'};">
                    ${isConnected ? 'Connected' : 'Disconnected'}
                </span>
            </div>
            <div class="server-actions">
                ${isConnected ? 
                    `<button class="disconnect-btn" onclick="disconnectServer('${server}')">Disconnect</button>` :
                    `<button class="connect-btn" onclick="connectServer('${server}')">Connect</button>`
                }
            </div>
        `;
        serversList.appendChild(serverDiv);
    });
}

async function connectServer(serverName) {
    try {
        const response = await fetch('/mcp/connect', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({server_name: serverName})
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            refreshMCPStatus();
        } else {
            alert(`Failed to connect: ${data.error}`);
        }
    } catch (e) {
        alert(`Connection error: ${e.message}`);
    }
}

async function disconnectServer(serverName) {
    try {
        const response = await fetch('/mcp/disconnect', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({server_name: serverName})
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            refreshMCPStatus();
        } else {
            alert(`Failed to disconnect: ${data.error}`);
        }
    } catch (e) {
        alert(`Disconnection error: ${e.message}`);
    }
}

// Initialize MCP status on page load
document.addEventListener('DOMContentLoaded', function() {
    refreshMCPStatus();
});
</script>
```

## 📊 **Effort Estimation**

### **Development Time**
- **Phase 1 (MCP Client Foundation)**: 2-3 days
- **Phase 2 (UI Integration)**: 1-2 days  
- **Phase 3 (Testing & Validation)**: 1 day
- **Total**: 4-6 days

### **Key Benefits**
- **Future-Ready**: Prepared for MCP server integration
- **Modular Design**: Clean separation of concerns
- **Extensible**: Easy to add new MCP servers
- **User-Friendly**: Intuitive UI for MCP management

### **Dependencies**
- MCP client libraries
- Async/await support in Flask
- WebSocket support for real-time updates
- Configuration management

## 🚀 **Next Steps**

1. **Implement MCP Client Manager** (Day 1-2)
2. **Add MCP Client to RAG Playground** (Day 2-3)
3. **Create MCP Client UI** (Day 3-4)
4. **Test and Validate** (Day 4-5)
5. **Documentation and Deployment** (Day 5-6)

This focused approach will give you a solid MCP client foundation in your RAG playground, ready for future MCP server integration when your dedicated system is set up.
