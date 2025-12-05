"""
Base agent class for task execution.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime
import json


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, agent_id: str, name: str, description: str):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.status = "idle"
        self.capabilities: List[str] = []
        self.current_task: Optional[Dict[str, Any]] = None
        self.task_history: List[Dict[str, Any]] = []
    
    @abstractmethod
    def can_execute(self, task_type: str) -> bool:
        """Check if agent can execute a task type."""
        pass
    
    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task."""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "capabilities": self.capabilities,
            "current_task": self.current_task,
            "task_count": len(self.task_history)
        }
    
    def get_task_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get task history."""
        return self.task_history[-limit:]
    
    def _log_task(self, task: Dict[str, Any], result: Dict[str, Any]):
        """Log task execution."""
        log_entry = {
            "task_id": task.get("task_id"),
            "task_type": task.get("task_type"),
            "status": result.get("status"),
            "started_at": task.get("started_at"),
            "completed_at": datetime.now().isoformat(),
            "result": result
        }
        self.task_history.append(log_entry)

