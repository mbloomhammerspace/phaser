# Integration Summary - Ansible, Hardware & Network Validation

## ✅ Completed Integrations

### 1. Ansible Execution Integration ✅

**Created Executors**:
- `cli/executors/ansible.py` - Ansible playbook execution
- `cli/executors/helm.py` - Helm chart operations
- `cli/executors/kubectl.py` - Kubernetes command execution

**Features**:
- Async playbook execution
- Inventory file handling
- Extra variables support
- Tag and skip-tag support
- Error handling and logging
- Playbook validation

**Integration Points**:
- Installation Agent now uses Ansible executor for:
  - Kubernetes cluster deployment (`01-kubespray.yml`)
  - GPU Operator installation (`03-gpu-operator.yml`)
  - RAG Blueprint deployment (`04-rag-blueprint.yml`)

**Usage**:
```python
from cli.executors.ansible import AnsibleExecutor

executor = AnsibleExecutor()
result = await executor.run_playbook(
    playbook="04-rag-blueprint.yml",
    inventory="discovery/inventory.yml",
    extra_vars={"blueprint_version": "v2.2.1"}
)
```

### 2. Hardware Validation ✅

**Enhanced Validator**: `cli/validators/hardware.py`

**Capabilities**:
- SSH to nodes and check hardware
- CPU core count validation
- RAM validation
- Storage availability check
- GPU detection and validation
- Per-node hardware reports

**Checks Performed**:
- **CPU**: Validates minimum cores (4 for master, 8 for worker)
- **RAM**: Validates minimum memory (8GB for master, 16GB for worker)
- **Storage**: Checks available disk space (minimum 50GB)
- **GPU**: Detects NVIDIA GPUs and validates drivers

**Usage**:
```python
from cli.validators.hardware import HardwareValidator

validator = HardwareValidator("discovery/inventory.yml")
results = validator.validate_all()
```

### 3. Network Validation ✅

**Enhanced Validator**: `cli/validators/network.py`

**Capabilities**:
- SSH connectivity testing
- Inter-node ping tests
- Port accessibility checks
- Network connectivity validation

**Checks Performed**:
- **SSH Connectivity**: Tests SSH access to all nodes
- **Inter-node Connectivity**: Pings between nodes
- **Port Accessibility**: Tests required Kubernetes ports:
  - 6443 (Kubernetes API)
  - 2379-2380 (etcd)
  - 10250 (kubelet)
  - 10256 (kube-proxy)

**Usage**:
```python
from cli.validators.network import NetworkValidator

validator = NetworkValidator("discovery/inventory.yml")
results = validator.validate_all()
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web UI / CLI                          │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│                  Agent Manager                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Installation │  │  Management  │  │ Configuration│  │
│  │    Agent     │  │    Agent     │  │    Agent     │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼─────────┐
│              Executors Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Ansible  │  │   Helm   │  │ kubectl  │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
└───────┼──────────────┼──────────────┼───────────────────┘
        │              │              │
┌───────▼──────────────▼──────────────▼───────────────────┐
│              Validation Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ System   │  │ Hardware │  │ Network  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
```

## Integration Flow

### Installation Flow with Ansible

1. **User submits task** via Web UI or CLI
2. **Agent Manager** routes to Installation Agent
3. **Installation Agent** calls Ansible Executor
4. **Ansible Executor** runs playbook with inventory
5. **Results** returned to agent and displayed in UI

### Validation Flow

1. **User runs validation** (preflight check)
2. **System Validator** checks local requirements
3. **Hardware Validator** SSHs to nodes and checks hardware
4. **Network Validator** tests connectivity and ports
5. **Results** aggregated and displayed

## Example Usage

### Via Web UI

1. Navigate to "Agents & Tasks" tab
2. Click "New Task"
3. Select "Installation Agent"
4. Choose task type: `install_rag_blueprint`
5. Enter configuration:
   ```json
   {
     "inventory_file": "discovery/inventory.yml",
     "blueprint_version": "v2.2.1",
     "gpu_count": 1
   }
   ```
6. Submit task
7. Monitor progress in real-time

### Via CLI

```bash
# Run hardware validation
python3 phaser.py validate preflight --inventory discovery/inventory.yml

# Run network validation
python3 phaser.py validate preflight --inventory discovery/inventory.yml

# Submit installation task via API
curl -X POST http://localhost:8000/api/agents/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "install_rag_blueprint",
    "config": {
      "inventory_file": "discovery/inventory.yml",
      "blueprint_version": "v2.2.1"
    }
  }'
```

## Error Handling

### Ansible Execution
- Playbook validation before execution
- Error capture and reporting
- Detailed stdout/stderr logging
- Return code checking

### Hardware Validation
- SSH connection failures handled gracefully
- Missing SSH keys detected
- Timeout handling for slow connections
- Partial results if some nodes fail

### Network Validation
- Connection timeouts handled
- Port tests with fallback
- Detailed error messages
- Per-node status reporting

## Performance Considerations

### Ansible Execution
- Async execution prevents blocking
- Timeout handling (30s default)
- Progress can be streamed via WebSocket

### Hardware Validation
- Parallel SSH connections (can be optimized)
- Timeout per node (10s SSH, 30s command)
- Caching results (future enhancement)

### Network Validation
- Quick port tests (3s timeout)
- Parallel connectivity tests
- Efficient ping tests (3 packets, 2s wait)

## Security Considerations

### SSH Key Management
- Uses inventory file SSH keys
- StrictHostKeyChecking disabled for automation
- BatchMode for non-interactive execution
- Key file permissions checked

### Network Testing
- Only tests required ports
- No sensitive data in network tests
- Timeout limits prevent hanging

## Next Steps / Future Enhancements

1. **Parallel Execution**: Run hardware/network checks in parallel
2. **Result Caching**: Cache validation results to avoid repeated checks
3. **Progress Streaming**: Stream Ansible output in real-time via WebSocket
4. **Retry Logic**: Automatic retry for failed validations
5. **Comprehensive Logging**: Enhanced logging for debugging
6. **Metrics Collection**: Track execution times and success rates
7. **Inventory Auto-discovery**: Automatically discover nodes if inventory missing

## Testing

### Test Ansible Integration
```bash
# Test playbook execution
python3 -c "
import asyncio
from cli.executors.ansible import AnsibleExecutor

async def test():
    executor = AnsibleExecutor()
    result = await executor.run_playbook('01-kubespray.yml', inventory='discovery/inventory.yml')
    print(result)

asyncio.run(test())
"
```

### Test Hardware Validation
```bash
python3 -c "
from cli.validators.hardware import HardwareValidator
validator = HardwareValidator('discovery/inventory.yml')
results = validator.validate_all()
for r in results:
    print(f\"{r['name']}: {r['status']} - {r['message']}\")
"
```

### Test Network Validation
```bash
python3 -c "
from cli.validators.network import NetworkValidator
validator = NetworkValidator('discovery/inventory.yml')
results = validator.validate_all()
for r in results:
    print(f\"{r['name']}: {r['status']} - {r['message']}\")
"
```

## Status

✅ **Ansible Integration**: Complete and functional  
✅ **Hardware Validation**: Complete with SSH-based checks  
✅ **Network Validation**: Complete with connectivity tests  
✅ **Agent Integration**: Agents use executors for real operations  
✅ **Error Handling**: Comprehensive error handling in place  

---

**All integrations complete!** The system is now ready for production use with real Ansible playbooks, hardware validation, and network testing.

