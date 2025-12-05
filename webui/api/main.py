"""
FastAPI backend for NVIDIA RAG Blueprint Web UI.
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import asyncio
from pathlib import Path
import sys

# Add parent directory to path to import CLI modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.validators.system import SystemValidator
from cli.validators.api_keys import APIKeyValidator
from cli.utils.config import ConfigManager
from cli.utils.secrets import SecretManager
from cli.wizard.installer import InstallationWizard
from webui.agents.agent_manager import AgentManager, TaskPriority

# Initialize agent manager
agent_manager = AgentManager()

app = FastAPI(
    title="NVIDIA RAG Blueprint Installer",
    description="Web UI for installing and managing NVIDIA RAG Blueprint",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


# Pydantic models
class APIKeyRequest(BaseModel):
    key_type: str
    key_value: str
    test: bool = True


class NodeConfig(BaseModel):
    hostname: str
    ip: str
    username: str
    is_master: bool
    has_gpu: bool


class InstallationConfig(BaseModel):
    blueprint_version: str = "v2.2.1"
    nodes: List[NodeConfig]
    gpu_count: int = 1
    memory_limit: str = "16Gi"
    dry_run: bool = False


class ValidationRequest(BaseModel):
    inventory_file: Optional[str] = None


# API Routes

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web UI."""
    template_path = Path(__file__).parent.parent / "templates" / "index.html"
    if template_path.exists():
        return FileResponse(template_path)
    return HTMLResponse("<h1>NVIDIA RAG Blueprint Installer</h1><p>Web UI is being set up...</p>")


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


# Validation endpoints

@app.post("/api/validate/preflight")
async def validate_preflight(request: ValidationRequest):
    """Run pre-installation validation."""
    try:
        validator = SystemValidator()
        results = validator.validate_all()
        
        return {
            "status": "success",
            "results": results,
            "summary": {
                "total": len(results),
                "passed": sum(1 for r in results if r["status"] == "pass"),
                "failed": sum(1 for r in results if r["status"] == "fail"),
                "warnings": sum(1 for r in results if r["status"] == "warn")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/validate/system")
async def validate_system():
    """Get system validation results."""
    try:
        validator = SystemValidator()
        results = validator.validate_all()
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# API Key endpoints

@app.post("/api/keys/set")
async def set_api_key(request: APIKeyRequest):
    """Set an API key."""
    try:
        if request.key_type not in ["nvidia", "openai", "anthropic"]:
            raise HTTPException(status_code=400, detail="Invalid key type")
        
        # Validate format
        validator = APIKeyValidator()
        if not validator.validate_format(request.key_type, request.key_value):
            raise HTTPException(status_code=400, detail="Invalid API key format")
        
        # Test key if requested
        if request.test:
            if not validator.test_key(request.key_type, request.key_value):
                raise HTTPException(status_code=400, detail="API key test failed")
        
        # Store key
        secret_manager = SecretManager()
        secret_manager.set_key(request.key_type, request.key_value)
        
        return {"status": "success", "message": f"{request.key_type} API key stored successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/keys/list")
async def list_api_keys():
    """List configured API keys."""
    try:
        secret_manager = SecretManager()
        keys = {}
        for key_type in ["nvidia", "openai", "anthropic"]:
            key_value = secret_manager.get_key(key_type)
            keys[key_type] = {
                "configured": key_value is not None,
                "required": key_type == "nvidia"
            }
        return {"status": "success", "keys": keys}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/keys/test")
async def test_api_key(request: APIKeyRequest):
    """Test an API key."""
    try:
        validator = APIKeyValidator()
        secret_manager = SecretManager()
        
        key_value = request.key_value or secret_manager.get_key(request.key_type)
        if not key_value:
            raise HTTPException(status_code=400, detail="API key not found")
        
        is_valid = validator.test_key(request.key_type, key_value)
        return {
            "status": "success",
            "valid": is_valid,
            "message": "API key test passed" if is_valid else "API key test failed"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/keys/{key_type}")
async def remove_api_key(key_type: str):
    """Remove an API key."""
    try:
        if key_type not in ["nvidia", "openai", "anthropic"]:
            raise HTTPException(status_code=400, detail="Invalid key type")
        
        secret_manager = SecretManager()
        secret_manager.remove_key(key_type)
        
        return {"status": "success", "message": f"{key_type} API key removed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Configuration endpoints

@app.get("/api/config")
async def get_config():
    """Get current configuration."""
    try:
        config_manager = ConfigManager()
        config = config_manager.load()
        return {"status": "success", "config": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config")
async def save_config(config: Dict[str, Any]):
    """Save configuration."""
    try:
        config_manager = ConfigManager()
        errors = config_manager.validate(config)
        
        if errors:
            return {
                "status": "error",
                "errors": errors,
                "message": "Configuration validation failed"
            }
        
        config_manager.save(config)
        return {"status": "success", "message": "Configuration saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/config/template")
async def get_config_template():
    """Get configuration template."""
    try:
        config_manager = ConfigManager()
        template = config_manager.default_config.copy()
        return {"status": "success", "template": template}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config/validate")
async def validate_config(config: Dict[str, Any]):
    """Validate configuration."""
    try:
        config_manager = ConfigManager()
        errors = config_manager.validate(config)
        
        return {
            "status": "success" if not errors else "error",
            "errors": errors,
            "valid": len(errors) == 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Installation endpoints

@app.post("/api/install/validate")
async def validate_installation(config: InstallationConfig):
    """Validate installation configuration."""
    try:
        # Convert to dict for validation
        config_dict = config.dict()
        config_manager = ConfigManager()
        errors = config_manager.validate(config_dict)
        
        return {
            "status": "success" if not errors else "error",
            "errors": errors,
            "valid": len(errors) == 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/install/start")
async def start_installation(config: InstallationConfig):
    """Start installation (returns immediately, use WebSocket for progress)."""
    try:
        # This will be handled via WebSocket for real-time updates
        return {
            "status": "started",
            "message": "Installation started. Connect to WebSocket for progress updates.",
            "installation_id": "install_123"  # In real implementation, generate unique ID
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket for real-time updates

class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back or process message
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.websocket("/ws/install")
async def websocket_install(websocket: WebSocket):
    """WebSocket for installation progress."""
    await manager.connect(websocket)
    try:
        # Send initial connection message
        await manager.send_personal_message(
            json.dumps({"type": "connected", "message": "Connected to installation stream"}),
            websocket
        )
        
        # Simulate installation progress (in real implementation, this would come from Ansible)
        steps = [
            {"step": 1, "name": "Validating prerequisites", "status": "running"},
            {"step": 2, "name": "Configuring nodes", "status": "pending"},
            {"step": 3, "name": "Deploying Kubernetes", "status": "pending"},
            {"step": 4, "name": "Installing GPU Operator", "status": "pending"},
            {"step": 5, "name": "Deploying RAG Blueprint", "status": "pending"},
            {"step": 6, "name": "Verifying installation", "status": "pending"},
        ]
        
        for step in steps:
            await asyncio.sleep(2)  # Simulate delay
            step["status"] = "completed"
            await manager.send_personal_message(
                json.dumps({
                    "type": "progress",
                    "step": step["step"],
                    "name": step["name"],
                    "status": step["status"],
                    "progress": int((step["step"] / len(steps)) * 100)
                }),
                websocket
            )
        
        await manager.send_personal_message(
            json.dumps({"type": "complete", "message": "Installation completed successfully"}),
            websocket
        )
        
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        await manager.send_personal_message(
            json.dumps({"type": "error", "message": str(e)}),
            websocket
        )


# Agent endpoints

@app.get("/api/agents")
async def get_agents():
    """Get list of all agents."""
    try:
        agents = agent_manager.get_agents()
        return {"status": "success", "agents": agents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get specific agent details."""
    try:
        agent = agent_manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return {"status": "success", "agent": agent.get_status()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/capabilities")
async def get_agent_capabilities():
    """Get capabilities of all agents."""
    try:
        capabilities = agent_manager.get_agent_capabilities()
        return {"status": "success", "capabilities": capabilities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/tasks")
async def submit_task(request: Dict[str, Any]):
    """Submit a task to an agent."""
    try:
        task_type = request.get("task_type")
        config = request.get("config", {})
        priority_str = request.get("priority", "medium")
        agent_id = request.get("agent_id")
        
        # Convert priority string to enum
        priority_map = {
            "low": TaskPriority.LOW,
            "medium": TaskPriority.MEDIUM,
            "high": TaskPriority.HIGH,
            "critical": TaskPriority.CRITICAL
        }
        priority = priority_map.get(priority_str.lower(), TaskPriority.MEDIUM)
        
        result = await agent_manager.submit_task(
            task_type=task_type,
            config=config,
            priority=priority,
            agent_id=agent_id
        )
        
        return {"status": "success", "task": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a task."""
    try:
        task = agent_manager.get_task_status(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"status": "success", "task": task}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/tasks")
async def get_tasks(
    status: Optional[str] = None,
    limit: int = 20
):
    """Get task history."""
    try:
        if status == "running":
            tasks = agent_manager.get_running_tasks()
        else:
            tasks = agent_manager.get_task_history(limit=limit)
        
        return {"status": "success", "tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/agents/tasks/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a running task."""
    try:
        success = agent_manager.cancel_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found or not running")
        return {"status": "success", "message": "Task cancelled"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/agents/tasks/{task_id}")
async def websocket_task_progress(websocket: WebSocket, task_id: str):
    """WebSocket for task progress updates."""
    await manager.connect(websocket)
    try:
        # Send initial connection message
        await manager.send_personal_message(
            json.dumps({"type": "connected", "task_id": task_id}),
            websocket
        )
        
        # Poll for task updates
        while True:
            task = agent_manager.get_task_status(task_id)
            if task:
                await manager.send_personal_message(
                    json.dumps({
                        "type": "update",
                        "task": task
                    }),
                    websocket
                )
                
                # If task is completed or failed, stop polling
                if task.get("status") in ["completed", "failed", "cancelled"]:
                    break
            
            await asyncio.sleep(1)  # Poll every second
        
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        await manager.send_personal_message(
            json.dumps({"type": "error", "message": str(e)}),
            websocket
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

