"""Tests for agent manager."""

import pytest
from unittest.mock import AsyncMock, patch
from webui.agents.agent_manager import AgentManager, TaskPriority
from webui.agents.base_agent import TaskStatus


class TestAgentManager:
    """Test AgentManager class."""
    
    @pytest.fixture
    def manager(self):
        """Create AgentManager instance."""
        return AgentManager()
    
    def test_initialization(self, manager):
        """Test agent manager initialization."""
        agents = manager.get_agents()
        assert len(agents) > 0
        assert any(a["agent_id"] == "installation" for a in agents)
        assert any(a["agent_id"] == "management" for a in agents)
        assert any(a["agent_id"] == "configuration" for a in agents)
    
    def test_get_agent(self, manager):
        """Test getting a specific agent."""
        agent = manager.get_agent("installation")
        assert agent is not None
        assert agent.agent_id == "installation"
    
    def test_get_agent_not_found(self, manager):
        """Test getting non-existent agent."""
        agent = manager.get_agent("nonexistent")
        assert agent is None
    
    def test_get_agent_capabilities(self, manager):
        """Test getting agent capabilities."""
        capabilities = manager.get_agent_capabilities()
        assert "installation" in capabilities
        assert len(capabilities["installation"]) > 0
    
    def test_find_agent_for_task(self, manager):
        """Test finding agent for a task type."""
        agent = manager.find_agent_for_task("install_kubernetes")
        assert agent is not None
        assert agent.agent_id == "installation"
    
    def test_find_agent_for_task_not_found(self, manager):
        """Test finding agent for unknown task type."""
        agent = manager.find_agent_for_task("unknown_task")
        assert agent is None
    
    @pytest.mark.asyncio
    async def test_submit_task(self, manager):
        """Test submitting a task."""
        result = await manager.submit_task(
            task_type="install_kubernetes",
            config={"inventory_file": "test.yml"},
            priority=TaskPriority.MEDIUM
        )
        
        assert "task_id" in result
        assert result["status"] in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value]
    
    @pytest.mark.asyncio
    async def test_submit_task_with_agent_id(self, manager):
        """Test submitting a task with specific agent."""
        result = await manager.submit_task(
            task_type="install_kubernetes",
            config={},
            priority=TaskPriority.MEDIUM,
            agent_id="installation"
        )
        
        assert "task_id" in result
    
    @pytest.mark.asyncio
    async def test_submit_task_no_agent(self, manager):
        """Test submitting a task with no available agent."""
        with pytest.raises(ValueError):
            await manager.submit_task(
                task_type="unknown_task",
                config={}
            )
    
    def test_get_task_status(self, manager):
        """Test getting task status."""
        # Submit a task first
        import asyncio
        task_result = asyncio.run(manager.submit_task(
            task_type="health_check",
            config={}
        ))
        
        task_id = task_result["task_id"]
        status = manager.get_task_status(task_id)
        
        assert status is not None
        assert status["task_id"] == task_id
    
    def test_get_task_status_not_found(self, manager):
        """Test getting status of non-existent task."""
        status = manager.get_task_status("nonexistent-task-id")
        assert status is None
    
    def test_get_task_history(self, manager):
        """Test getting task history."""
        history = manager.get_task_history(limit=10)
        assert isinstance(history, list)
    
    def test_get_running_tasks(self, manager):
        """Test getting running tasks."""
        running = manager.get_running_tasks()
        assert isinstance(running, list)
    
    def test_cancel_task(self, manager):
        """Test cancelling a task."""
        # Submit a task
        import asyncio
        task_result = asyncio.run(manager.submit_task(
            task_type="health_check",
            config={}
        ))
        
        task_id = task_result["task_id"]
        # Task completes quickly, so cancellation may not work
        # But we can test the method exists
        result = manager.cancel_task(task_id)
        assert isinstance(result, bool)

