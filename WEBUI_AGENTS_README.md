# Web UI Agents System

## Overview

The Web UI now includes an **agent-based task execution system** that allows you to perform various operational tasks once the base OS/K8s and CSI are installed. The system uses specialized agents to handle different types of tasks.

## Available Agents

### 1. Installation Agent
**Purpose**: Handles installation of Kubernetes components, GPU Operator, and RAG Blueprint

**Capabilities**:
- `install_kubernetes` - Deploy Kubernetes cluster
- `install_gpu_operator` - Install NVIDIA GPU Operator
- `install_rag_blueprint` - Deploy NVIDIA RAG Blueprint
- `install_observability` - Install monitoring stack (Prometheus, Grafana, Jaeger)
- `install_storage` - Configure storage components (NFS, CSI)

### 2. Management Agent
**Purpose**: Handles cluster management, scaling, updates, and maintenance

**Capabilities**:
- `scale_services` - Scale services up or down
- `update_components` - Update cluster components
- `backup_cluster` - Backup cluster configuration and data
- `restore_cluster` - Restore cluster from backup
- `health_check` - Perform comprehensive health check
- `cleanup_resources` - Clean up unused resources

### 3. Configuration Agent
**Purpose**: Manages cluster configuration, validation, and deployment

**Capabilities**:
- `update_config` - Update cluster configuration
- `validate_config` - Validate configuration
- `apply_config` - Apply configuration to cluster
- `rollback_config` - Rollback to previous configuration
- `export_config` - Export current configuration
- `import_config` - Import configuration from file

## Using Agents in the Web UI

### Accessing Agents

1. Start the web server:
   ```bash
   python3 webui/run.py
   ```

2. Open `http://localhost:8000` in your browser

3. Click on the **"Agents & Tasks"** tab

### Viewing Available Agents

The left panel shows all available agents with their:
- Status (idle/running)
- Capabilities
- Current task (if any)
- Task execution count

### Submitting Tasks

1. Click **"New Task"** button
2. Select an agent (or leave as "Auto-select" to automatically find the right agent)
3. Choose a task type from the dropdown
4. Set priority (Low, Medium, High, Critical)
5. Enter configuration as JSON (optional)
6. Click **"Submit Task"**

### Monitoring Tasks

- **Task List**: Shows all tasks with their status
- **Task Details**: Click "View" to see detailed task information
- **Real-time Updates**: Tasks update in real-time via WebSocket
- **Cancel Tasks**: Cancel running tasks if needed

## API Endpoints

### Agent Management

```bash
# Get all agents
GET /api/agents

# Get specific agent
GET /api/agents/{agent_id}

# Get agent capabilities
GET /api/agents/capabilities
```

### Task Management

```bash
# Submit a task
POST /api/agents/tasks
{
  "agent_id": "installation",  # Optional, auto-select if not provided
  "task_type": "install_rag_blueprint",
  "priority": "high",
  "config": {
    "blueprint_version": "v2.2.1",
    "nodes": [...]
  }
}

# Get task status
GET /api/agents/tasks/{task_id}

# Get task history
GET /api/agents/tasks?limit=20

# Get running tasks
GET /api/agents/tasks?status=running

# Cancel a task
DELETE /api/agents/tasks/{task_id}
```

### WebSocket for Real-time Updates

```javascript
// Connect to task progress stream
ws://localhost:8000/ws/agents/tasks/{task_id}
```

## Example Tasks

### Install RAG Blueprint

```json
{
  "task_type": "install_rag_blueprint",
  "priority": "high",
  "config": {
    "blueprint_version": "v2.2.1",
    "gpu_count": 1,
    "memory_limit": "16Gi"
  }
}
```

### Scale Services

```json
{
  "task_type": "scale_services",
  "priority": "medium",
  "config": {
    "service": "rag-server",
    "replicas": 3
  }
}
```

### Health Check

```json
{
  "task_type": "health_check",
  "priority": "medium",
  "config": {}
}
```

### Backup Cluster

```json
{
  "task_type": "backup_cluster",
  "priority": "high",
  "config": {
    "backup_path": "/backups/cluster-backup-2024"
  }
}
```

## Task Status

Tasks can have the following statuses:
- **pending** - Task is queued
- **running** - Task is currently executing
- **completed** - Task completed successfully
- **failed** - Task failed with an error
- **cancelled** - Task was cancelled

## Task Priority

Tasks can be assigned priorities:
- **low** - Low priority, executed when resources are available
- **medium** - Normal priority (default)
- **high** - High priority, executed before lower priority tasks
- **critical** - Critical priority, executed immediately

## Architecture

```
Agent Manager
├── Installation Agent
│   ├── install_kubernetes
│   ├── install_gpu_operator
│   ├── install_rag_blueprint
│   ├── install_observability
│   └── install_storage
├── Management Agent
│   ├── scale_services
│   ├── update_components
│   ├── backup_cluster
│   ├── restore_cluster
│   ├── health_check
│   └── cleanup_resources
└── Configuration Agent
    ├── update_config
    ├── validate_config
    ├── apply_config
    ├── rollback_config
    ├── export_config
    └── import_config
```

## Extending the System

### Adding a New Agent

1. Create a new agent class inheriting from `BaseAgent`:
   ```python
   from webui.agents.base_agent import BaseAgent
   
   class MyAgent(BaseAgent):
       def __init__(self):
           super().__init__(
               agent_id="my_agent",
               name="My Agent",
               description="Description of what this agent does"
           )
           self.capabilities = ["task1", "task2"]
       
       def can_execute(self, task_type: str) -> bool:
           return task_type in self.capabilities
       
       async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
           # Implement task execution
           pass
   ```

2. Register the agent in `AgentManager._initialize_agents()`

### Adding New Capabilities

1. Add the capability to the agent's `capabilities` list
2. Implement the execution method in the agent
3. The capability will automatically appear in the UI

## Integration with Ansible

The agents are designed to integrate with your existing Ansible playbooks:

```python
async def _install_rag_blueprint(self, config: Dict[str, Any]) -> Dict[str, Any]:
    """Install NVIDIA RAG Blueprint using Ansible."""
    # Call your existing Ansible playbook
    from cli.executors.ansible import AnsibleExecutor
    
    executor = AnsibleExecutor()
    result = await executor.run_playbook(
        playbook="playbooks/04-rag-blueprint.yml",
        inventory=config.get("inventory"),
        extra_vars=config
    )
    
    return result
```

## Next Steps

1. **Integrate with Ansible** - Connect agents to actual Ansible playbooks
2. **Add More Agents** - Create specialized agents for specific tasks
3. **Task Scheduling** - Add ability to schedule tasks
4. **Task Dependencies** - Support for task dependencies
5. **Task Retry** - Automatic retry for failed tasks
6. **Notifications** - Email/Slack notifications for task completion

## Status

✅ **Agent System**: Fully implemented  
✅ **Agent Manager**: Working  
✅ **Task Queue**: Functional  
✅ **Web UI Integration**: Complete  
✅ **WebSocket Updates**: Real-time progress  
⏳ **Ansible Integration**: Next step  
⏳ **Hardware Validation**: Next step  

---

**Ready to use!** Start the web server and navigate to the "Agents & Tasks" tab to begin using the agent system.

