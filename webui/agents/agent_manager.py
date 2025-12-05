"""
Agent manager for coordinating multiple agents.
"""

import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import deque

from webui.agents.base_agent import BaseAgent, TaskStatus, TaskPriority
from webui.agents.installation_agent import InstallationAgent
from webui.agents.management_agent import ManagementAgent
from webui.agents.configuration_agent import ConfigurationAgent


class AgentManager:
    """Manages multiple agents and task execution."""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: deque = deque()
        self.running_tasks: Dict[str, Dict[str, Any]] = {}
        self.completed_tasks: List[Dict[str, Any]] = []
        
        # Initialize agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all available agents."""
        agents = [
            InstallationAgent(),
            ManagementAgent(),
            ConfigurationAgent()
        ]
        
        for agent in agents:
            self.agents[agent.agent_id] = agent
    
    def get_agents(self) -> List[Dict[str, Any]]:
        """Get list of all agents with their status."""
        return [agent.get_status() for agent in self.agents.values()]
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get a specific agent."""
        return self.agents.get(agent_id)
    
    def get_agent_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all agents."""
        return {
            agent_id: agent.capabilities
            for agent_id, agent in self.agents.items()
        }
    
    def find_agent_for_task(self, task_type: str) -> Optional[BaseAgent]:
        """Find an agent that can execute a task type."""
        for agent in self.agents.values():
            if agent.can_execute(task_type):
                return agent
        return None
    
    async def submit_task(
        self,
        task_type: str,
        config: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit a task for execution."""
        # Find agent if not specified
        if agent_id:
            agent = self.agents.get(agent_id)
        else:
            agent = self.find_agent_for_task(task_type)
        
        if not agent:
            raise ValueError(f"No agent available for task type: {task_type}")
        
        # Create task
        task_id = str(uuid.uuid4())
        task = {
            "task_id": task_id,
            "task_type": task_type,
            "config": config,
            "priority": priority.value,
            "agent_id": agent.agent_id,
            "status": TaskStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None
        }
        
        # Add to queue
        self.task_queue.append(task)
        
        # Execute task
        task["started_at"] = datetime.now().isoformat()
        task["status"] = TaskStatus.RUNNING.value
        self.running_tasks[task_id] = task
        
        try:
            result = await agent.execute_task(task)
            task["completed_at"] = datetime.now().isoformat()
            task["status"] = result.get("status", TaskStatus.COMPLETED.value)
            task["result"] = result
            
        except Exception as e:
            task["completed_at"] = datetime.now().isoformat()
            task["status"] = TaskStatus.FAILED.value
            task["error"] = str(e)
            result = {"status": TaskStatus.FAILED.value, "error": str(e)}
        
        finally:
            # Move to completed
            self.running_tasks.pop(task_id, None)
            self.completed_tasks.append(task)
            # Keep only last 100 completed tasks
            if len(self.completed_tasks) > 100:
                self.completed_tasks = self.completed_tasks[-100:]
        
        return {
            "task_id": task_id,
            "status": task["status"],
            "result": result
        }
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a task."""
        # Check running tasks
        if task_id in self.running_tasks:
            return self.running_tasks[task_id]
        
        # Check completed tasks
        for task in self.completed_tasks:
            if task["task_id"] == task_id:
                return task
        
        return None
    
    def get_task_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get task execution history."""
        return self.completed_tasks[-limit:]
    
    def get_running_tasks(self) -> List[Dict[str, Any]]:
        """Get currently running tasks."""
        return list(self.running_tasks.values())
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task["status"] = TaskStatus.CANCELLED.value
            task["completed_at"] = datetime.now().isoformat()
            self.completed_tasks.append(task)
            self.running_tasks.pop(task_id)
            return True
        return False

