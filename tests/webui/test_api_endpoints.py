"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from webui.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestAPIEndpoints:
    """Test API endpoints."""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
    
    @patch('cli.validators.system.SystemValidator')
    def test_validate_preflight(self, mock_validator, client):
        """Test preflight validation endpoint."""
        mock_validator_instance = MagicMock()
        mock_validator_instance.validate_all.return_value = [
            {"name": "Python", "status": "pass", "message": "Python 3.8+"}
        ]
        mock_validator.return_value = mock_validator_instance
        
        response = client.post("/api/validate/preflight", json={})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "results" in data
    
    @patch('cli.utils.secrets.SecretManager')
    def test_set_api_key(self, mock_secret_manager, client):
        """Test setting API key endpoint."""
        mock_manager = MagicMock()
        mock_secret_manager.return_value = mock_manager
        
        response = client.post(
            "/api/keys/set",
            json={
                "key_type": "nvidia",
                "key_value": "nvapi-test-key",
                "test": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    @patch('cli.utils.secrets.SecretManager')
    def test_list_api_keys(self, mock_secret_manager, client):
        """Test listing API keys endpoint."""
        mock_manager = MagicMock()
        mock_manager.get_key.side_effect = lambda k: "test-key" if k == "nvidia" else None
        mock_secret_manager.return_value = mock_manager
        
        response = client.get("/api/keys/list")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "keys" in data
    
    @patch('cli.utils.config.ConfigManager')
    def test_get_config(self, mock_config_manager, client):
        """Test getting configuration endpoint."""
        mock_manager = MagicMock()
        mock_manager.load.return_value = {"blueprint_version": "v2.2.1"}
        mock_config_manager.return_value = mock_manager
        
        response = client.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "config" in data
    
    @patch('cli.utils.config.ConfigManager')
    def test_save_config(self, mock_config_manager, client):
        """Test saving configuration endpoint."""
        mock_manager = MagicMock()
        mock_manager.validate.return_value = []
        mock_config_manager.return_value = mock_manager
        
        response = client.post(
            "/api/config",
            json={"blueprint_version": "v2.2.1", "nodes": []}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    @patch('webui.api.main.agent_manager')
    def test_get_agents(self, mock_agent_manager, client):
        """Test getting agents endpoint."""
        mock_agent_manager.get_agents.return_value = [
            {"agent_id": "installation", "name": "Installation Agent"}
        ]
        
        response = client.get("/api/agents")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "agents" in data
    
    @patch('webui.api.main.agent_manager')
    @pytest.mark.asyncio
    async def test_submit_task(self, mock_agent_manager, client):
        """Test submitting a task endpoint."""
        mock_agent_manager.submit_task = AsyncMock(return_value={
            "task_id": "test-123",
            "status": "completed",
            "result": {}
        })
        
        response = client.post(
            "/api/agents/tasks",
            json={
                "task_type": "install_kubernetes",
                "config": {},
                "priority": "medium"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "task" in data
    
    @patch('webui.api.main.agent_manager')
    def test_get_task_status(self, mock_agent_manager, client):
        """Test getting task status endpoint."""
        mock_agent_manager.get_task_status.return_value = {
            "task_id": "test-123",
            "status": "completed"
        }
        
        response = client.get("/api/agents/tasks/test-123")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "task" in data
    
    @patch('webui.api.main.agent_manager')
    def test_get_tasks(self, mock_agent_manager, client):
        """Test getting tasks endpoint."""
        mock_agent_manager.get_task_history.return_value = [
            {"task_id": "test-1", "status": "completed"}
        ]
        
        response = client.get("/api/agents/tasks")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "tasks" in data

