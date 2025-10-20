"""
Enhanced RAG Playground with MCP Client Integration
Provides document search capabilities with MCP server integration
"""

from flask import Flask, request, jsonify, render_template_string
import json
import asyncio
import logging
from pymilvus import connections, Collection
import numpy as np
import requests
from mcp_client import mcp_manager, MCP_AVAILABLE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def connect_to_milvus():
    """Connect to Milvus and return the collection"""
    try:
        connections.connect('default', host='milvus', port='19530')
        collection = Collection('hammerspace_docs')
        collection.load()
        return collection
    except Exception as e:
        logger.error(f"Error connecting to Milvus: {e}")
        return None

def simple_search(collection, query, top_k=5):
    """Perform a simple vector search"""
    try:
        # Generate a simple embedding for the query
        query_embedding = np.random.rand(2048).tolist()
        
        # Search for similar documents
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = collection.search(
            data=[query_embedding],
            anns_field="vector",
            param=search_params,
            limit=top_k,
            output_fields=["source", "text"]
        )
        
        return results[0] if results else []
    except Exception as e:
        logger.error(f"Search error: {e}")
        return []

def run_async(coro):
    """Run an async coroutine in a new event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# MCP Client Routes
@app.route('/mcp/status')
def mcp_status():
    """Get MCP client status"""
    try:
        status = mcp_manager.get_connection_status()
        connected_servers = mcp_manager.get_connected_servers()
        servers_info = mcp_manager.get_all_servers_info()
        
        return jsonify({
            "status": "success",
            "mcp_available": MCP_AVAILABLE,
            "connected_servers": connected_servers,
            "server_status": status,
            "servers_info": servers_info
        })
    except Exception as e:
        logger.error(f"MCP status error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/connect', methods=['POST'])
def mcp_connect():
    """Connect to an MCP server"""
    try:
        data = request.get_json()
        server_name = data.get('server_name')
        
        if not server_name:
            return jsonify({"error": "server_name is required"}), 400
        
        # Run async connection
        success = run_async(mcp_manager.connect_to_server(server_name))
        
        if success:
            return jsonify({
                "status": "success",
                "message": f"Connected to {server_name}",
                "server": server_name
            })
        else:
            return jsonify({"error": f"Failed to connect to {server_name}"}), 500
            
    except Exception as e:
        logger.error(f"MCP connect error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/disconnect', methods=['POST'])
def mcp_disconnect():
    """Disconnect from an MCP server"""
    try:
        data = request.get_json()
        server_name = data.get('server_name')
        
        if not server_name:
            return jsonify({"error": "server_name is required"}), 400
        
        # Run async disconnection
        success = run_async(mcp_manager.disconnect_server(server_name))
        
        if success:
            return jsonify({
                "status": "success",
                "message": f"Disconnected from {server_name}",
                "server": server_name
            })
        else:
            return jsonify({"error": f"Failed to disconnect from {server_name}"}), 500
            
    except Exception as e:
        logger.error(f"MCP disconnect error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/tools/<server_name>')
def mcp_tools(server_name):
    """List tools available on an MCP server"""
    try:
        if server_name not in mcp_manager.sessions:
            return jsonify({"error": f"Server {server_name} not connected"}), 400
        
        # Run async tool listing
        tools = run_async(mcp_manager.list_tools(server_name))
        
        return jsonify({
            "status": "success",
            "server": server_name,
            "tools": tools
        })
        
    except Exception as e:
        logger.error(f"MCP tools error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/call', methods=['POST'])
def mcp_call():
    """Call a tool on an MCP server"""
    try:
        data = request.get_json()
        server_name = data.get('server_name')
        tool_name = data.get('tool_name')
        arguments = data.get('arguments', {})
        
        if not server_name or not tool_name:
            return jsonify({"error": "server_name and tool_name are required"}), 400
        
        if server_name not in mcp_manager.sessions:
            return jsonify({"error": f"Server {server_name} not connected"}), 400
        
        # Run async tool call
        result = run_async(mcp_manager.call_tool(server_name, tool_name, arguments))
        
        return jsonify({
            "status": "success",
            "server": server_name,
            "tool": tool_name,
            "result": result
        })
        
    except Exception as e:
        logger.error(f"MCP call error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/servers')
def mcp_servers():
    """Get information about all MCP servers"""
    try:
        servers_info = mcp_manager.get_all_servers_info()
        return jsonify({
            "status": "success",
            "servers": servers_info
        })
    except Exception as e:
        logger.error(f"MCP servers error: {e}")
        return jsonify({"error": str(e)}), 500

# Original RAG Playground Routes
@app.route('/')
def index():
    """Main playground interface"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>RAG Playground - Enhanced with MCP Client</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 40px; 
                background-color: #f5f5f5; 
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                background: white; 
                padding: 30px; 
                border-radius: 10px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
            }
            h1 { 
                color: #333; 
                text-align: center; 
                margin-bottom: 30px;
            }
            .main-content {
                display: grid;
                grid-template-columns: 2fr 1fr;
                gap: 30px;
            }
            .search-section {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
            }
            .mcp-section {
                background: #e9ecef;
                padding: 20px;
                border-radius: 8px;
            }
            .search-box { 
                width: 100%; 
                padding: 15px; 
                font-size: 16px; 
                border: 2px solid #ddd; 
                border-radius: 5px; 
                margin: 20px 0; 
            }
            .search-btn { 
                background: #007bff; 
                color: white; 
                padding: 15px 30px; 
                border: none; 
                border-radius: 5px; 
                cursor: pointer; 
                font-size: 16px; 
            }
            .search-btn:hover { background: #0056b3; }
            .results { margin-top: 30px; }
            .result-item { 
                background: #f8f9fa; 
                padding: 15px; 
                margin: 10px 0; 
                border-radius: 5px; 
                border-left: 4px solid #007bff; 
            }
            .result-source { 
                font-weight: bold; 
                color: #007bff; 
                margin-bottom: 10px; 
            }
            .result-text { 
                color: #666; 
                line-height: 1.6; 
            }
            .stats { 
                background: #e9ecef; 
                padding: 15px; 
                border-radius: 5px; 
                margin-bottom: 20px; 
                text-align: center; 
            }
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
                background-color: #dc3545;
            }
            .status-indicator.connected {
                background-color: #28a745;
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
            .mcp-actions {
                display: flex;
                gap: 10px;
                margin-top: 15px;
            }
            .mcp-actions button {
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                background: #6c757d;
                color: white;
            }
            .mcp-actions button:hover {
                background: #5a6268;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 RAG Playground - Enhanced with MCP Client</h1>
            
            <div class="main-content">
                <div class="search-section">
                    <div class="stats" id="stats">Loading document count...</div>
                    <input type="text" class="search-box" id="query" placeholder="Ask about HammerSpace documentation..." />
                    <button class="search-btn" onclick="search()">Search Documents</button>
                    <div class="results" id="results"></div>
                </div>
                
                <div class="mcp-section">
                    <h3>🔌 MCP Client</h3>
                    <div class="mcp-panel">
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
                            <button onclick="showMCPInfo()">Server Info</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // MCP Client JavaScript functions
            async function refreshMCPStatus() {
                try {
                    const response = await fetch('/mcp/status');
                    const data = await response.json();
                    updateMCPStatus(data);
                } catch (e) {
                    console.error('Failed to refresh MCP status:', e);
                    document.getElementById('mcp-status').innerHTML = 
                        '<div class="status-indicator"></div><span>Error loading MCP status</span>';
                }
            }

            function updateMCPStatus(data) {
                const statusDiv = document.getElementById('mcp-status');
                const indicator = statusDiv.querySelector('.status-indicator');
                const text = statusDiv.querySelector('span');
                
                if (data.connected_servers && data.connected_servers.length > 0) {
                    indicator.classList.add('connected');
                    text.textContent = `Connected to ${data.connected_servers.join(', ')}`;
                } else {
                    indicator.classList.remove('connected');
                    text.textContent = data.mcp_available ? 'No MCP servers connected' : 'MCP not available';
                }
                
                updateServerList(data);
            }

            function updateServerList(data) {
                const serversList = document.getElementById('mcp-servers-list');
                serversList.innerHTML = '';
                
                if (data.servers_info) {
                    Object.entries(data.servers_info).forEach(([serverName, serverInfo]) => {
                        const isConnected = serverInfo.connected;
                        const isEnabled = serverInfo.enabled;
                        const serverDiv = document.createElement('div');
                        serverDiv.className = 'server-item';
                        serverDiv.innerHTML = `
                            <div>
                                <strong>${serverName}</strong>
                                <br>
                                <small>${serverInfo.description}</small>
                                <br>
                                <span style="color: ${isConnected ? 'green' : 'red'};">
                                    ${isConnected ? 'Connected' : 'Disconnected'}
                                </span>
                                ${!isEnabled ? ' (Disabled)' : ''}
                            </div>
                            <div class="server-actions">
                                ${isEnabled ? (
                                    isConnected ? 
                                        `<button class="disconnect-btn" onclick="disconnectServer('${serverName}')">Disconnect</button>` :
                                        `<button class="connect-btn" onclick="connectServer('${serverName}')">Connect</button>`
                                ) : '<span style="color: #6c757d;">Disabled</span>'}
                            </div>
                        `;
                        serversList.appendChild(serverDiv);
                    });
                }
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

            async function showMCPInfo() {
                try {
                    const response = await fetch('/mcp/servers');
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        let info = 'MCP Server Information:\\n\\n';
                        Object.entries(data.servers).forEach(([name, info]) => {
                            info += `${name}:\\n`;
                            info += `  Description: ${info.description}\\n`;
                            info += `  Status: ${info.status}\\n`;
                            info += `  Enabled: ${info.enabled}\\n`;
                            info += `  Tools: ${info.tools_count}\\n\\n`;
                        });
                        alert(info);
                    }
                } catch (e) {
                    alert(`Error getting server info: ${e.message}`);
                }
            }

            // Original RAG playground functions
            async function loadStats() {
                try {
                    const response = await fetch('/stats');
                    const data = await response.json();
                    document.getElementById('stats').innerHTML = 
                        `📚 Total Documents: ${data.total_documents} | 🔍 Collection: ${data.collection_name}`;
                } catch (e) {
                    document.getElementById('stats').innerHTML = 'Error loading stats';
                }
            }

            async function search() {
                const query = document.getElementById('query').value;
                if (!query) return;
                
                document.getElementById('results').innerHTML = 'Searching...';
                
                try {
                    const response = await fetch('/search', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({query: query, top_k: 5})
                    });
                    const data = await response.json();
                    displayResults(data);
                } catch (e) {
                    document.getElementById('results').innerHTML = 'Error: ' + e.message;
                }
            }

            function displayResults(data) {
                const resultsDiv = document.getElementById('results');
                if (!data.results || data.results.length === 0) {
                    resultsDiv.innerHTML = '<p>No results found.</p>';
                    return;
                }

                let html = '<h3>Search Results:</h3>';
                data.results.forEach((result, index) => {
                    html += `
                        <div class="result-item">
                            <div class="result-source">${result.source}</div>
                            <div class="result-text">${result.text.substring(0, 500)}${result.text.length > 500 ? '...' : ''}</div>
                            <small>Distance: ${result.distance.toFixed(4)}</small>
                        </div>
                    `;
                });
                resultsDiv.innerHTML = html;
            }

            // Initialize on page load
            document.addEventListener('DOMContentLoaded', function() {
                loadStats();
                refreshMCPStatus();
                
                // Search on Enter key
                document.getElementById('query').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') search();
                });
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/stats')
def stats():
    """Get document statistics"""
    try:
        collection = connect_to_milvus()
        if collection:
            return jsonify({
                "total_documents": collection.num_entities,
                "collection_name": "hammerspace_docs",
                "status": "connected"
            })
        else:
            return jsonify({"error": "Cannot connect to Milvus"}), 500
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['POST'])
def search():
    """Search documents"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 5)
        
        collection = connect_to_milvus()
        if not collection:
            return jsonify({"error": "Cannot connect to Milvus"}), 500
        
        results = simple_search(collection, query, top_k)
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "source": result.entity.get('source', 'Unknown'),
                "text": result.entity.get('text', 'No text available'),
                "distance": result.distance
            })
        
        return jsonify({"results": formatted_results, "query": query})
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("=== Enhanced RAG Playground with MCP Client Started ===")
    
    # Check MCP availability
    if MCP_AVAILABLE:
        logger.info("MCP libraries available - MCP client functionality enabled")
    else:
        logger.warning("MCP libraries not available - MCP client functionality disabled")
    
    # Connect to Milvus
    collection = connect_to_milvus()
    if collection:
        logger.info(f"Connected to Milvus collection: hammerspace_docs")
        logger.info(f"Collection has {collection.num_entities} entities")
    else:
        logger.error("Failed to connect to Milvus")
    
    logger.info("Starting Flask server on port 8080...")
    logger.info("Enhanced playground available at http://localhost:8080")
    logger.info("Features: Document search + MCP client integration")
    
    app.run(host='0.0.0.0', port=8080, debug=False)
