import asyncio
import subprocess
import json
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Milvus MCP Wrapper")

class MCPRequest(BaseModel):
    method: str
    params: dict = {}

class MCPResponse(BaseModel):
    result: dict = {}
    error: str = None

async def call_mcp_server(method: str, params: dict = {}):
    """Call the Milvus MCP server via stdio"""
    try:
        # Create MCP request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        # Start the MCP server process
        process = await asyncio.create_subprocess_exec(
            "uv", "run", "src/mcp_server_milvus/server.py", 
            "--milvus-uri", "http://milvus-external-etcd-clean:19530",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="/app/mcp-server-milvus"
        )
        
        # Send the request
        request_json = json.dumps(request) + "\n"
        stdout, stderr = await process.communicate(input=request_json.encode())
        
        if process.returncode == 0:
            response = json.loads(stdout.decode())
            return response.get("result", {})
        else:
            logger.error(f"MCP server error: {stderr.decode()}")
            return {"error": stderr.decode()}
            
    except Exception as e:
        logger.error(f"Error calling MCP server: {e}")
        return {"error": str(e)}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "milvus-mcp-wrapper"}

@app.get("/mcp/tools")
async def get_tools():
    """Get available MCP tools"""
    result = await call_mcp_server("tools/list")
    return result

@app.get("/mcp/collections")
async def get_collections():
    """Get Milvus collections"""
    result = await call_mcp_server("milvus/list_collections")
    return result

@app.post("/mcp/search")
async def search_vectors(request: dict):
    """Search vectors in Milvus"""
    result = await call_mcp_server("milvus/search", request)
    return result

@app.get("/")
async def root():
    return {
        "service": "Milvus MCP Wrapper",
        "endpoints": [
            "/health",
            "/mcp/tools", 
            "/mcp/collections",
            "/mcp/search"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
