// MCP Overlay Injector for NVIDIA RAG Blueprint
// This script injects MCP controls into the existing NVIDIA RAG Blueprint interface

(function() {
    'use strict';
    
    // Configuration
    const RAG_SERVER_URL = window.location.origin.replace(':32507', ':8081'); // Adjust port mapping
    const OVERLAY_ID = 'mcp-control-overlay';
    
    // MCP Settings State
    let mcpGlobalEnabled = true;
    let mcpAutoConnect = true;
    
    // Create MCP Control Overlay
    function createMCPOverlay() {
        // Remove existing overlay if it exists
        const existingOverlay = document.getElementById(OVERLAY_ID);
        if (existingOverlay) {
            existingOverlay.remove();
        }
        
        // Create overlay container
        const overlay = document.createElement('div');
        overlay.id = OVERLAY_ID;
        overlay.innerHTML = `
            <div class="mcp-overlay-content">
                <div class="mcp-overlay-header">
                    <h3>🔌 MCP Services Control</h3>
                    <button class="mcp-close-btn" onclick="document.getElementById('${OVERLAY_ID}').style.display='none'">×</button>
                </div>
                <div class="mcp-overlay-body">
                    <div class="mcp-status">
                        <strong>Status:</strong> <span id="mcp-status-text">Loading...</span>
                    </div>
                    <div class="mcp-controls">
                        <label class="mcp-checkbox-label">
                            <input type="checkbox" id="mcp-global-toggle" ${mcpGlobalEnabled ? 'checked' : ''}>
                            Enable MCP Services
                        </label>
                        <label class="mcp-checkbox-label">
                            <input type="checkbox" id="mcp-auto-connect-toggle" ${mcpAutoConnect ? 'checked' : ''}>
                            Auto-connect MCP Servers
                        </label>
                    </div>
                    <div class="mcp-actions">
                        <button class="mcp-btn mcp-btn-primary" onclick="window.mcpOverlay.enableMCP()">Enable All</button>
                        <button class="mcp-btn mcp-btn-danger" onclick="window.mcpOverlay.disableMCP()">Disable All</button>
                        <button class="mcp-btn mcp-btn-secondary" onclick="window.mcpOverlay.refreshSettings()">Refresh</button>
                    </div>
                </div>
            </div>
        `;
        
        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            #${OVERLAY_ID} {
                position: fixed;
                top: 20px;
                right: 20px;
                width: 300px;
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 10000;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            
            .mcp-overlay-header {
                background: #f8f9fa;
                padding: 12px 16px;
                border-bottom: 1px solid #ddd;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-radius: 8px 8px 0 0;
            }
            
            .mcp-overlay-header h3 {
                margin: 0;
                font-size: 14px;
                font-weight: 600;
                color: #333;
            }
            
            .mcp-close-btn {
                background: none;
                border: none;
                font-size: 18px;
                cursor: pointer;
                color: #666;
                padding: 0;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .mcp-overlay-body {
                padding: 16px;
            }
            
            .mcp-status {
                margin-bottom: 12px;
                padding: 8px;
                background: #e9ecef;
                border-radius: 4px;
                font-size: 12px;
            }
            
            .mcp-controls {
                margin-bottom: 16px;
            }
            
            .mcp-checkbox-label {
                display: flex;
                align-items: center;
                margin-bottom: 8px;
                font-size: 13px;
                cursor: pointer;
            }
            
            .mcp-checkbox-label input[type="checkbox"] {
                margin-right: 8px;
                transform: scale(1.1);
            }
            
            .mcp-actions {
                display: flex;
                gap: 6px;
                flex-wrap: wrap;
            }
            
            .mcp-btn {
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                font-size: 11px;
                cursor: pointer;
                font-weight: 500;
            }
            
            .mcp-btn-primary {
                background: #007bff;
                color: white;
            }
            
            .mcp-btn-danger {
                background: #dc3545;
                color: white;
            }
            
            .mcp-btn-secondary {
                background: #6c757d;
                color: white;
            }
            
            .mcp-btn:hover {
                opacity: 0.8;
            }
            
            #mcp-toggle-button {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                font-size: 18px;
                cursor: pointer;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                z-index: 9999;
            }
            
            #mcp-toggle-button:hover {
                background: #0056b3;
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(overlay);
        
        // Add event listeners
        document.getElementById('mcp-global-toggle').addEventListener('change', function() {
            window.mcpOverlay.updateMCPSettings();
        });
        
        document.getElementById('mcp-auto-connect-toggle').addEventListener('change', function() {
            window.mcpOverlay.updateMCPSettings();
        });
        
        // Load initial settings
        window.mcpOverlay.loadSettings();
    }
    
    // Create toggle button
    function createToggleButton() {
        const toggleBtn = document.createElement('button');
        toggleBtn.id = 'mcp-toggle-button';
        toggleBtn.innerHTML = '🔌';
        toggleBtn.title = 'Toggle MCP Controls';
        toggleBtn.onclick = function() {
            const overlay = document.getElementById(OVERLAY_ID);
            if (overlay) {
                overlay.style.display = overlay.style.display === 'none' ? 'block' : 'none';
            }
        };
        document.body.appendChild(toggleBtn);
    }
    
    // MCP Overlay Functions
    window.mcpOverlay = {
        async loadSettings() {
            try {
                const response = await fetch(`${RAG_SERVER_URL}/mcp/settings`);
                if (response.ok) {
                    const settings = await response.json();
                    mcpGlobalEnabled = settings.mcp_global_enabled;
                    mcpAutoConnect = settings.mcp_auto_connect;
                    
                    // Update UI
                    document.getElementById('mcp-global-toggle').checked = mcpGlobalEnabled;
                    document.getElementById('mcp-auto-connect-toggle').checked = mcpAutoConnect;
                    this.updateStatus();
                }
            } catch (e) {
                console.error('Error loading MCP settings:', e);
                document.getElementById('mcp-status-text').textContent = 'Error loading settings';
            }
        },
        
        async updateMCPSettings() {
            mcpGlobalEnabled = document.getElementById('mcp-global-toggle').checked;
            mcpAutoConnect = document.getElementById('mcp-auto-connect-toggle').checked;
            
            try {
                const response = await fetch(`${RAG_SERVER_URL}/mcp/settings`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        mcp_global_enabled: mcpGlobalEnabled,
                        mcp_auto_connect: mcpAutoConnect
                    })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    console.log('MCP settings updated:', result);
                    this.updateStatus();
                }
            } catch (e) {
                console.error('Error updating MCP settings:', e);
            }
        },
        
        async enableMCP() {
            try {
                const response = await fetch(`${RAG_SERVER_URL}/mcp/enable`, { method: 'POST' });
                if (response.ok) {
                    const result = await response.json();
                    console.log('MCP enabled:', result);
                    this.loadSettings();
                }
            } catch (e) {
                console.error('Error enabling MCP:', e);
            }
        },
        
        async disableMCP() {
            try {
                const response = await fetch(`${RAG_SERVER_URL}/mcp/disable`, { method: 'POST' });
                if (response.ok) {
                    const result = await response.json();
                    console.log('MCP disabled:', result);
                    this.loadSettings();
                }
            } catch (e) {
                console.error('Error disabling MCP:', e);
            }
        },
        
        async refreshSettings() {
            await this.loadSettings();
        },
        
        updateStatus() {
            const statusText = document.getElementById('mcp-status-text');
            if (statusText) {
                statusText.textContent = mcpGlobalEnabled ? 'Enabled' : 'Disabled';
                statusText.style.color = mcpGlobalEnabled ? '#28a745' : '#dc3545';
            }
        }
    };
    
    // Initialize when DOM is ready
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }
        
        // Wait a bit for the page to fully load
        setTimeout(() => {
            createToggleButton();
            createMCPOverlay();
            
            // Hide overlay by default
            const overlay = document.getElementById(OVERLAY_ID);
            if (overlay) {
                overlay.style.display = 'none';
            }
        }, 2000);
    }
    
    // Start the overlay
    init();
    
    console.log('🔌 MCP Overlay Injector loaded! Click the 🔌 button to access MCP controls.');
    
})();
