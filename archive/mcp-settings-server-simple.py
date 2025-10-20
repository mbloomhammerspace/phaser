from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import requests
import json
import os
import logging
import time
from pymilvus import connections, Collection
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Enhanced RAG Server with MCP Integration",
    description="NVIDIA RAG Blueprint server enhanced with MCP client capabilities",
    version="2.2.0-mcp"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
MILVUS_HOST = os.getenv('MILVUS_HOST', 'milvus-external-etcd-clean')
MILVUS_PORT = int(os.getenv('MILVUS_PORT', '19530'))
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'hammerspace_docs')
MILVUS_MCP_URL = os.getenv('MILVUS_MCP_URL', 'http://milvus-mcp-wrapper-service:8000')

# MCP Settings - Global state
MCP_GLOBAL_ENABLED = True
MCP_AUTO_CONNECT = True

# Pydantic models
class HealthResponse(BaseModel):
    message: str = "Service is up."
    databases: List[Dict] = []
    object_storage: List[Dict] = []
    nim: List[Dict] = []
    mcp_status: Dict = {}

class DatabaseHealthInfo(BaseModel):
    service: str
    url: str
    status: str
    collections: Optional[int] = None
    error: Optional[str] = None

class DocumentSearch(BaseModel):
    query: str = "Tell me something interesting"
    collection_names: List[str] = ["hammerspace_docs"]
    vdb_top_k: int = 100
    reranker_top_k: int = 10
    confidence_score_threshold: float = 0.0

class ChainResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    model: str
    processing_time: float
    timestamp: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    collection_names: List[str] = ["hammerspace_docs"]
    use_knowledge_base: bool = True
    temperature: float = 0.5
    top_p: float = 0.9
    max_tokens: int = 1000

# Milvus connection function
def connect_to_milvus():
    try:
        connections.connect(
            alias="default",
            host=MILVUS_HOST,
            port=MILVUS_PORT
        )
        collection = Collection(COLLECTION_NAME)
        collection.load()
        return collection
    except Exception as e:
        logger.error(f"Error connecting to Milvus: {e}")
        return None

# MCP Settings Endpoints
@app.get("/mcp/settings")
def get_mcp_settings():
    """Get current MCP settings for the frontend"""
    return {
        "mcp_global_enabled": MCP_GLOBAL_ENABLED,
        "mcp_auto_connect": MCP_AUTO_CONNECT,
        "mcp_available": True
    }

@app.post("/mcp/settings")
def update_mcp_settings(settings: Dict[str, Any]):
    """Update MCP settings from the frontend"""
    global MCP_GLOBAL_ENABLED, MCP_AUTO_CONNECT
    
    try:
        if 'mcp_global_enabled' in settings:
            MCP_GLOBAL_ENABLED = bool(settings['mcp_global_enabled'])
            logger.info(f"MCP Global Enabled: {MCP_GLOBAL_ENABLED}")
        
        if 'mcp_auto_connect' in settings:
            MCP_AUTO_CONNECT = bool(settings['mcp_auto_connect'])
            logger.info(f"MCP Auto-connect: {MCP_AUTO_CONNECT}")
        
        return {
            "message": "MCP settings updated successfully",
            "mcp_global_enabled": MCP_GLOBAL_ENABLED,
            "mcp_auto_connect": MCP_AUTO_CONNECT
        }
        
    except Exception as e:
        logger.error(f"Error updating MCP settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mcp/disable")
def disable_mcp():
    """Disable all MCP services"""
    global MCP_GLOBAL_ENABLED
    MCP_GLOBAL_ENABLED = False
    logger.info("MCP services disabled via API")
    return {
        "message": "All MCP services have been disabled",
        "mcp_global_enabled": MCP_GLOBAL_ENABLED
    }

@app.post("/mcp/enable")
def enable_mcp():
    """Enable all MCP services"""
    global MCP_GLOBAL_ENABLED
    MCP_GLOBAL_ENABLED = True
    logger.info("MCP services enabled via API")
    return {
        "message": "All MCP services have been enabled",
        "mcp_global_enabled": MCP_GLOBAL_ENABLED
    }

# Enhanced health endpoint with MCP settings
@app.get("/health", response_model=HealthResponse)
async def health_check(check_dependencies: bool = False):
    """Perform a Health Check with MCP settings"""
    db_health = []
    
    # Check Milvus direct connection
    milvus_direct_status = "disconnected"
    milvus_direct_error = None
    milvus_direct_collections = None
    try:
        collection = connect_to_milvus()
        if collection:
            milvus_direct_status = "connected"
            milvus_direct_collections = collection.num_entities
    except Exception as e:
        milvus_direct_error = str(e)
    db_health.append(DatabaseHealthInfo(
        service="milvus_direct",
        url=f"grpc://{MILVUS_HOST}:{MILVUS_PORT}",
        status=milvus_direct_status,
        collections=milvus_direct_collections,
        error=milvus_direct_error
    ))

    # Check Milvus MCP Wrapper connection
    mcp_wrapper_status = "disconnected"
    mcp_wrapper_error = None
    try:
        response = requests.get(f"{MILVUS_MCP_URL}/health", timeout=5)
        if response.status_code == 200:
            mcp_wrapper_status = "connected"
        else:
            mcp_wrapper_error = f"HTTP Status: {response.status_code}"
    except Exception as e:
        mcp_wrapper_error = str(e)
    db_health.append(DatabaseHealthInfo(
        service="milvus_mcp_wrapper",
        url=MILVUS_MCP_URL,
        status=mcp_wrapper_status,
        error=mcp_wrapper_error
    ))

    # Add MCP settings to the health response
    mcp_status = {
        "mcp_global_enabled": MCP_GLOBAL_ENABLED,
        "mcp_auto_connect": MCP_AUTO_CONNECT,
        "mcp_available": True
    }

    return HealthResponse(
        message="Enhanced RAG Server with MCP integration is up.",
        databases=db_health,
        mcp_status=mcp_status
    )

# Root endpoint
@app.get("/")
def root():
    """Root endpoint with service information"""
    return {
        "service": "Enhanced RAG Server with MCP Integration",
        "version": "2.2.0-mcp",
        "endpoints": {
            "health": "/health",
            "search": "/search",
            "generate": "/generate",
            "chat_completions": "/chat/completions",
            "mcp_status": "/mcp/status",
            "mcp_collections": "/mcp/collections",
            "mcp_settings": "/mcp/settings"
        }
    }

# Simple search endpoint
@app.post("/search")
async def search_documents(search: DocumentSearch):
    """Search documents in the vector database"""
    if not MCP_GLOBAL_ENABLED:
        return {"message": "MCP services are disabled", "results": []}
    
    try:
        collection = connect_to_milvus()
        if not collection:
            raise HTTPException(status_code=500, detail="Cannot connect to Milvus")
        
        # Perform vector search
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = collection.search(
            data=[np.random.rand(768)],  # Dummy vector for now
            anns_field="vector",
            param=search_params,
            limit=search.reranker_top_k,
            output_fields=["text", "source"]
        )
        
        return {"results": results, "query": search.query}
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Simple generate endpoint
@app.post("/generate")
async def generate_response(request: ChatRequest):
    """Generate a response using the knowledge base"""
    if not MCP_GLOBAL_ENABLED:
        return {
            "choices": [{
                "message": {
                    "content": "MCP services are currently disabled. Please enable MCP services to use this feature."
                }
            }]
        }
    
    try:
        # Simple response for now
        user_message = request.messages[-1].content if request.messages else "Hello"
        
        return {
            "choices": [{
                "message": {
                    "content": f"Enhanced RAG response for: {user_message} (MCP Enabled)"
                }
            }]
        }
        
    except Exception as e:
        logger.error(f"Generate error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat completions endpoint
@app.post("/chat/completions")
async def chat_completions(request: ChatRequest):
    """Chat completions endpoint"""
    return await generate_response(request)

if __name__ == "__main__":
    print("=== Enhanced RAG Server with MCP Integration ===")
    print("🚀 Starting FastAPI server on port 8081...")
    print("🔌 MCP Settings available at /mcp/settings")
    print("🌐 Health check with MCP status at /health")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
