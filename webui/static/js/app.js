// Main JavaScript for NVIDIA RAG Blueprint Installer Web UI

const API_BASE = '/api';
let currentStep = 1;
let installationConfig = {};

// Utility Functions

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastBody = document.getElementById('toast-body');
    toastBody.textContent = message;
    toast.className = `toast ${type}`;
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

async function apiCall(endpoint, method = 'GET', body = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        if (body) {
            options.body = JSON.stringify(body);
        }
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || 'API request failed');
        }
        return data;
    } catch (error) {
        console.error('API Error:', error);
        showToast(`Error: ${error.message}`, 'error');
        throw error;
    }
}

// Installation Wizard Functions

async function checkPrerequisites() {
    const resultsDiv = document.getElementById('prerequisites-results');
    resultsDiv.innerHTML = '<div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>';
    
    try {
        const data = await apiCall('/validate/preflight', 'POST', {});
        displayValidationResults(data.results, resultsDiv);
        showToast('Prerequisites check completed', 'success');
    } catch (error) {
        resultsDiv.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
}

function displayValidationResults(results, container) {
    let html = '<table class="table validation-table"><thead><tr><th>Check</th><th>Status</th><th>Message</th></tr></thead><tbody>';
    
    results.forEach(result => {
        const statusClass = `status-${result.status}`;
        const statusIcon = result.status === 'pass' ? '✓' : result.status === 'fail' ? '✗' : '⚠';
        html += `
            <tr>
                <td>${result.name}</td>
                <td><span class="status-badge ${statusClass}">${statusIcon} ${result.status.toUpperCase()}</span></td>
                <td>${result.message || ''}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

function nextStep() {
    if (currentStep < 6) {
        document.getElementById(`step-${currentStep}`).classList.add('d-none');
        currentStep++;
        document.getElementById(`step-${currentStep}`).classList.remove('d-none');
        updateNavigation();
        loadStepContent(currentStep);
    }
}

function prevStep() {
    if (currentStep > 1) {
        document.getElementById(`step-${currentStep}`).classList.add('d-none');
        currentStep--;
        document.getElementById(`step-${currentStep}`).classList.remove('d-none');
        updateNavigation();
    }
}

function updateNavigation() {
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const installBtn = document.getElementById('install-btn');
    
    prevBtn.style.display = currentStep > 1 ? 'inline-block' : 'none';
    
    if (currentStep < 5) {
        nextBtn.style.display = 'inline-block';
        installBtn.style.display = 'none';
    } else if (currentStep === 5) {
        nextBtn.style.display = 'none';
        installBtn.style.display = 'inline-block';
    } else {
        nextBtn.style.display = 'none';
        installBtn.style.display = 'none';
    }
}

function loadStepContent(step) {
    switch(step) {
        case 2:
            loadAPIKeysConfig();
            break;
        case 3:
            loadNodeConfig();
            break;
        case 4:
            loadBlueprintConfig();
            break;
        case 5:
            loadReviewConfig();
            break;
    }
}

async function loadAPIKeysConfig() {
    const container = document.getElementById('api-keys-config');
    try {
        const data = await apiCall('/keys/list');
        let html = '<div class="row">';
        
        ['nvidia', 'openai', 'anthropic'].forEach(keyType => {
            const key = data.keys[keyType];
            const required = keyType === 'nvidia' ? '<span class="text-danger">(Required)</span>' : '<span class="text-muted">(Optional)</span>';
            const status = key.configured ? '<span class="badge bg-success">Configured</span>' : '<span class="badge bg-warning">Not Set</span>';
            
            html += `
                <div class="col-md-4 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h6>${keyType.toUpperCase()} API Key ${required}</h6>
                            <p>Status: ${status}</p>
                            <button class="btn btn-sm btn-primary" onclick="setAPIKeyModal('${keyType}')">
                                <i class="bi bi-pencil"></i> Set Key
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">Error loading API keys: ${error.message}</div>`;
    }
}

function loadNodeConfig() {
    const container = document.getElementById('node-config');
    container.innerHTML = `
        <div id="nodes-list"></div>
        <button class="btn btn-primary" onclick="addNode()">
            <i class="bi bi-plus-circle"></i> Add Node
        </button>
    `;
    installationConfig.nodes = installationConfig.nodes || [];
    renderNodes();
}

function addNode() {
    const hostname = prompt('Hostname:');
    const ip = prompt('IP Address:');
    const username = prompt('SSH Username:', 'ubuntu');
    const isMaster = confirm('Is this a master node?');
    const hasGpu = confirm('Does this node have GPU?');
    
    if (hostname && ip) {
        installationConfig.nodes.push({
            hostname,
            ip,
            username,
            is_master: isMaster,
            has_gpu: hasGpu
        });
        renderNodes();
    }
}

function renderNodes() {
    const container = document.getElementById('nodes-list');
    if (!installationConfig.nodes || installationConfig.nodes.length === 0) {
        container.innerHTML = '<p class="text-muted">No nodes configured. Click "Add Node" to add one.</p>';
        return;
    }
    
    let html = '';
    installationConfig.nodes.forEach((node, index) => {
        const nodeClass = node.is_master ? 'master' : node.has_gpu ? 'gpu' : '';
        html += `
            <div class="node-card ${nodeClass}">
                <div class="d-flex justify-content-between">
                    <div>
                        <strong>${node.hostname}</strong> ${node.is_master ? '<span class="badge bg-success">Master</span>' : ''} ${node.has_gpu ? '<span class="badge bg-primary">GPU</span>' : ''}
                        <br>
                        <small class="text-muted">${node.ip} (${node.username})</small>
                    </div>
                    <button class="btn btn-sm btn-danger" onclick="removeNode(${index})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });
    container.innerHTML = html;
}

function removeNode(index) {
    installationConfig.nodes.splice(index, 1);
    renderNodes();
}

function loadBlueprintConfig() {
    const container = document.getElementById('blueprint-config');
    installationConfig.blueprint_version = installationConfig.blueprint_version || 'v2.2.1';
    installationConfig.gpu_count = installationConfig.gpu_count || 1;
    installationConfig.memory_limit = installationConfig.memory_limit || '16Gi';
    
    container.innerHTML = `
        <div class="mb-3">
            <label class="form-label">Blueprint Version</label>
            <input type="text" class="form-control" id="blueprint-version" value="${installationConfig.blueprint_version}">
        </div>
        <div class="mb-3">
            <label class="form-label">GPU Count per GPU Node</label>
            <input type="number" class="form-control" id="gpu-count" value="${installationConfig.gpu_count}" min="1">
        </div>
        <div class="mb-3">
            <label class="form-label">Memory Limit</label>
            <input type="text" class="form-control" id="memory-limit" value="${installationConfig.memory_limit}" placeholder="e.g., 16Gi">
        </div>
    `;
}

function loadReviewConfig() {
    const container = document.getElementById('review-config');
    const version = document.getElementById('blueprint-version')?.value || installationConfig.blueprint_version;
    const gpuCount = document.getElementById('gpu-count')?.value || installationConfig.gpu_count;
    const memoryLimit = document.getElementById('memory-limit')?.value || installationConfig.memory_limit;
    
    installationConfig.blueprint_version = version;
    installationConfig.gpu_count = parseInt(gpuCount);
    installationConfig.memory_limit = memoryLimit;
    
    container.innerHTML = `
        <div class="card">
            <div class="card-body">
                <h6>Configuration Summary</h6>
                <table class="table">
                    <tr><td><strong>Blueprint Version</strong></td><td>${version}</td></tr>
                    <tr><td><strong>Nodes</strong></td><td>${installationConfig.nodes?.length || 0}</td></tr>
                    <tr><td><strong>GPU Count</strong></td><td>${gpuCount}</td></tr>
                    <tr><td><strong>Memory Limit</strong></td><td>${memoryLimit}</td></tr>
                </table>
            </div>
        </div>
    `;
}

async function startInstallation() {
    const container = document.getElementById('installation-progress');
    container.innerHTML = '<div class="spinner-border" role="status"><span class="visually-hidden">Starting installation...</span></div>';
    
    // Move to step 6
    document.getElementById(`step-${currentStep}`).classList.add('d-none');
    currentStep = 6;
    document.getElementById(`step-${currentStep}`).classList.remove('d-none');
    updateNavigation();
    
    // Connect to WebSocket for progress updates
    const ws = new WebSocket(`ws://${window.location.host}/ws/install`);
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'progress') {
            updateInstallationProgress(data);
        } else if (data.type === 'complete') {
            container.innerHTML += `<div class="alert alert-success">${data.message}</div>`;
            ws.close();
        } else if (data.type === 'error') {
            container.innerHTML += `<div class="alert alert-danger">Error: ${data.message}</div>`;
            ws.close();
        }
    };
    
    ws.onerror = (error) => {
        container.innerHTML += `<div class="alert alert-danger">WebSocket error: ${error}</div>`;
    };
    
    try {
        await apiCall('/install/start', 'POST', installationConfig);
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">Failed to start installation: ${error.message}</div>`;
    }
}

function updateInstallationProgress(data) {
    const container = document.getElementById('installation-progress');
    const stepHtml = `
        <div class="progress-step ${data.status === 'completed' ? 'completed' : data.status === 'running' ? 'running' : 'pending'}">
            <span class="progress-icon">${data.status === 'completed' ? '✓' : data.status === 'running' ? '⟳' : '○'}</span>
            <span>Step ${data.step}: ${data.name}</span>
            <span class="ms-auto">${data.progress}%</span>
        </div>
    `;
    container.innerHTML = (container.innerHTML || '') + stepHtml;
}

// Validation Functions

async function runValidation() {
    const resultsDiv = document.getElementById('validation-results');
    resultsDiv.innerHTML = '<div class="spinner-border" role="status"><span class="visually-hidden">Running validation...</span></div>';
    
    try {
        const data = await apiCall('/validate/preflight', 'POST', {});
        displayValidationResults(data.results, resultsDiv);
        
        const summary = data.summary;
        resultsDiv.innerHTML += `
            <div class="alert alert-info mt-3">
                <strong>Summary:</strong> ${summary.passed}/${summary.total} checks passed
                ${summary.failed > 0 ? `, ${summary.failed} failed` : ''}
                ${summary.warnings > 0 ? `, ${summary.warnings} warnings` : ''}
            </div>
        `;
        showToast('Validation completed', 'success');
    } catch (error) {
        resultsDiv.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
}

// API Key Functions

async function loadAPIKeys() {
    const container = document.getElementById('api-keys-list');
    try {
        const data = await apiCall('/keys/list');
        let html = '<h6>Configured API Keys</h6><table class="table"><thead><tr><th>Key Type</th><th>Status</th><th>Actions</th></tr></thead><tbody>';
        
        Object.entries(data.keys).forEach(([keyType, key]) => {
            const required = keyType === 'nvidia' ? '<span class="text-danger">(Required)</span>' : '<span class="text-muted">(Optional)</span>';
            const status = key.configured ? '<span class="badge bg-success">Configured</span>' : '<span class="badge bg-warning">Not Set</span>';
            html += `
                <tr>
                    <td>${keyType.toUpperCase()} ${required}</td>
                    <td>${status}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="setAPIKeyModal('${keyType}')">Set</button>
                        ${key.configured ? `<button class="btn btn-sm btn-info" onclick="testAPIKey('${keyType}')">Test</button>` : ''}
                        ${key.configured ? `<button class="btn btn-sm btn-danger" onclick="removeAPIKey('${keyType}')">Remove</button>` : ''}
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">Error loading API keys: ${error.message}</div>`;
    }
}

function setAPIKeyModal(keyType) {
    const keyValue = prompt(`Enter ${keyType.toUpperCase()} API key:`);
    if (keyValue) {
        setAPIKey(keyType, keyValue);
    }
}

async function setAPIKey(keyType = null, keyValue = null) {
    keyType = keyType || document.getElementById('key-type').value;
    keyValue = keyValue || document.getElementById('key-value').value;
    const testKey = document.getElementById('test-key')?.checked ?? true;
    
    if (!keyValue) {
        showToast('Please enter an API key', 'error');
        return;
    }
    
    try {
        await apiCall('/keys/set', 'POST', {
            key_type: keyType,
            key_value: keyValue,
            test: testKey
        });
        showToast(`${keyType.toUpperCase()} API key set successfully`, 'success');
        document.getElementById('key-value').value = '';
        loadAPIKeys();
        if (currentStep === 2) {
            loadAPIKeysConfig();
        }
    } catch (error) {
        showToast(`Failed to set API key: ${error.message}`, 'error');
    }
}

async function testAPIKey(keyType) {
    try {
        const data = await apiCall('/keys/test', 'POST', {
            key_type: keyType,
            key_value: ''
        });
        showToast(data.message, data.valid ? 'success' : 'error');
    } catch (error) {
        showToast(`Failed to test API key: ${error.message}`, 'error');
    }
}

async function removeAPIKey(keyType) {
    if (!confirm(`Are you sure you want to remove the ${keyType.toUpperCase()} API key?`)) {
        return;
    }
    
    try {
        await apiCall(`/keys/${keyType}`, 'DELETE');
        showToast(`${keyType.toUpperCase()} API key removed`, 'success');
        loadAPIKeys();
    } catch (error) {
        showToast(`Failed to remove API key: ${error.message}`, 'error');
    }
}

// Configuration Functions

async function loadConfig() {
    const container = document.getElementById('config-editor');
    try {
        const data = await apiCall('/config');
        container.innerHTML = `
            <textarea class="form-control config-editor" id="config-yaml">${JSON.stringify(data.config, null, 2)}</textarea>
        `;
        showToast('Configuration loaded', 'success');
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">Error loading configuration: ${error.message}</div>`;
    }
}

async function saveConfig() {
    const configText = document.getElementById('config-yaml').value;
    try {
        const config = JSON.parse(configText);
        const data = await apiCall('/config', 'POST', config);
        if (data.status === 'success') {
            showToast('Configuration saved successfully', 'success');
        } else {
            showToast(`Configuration validation failed: ${data.errors.join(', ')}`, 'error');
        }
    } catch (error) {
        showToast(`Failed to save configuration: ${error.message}`, 'error');
    }
}

async function generateTemplate() {
    const container = document.getElementById('config-editor');
    try {
        const data = await apiCall('/config/template');
        container.innerHTML = `
            <textarea class="form-control config-editor" id="config-yaml">${JSON.stringify(data.template, null, 2)}</textarea>
        `;
        showToast('Template generated', 'success');
    } catch (error) {
        showToast(`Failed to generate template: ${error.message}`, 'error');
    }
}

async function validateConfig() {
    const configText = document.getElementById('config-yaml').value;
    try {
        const config = JSON.parse(configText);
        const data = await apiCall('/config/validate', 'POST', config);
        if (data.valid) {
            showToast('Configuration is valid', 'success');
        } else {
            showToast(`Configuration validation failed: ${data.errors.join(', ')}`, 'error');
        }
    } catch (error) {
        showToast(`Failed to validate configuration: ${error.message}`, 'error');
    }
}

// Diagnostics Functions

async function runDiagnostics() {
    const resultsDiv = document.getElementById('diagnostics-results');
    resultsDiv.innerHTML = '<div class="spinner-border" role="status"><span class="visually-hidden">Running diagnostics...</span></div>';
    
    try {
        // For now, use validation endpoint
        const data = await apiCall('/validate/preflight', 'POST', {});
        displayValidationResults(data.results, resultsDiv);
        showToast('Diagnostics completed', 'success');
    } catch (error) {
        resultsDiv.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
}

// Agent and Task Functions

async function loadAgents() {
    const container = document.getElementById('agents-list');
    try {
        const data = await apiCall('/agents');
        let html = '';
        
        data.agents.forEach(agent => {
            const statusClass = agent.status === 'idle' ? 'success' : 'warning';
            html += `
                <div class="card mb-2">
                    <div class="card-body">
                        <h6>${agent.name}</h6>
                        <p class="text-muted small">${agent.description}</p>
                        <div class="mb-2">
                            <span class="badge bg-${statusClass}">${agent.status}</span>
                            ${agent.current_task ? `<span class="badge bg-info">Running Task</span>` : ''}
                        </div>
                        <div class="small">
                            <strong>Capabilities:</strong><br>
                            ${agent.capabilities.map(c => `<span class="badge bg-secondary">${c}</span>`).join(' ')}
                        </div>
                        <div class="small mt-2">
                            Tasks executed: ${agent.task_count}
                        </div>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html || '<p class="text-muted">No agents available</p>';
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">Error loading agents: ${error.message}</div>`;
    }
}

async function loadTasks() {
    const container = document.getElementById('tasks-list');
    try {
        const data = await apiCall('/agents/tasks?limit=20');
        let html = '<table class="table"><thead><tr><th>Task ID</th><th>Type</th><th>Agent</th><th>Status</th><th>Created</th><th>Actions</th></tr></thead><tbody>';
        
        data.tasks.forEach(task => {
            const statusClass = {
                'completed': 'success',
                'running': 'primary',
                'failed': 'danger',
                'pending': 'warning',
                'cancelled': 'secondary'
            }[task.status] || 'secondary';
            
            html += `
                <tr>
                    <td><code>${task.task_id.substring(0, 8)}...</code></td>
                    <td>${task.task_type}</td>
                    <td>${task.agent_id}</td>
                    <td><span class="badge bg-${statusClass}">${task.status}</span></td>
                    <td>${new Date(task.created_at).toLocaleString()}</td>
                    <td>
                        <button class="btn btn-sm btn-info" onclick="viewTask('${task.task_id}')">
                            <i class="bi bi-eye"></i> View
                        </button>
                        ${task.status === 'running' ? `
                            <button class="btn btn-sm btn-danger" onclick="cancelTask('${task.task_id}')">
                                <i class="bi bi-x-circle"></i> Cancel
                            </button>
                        ` : ''}
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        container.innerHTML = html || '<p class="text-muted">No tasks found</p>';
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">Error loading tasks: ${error.message}</div>`;
    }
}

function showTaskForm() {
    document.getElementById('task-form').style.display = 'block';
    loadAgentCapabilities();
}

function hideTaskForm() {
    document.getElementById('task-form').style.display = 'none';
}

async function loadAgentCapabilities() {
    try {
        const data = await apiCall('/agents/capabilities');
        const agentSelect = document.getElementById('task-agent');
        const taskTypeSelect = document.getElementById('task-type');
        
        // Populate agent select
        agentSelect.innerHTML = '<option value="">Auto-select</option>';
        Object.keys(data.capabilities).forEach(agentId => {
            agentSelect.innerHTML += `<option value="${agentId}">${agentId}</option>`;
        });
        
        // Populate task type select
        taskTypeSelect.innerHTML = '<option value="">Select task type</option>';
        Object.entries(data.capabilities).forEach(([agentId, capabilities]) => {
            capabilities.forEach(capability => {
                taskTypeSelect.innerHTML += `<option value="${capability}" data-agent="${agentId}">${capability}</option>`;
            });
        });
    } catch (error) {
        showToast(`Error loading capabilities: ${error.message}`, 'error');
    }
}

async function submitTask() {
    const agentId = document.getElementById('task-agent').value;
    const taskType = document.getElementById('task-type').value;
    const priority = document.getElementById('task-priority').value;
    const configText = document.getElementById('task-config').value;
    
    if (!taskType) {
        showToast('Please select a task type', 'error');
        return;
    }
    
    let config = {};
    if (configText) {
        try {
            config = JSON.parse(configText);
        } catch (e) {
            showToast('Invalid JSON configuration', 'error');
            return;
        }
    }
    
    try {
        const data = await apiCall('/agents/tasks', 'POST', {
            agent_id: agentId || undefined,
            task_type: taskType,
            priority: priority,
            config: config
        });
        
        showToast(`Task submitted: ${data.task.task_id}`, 'success');
        hideTaskForm();
        loadTasks();
        
        // Connect to WebSocket for progress updates
        connectTaskWebSocket(data.task.task_id);
    } catch (error) {
        showToast(`Failed to submit task: ${error.message}`, 'error');
    }
}

async function viewTask(taskId) {
    try {
        const data = await apiCall(`/agents/tasks/${taskId}`);
        const task = data.task;
        
        let html = `
            <div class="modal fade" id="taskModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Task Details</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <table class="table">
                                <tr><th>Task ID</th><td><code>${task.task_id}</code></td></tr>
                                <tr><th>Type</th><td>${task.task_type}</td></tr>
                                <tr><th>Agent</th><td>${task.agent_id}</td></tr>
                                <tr><th>Status</th><td><span class="badge bg-${task.status === 'completed' ? 'success' : task.status === 'failed' ? 'danger' : 'warning'}">${task.status}</span></td></tr>
                                <tr><th>Created</th><td>${new Date(task.created_at).toLocaleString()}</td></tr>
                                ${task.started_at ? `<tr><th>Started</th><td>${new Date(task.started_at).toLocaleString()}</td></tr>` : ''}
                                ${task.completed_at ? `<tr><th>Completed</th><td>${new Date(task.completed_at).toLocaleString()}</td></tr>` : ''}
                            </table>
                            ${task.result ? `<h6>Result:</h6><pre class="bg-light p-3">${JSON.stringify(task.result, null, 2)}</pre>` : ''}
                            ${task.error ? `<div class="alert alert-danger">Error: ${task.error}</div>` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', html);
        const modal = new bootstrap.Modal(document.getElementById('taskModal'));
        modal.show();
        
        // Remove modal from DOM after closing
        document.getElementById('taskModal').addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    } catch (error) {
        showToast(`Error loading task: ${error.message}`, 'error');
    }
}

async function cancelTask(taskId) {
    if (!confirm('Are you sure you want to cancel this task?')) {
        return;
    }
    
    try {
        await apiCall(`/agents/tasks/${taskId}`, 'DELETE');
        showToast('Task cancelled', 'success');
        loadTasks();
    } catch (error) {
        showToast(`Failed to cancel task: ${error.message}`, 'error');
    }
}

function connectTaskWebSocket(taskId) {
    const ws = new WebSocket(`ws://${window.location.host}/ws/agents/tasks/${taskId}`);
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'update') {
            showToast(`Task ${taskId.substring(0, 8)}... updated: ${data.task.status}`, 'info');
            loadTasks(); // Refresh task list
        }
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    updateNavigation();
    loadAPIKeys();
    
    // Load agents when agents tab is clicked
    document.getElementById('agents-tab').addEventListener('shown.bs.tab', () => {
        loadAgents();
        loadTasks();
    });
});

