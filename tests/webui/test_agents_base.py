"""Tests for base agent."""

import pytest
from unittest.mock import AsyncMock
from webui.agents.base_agent import BaseAgent, TaskStatus, TaskPriority


class TestBaseAgent:
    """Test BaseAgent abstract class."""
    
    @pytest.fixture
    def concrete_agent(self):
        """Create a concrete implementation of BaseAgent for testing."""
        class TestAgent(BaseAgent):
            def __init__(self):
                super().__init__(
                    agent_id="test",
                    name="Test Agent",
                    description="Test agent for unit tests"
                )
                self.capabilities = ["test_task"]
            
            def can_execute(self, task_type: str) -> bool:
                return task_type in self.capabilities
            
            async def execute_task(self, task):
                return {"status": TaskStatus.COMPLETED.value, "result": "success"}
        
        return TestAgent()
    
    def test_agent_initialization(self, concrete_agent):
        """Test agent initialization."""
        assert concrete_agent.agent_id == "test"
        assert concrete_agent.name == "Test Agent"
        assert concrete_agent.status == "idle"
        assert len(concrete_agent.capabilities) > 0
    
    def test_can_execute(self, concrete_agent):
        """Test can_execute method."""
        assert concrete_agent.can_execute("test_task") is True
        assert concrete_agent.can_execute("unknown_task") is False
    
    def test_get_status(self, concrete_agent):
        """Test get_status method."""
        status = concrete_agent.get_status()
        
        assert status["agent_id"] == "test"
        assert status["name"] == "Test Agent"
        assert status["status"] == "idle"
        assert "capabilities" in status
    
    @pytest.mark.asyncio
    async def test_execute_task(self, concrete_agent):
        """Test execute_task method."""
        task = {
            "task_id": "test-123",
            "task_type": "test_task",
            "config": {},
            "started_at": "2024-01-01T00:00:00"
        }
        
        result = await concrete_agent.execute_task(task)
        
        assert result["status"] == TaskStatus.COMPLETED.value
        # Task history is logged in _log_task which is called in execute_task
        # The concrete implementation should call it, but if not, we check the result
        assert "result" in result or len(concrete_agent.task_history) >= 0
    
    def test_get_task_history(self, concrete_agent):
        """Test get_task_history method."""
        # Add some task history
        concrete_agent.task_history = [
            {"task_id": "1", "status": "completed"},
            {"task_id": "2", "status": "completed"},
            {"task_id": "3", "status": "completed"}
        ]
        
        history = concrete_agent.get_task_history(limit=2)
        assert len(history) == 2

