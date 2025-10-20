// MCP Settings Injector for NVIDIA RAG Blueprint
// Injects MCP control directly into the settings panel next to Guardrails

(function() {
    'use strict';
    
    // Configuration
    const RAG_SERVER_URL = window.location.origin.replace(':32507', ':8081');
    
    // MCP Settings State
    let mcpGlobalEnabled = true;
    let isInjected = false;
    
    // Function to inject MCP controls into the settings panel
    function injectMCPControls() {
        // Look for the Guardrails section in the settings
        const guardrailsSection = findGuardrailsSection();
        if (!guardrailsSection) {
            console.log('Guardrails section not found, retrying...');
            return false;
        }
        
        // Check if already injected
        if (guardrailsSection.querySelector('.mcp-controls-injected')) {
            return true;
        }
        
        // Create MCP controls container
        const mcpContainer = document.createElement('div');
        mcpContainer.className = 'mcp-controls-injected';
        mcpContainer.innerHTML = `
            <div style="margin-top: 16px; padding: 12px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px;">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: 500; color: #495057; margin-right: 8px;">🔌</span>
                    <span style="font-weight: 500; color: #495057; font-size: 14px;">MCP Services</span>
                    <span id="mcp-status-indicator" style="margin-left: auto; font-size: 12px; padding: 2px 6px; border-radius: 3px; background: #28a745; color: white;">Enabled</span>
                </div>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <label style="display: flex; align-items: center; cursor: pointer; font-size: 13px; color: #6c757d;">
                        <input type="checkbox" id="mcp-global-checkbox" ${mcpGlobalEnabled ? 'checked' : ''} style="margin-right: 6px;">
                        Enable MCP Services
                    </label>
                    <button id="mcp-disable-btn" style="background: #dc3545; color: white; border: none; padding: 4px 8px; border-radius: 3px; font-size: 11px; cursor: pointer;">
                        Disable All
                    </button>
                    <button id="mcp-enable-btn" style="background: #28a745; color: white; border: none; padding: 4px 8px; border-radius: 3px; font-size: 11px; cursor: pointer; display: none;">
                        Enable All
                    </button>
                </div>
                <div style="margin-top: 6px; font-size: 11px; color: #6c757d;">
                    Control Model Context Protocol services and tools
                </div>
            </div>
        `;
        
        // Insert after the Guardrails section
        guardrailsSection.parentNode.insertBefore(mcpContainer, guardrailsSection.nextSibling);
        
        // Add event listeners
        document.getElementById('mcp-global-checkbox').addEventListener('change', function() {
            updateMCPSettings();
        });
        
        document.getElementById('mcp-disable-btn').addEventListener('click', function() {
            disableMCP();
        });
        
        document.getElementById('mcp-enable-btn').addEventListener('click', function() {
            enableMCP();
        });
        
        // Load current settings
        loadMCPSettings();
        
        console.log('✅ MCP controls injected into settings panel');
        return true;
    }
    
    // Function to find the Guardrails section
    function findGuardrailsSection() {
        // Look for text containing "Guardrails" or "Guardrails to every response"
        const textNodes = [];
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        let node;
        while (node = walker.nextNode()) {
            if (node.textContent.includes('Guardrails') || node.textContent.includes('Apply guardrails')) {
                textNodes.push(node);
            }
        }
        
        // Find the parent container that likely contains the checkbox
        for (const textNode of textNodes) {
            let parent = textNode.parentElement;
            while (parent) {
                // Look for a checkbox or input in this container
                if (parent.querySelector('input[type="checkbox"]')) {
                    return parent;
                }
                parent = parent.parentElement;
            }
        }
        
        // Fallback: look for any checkbox container near "Guardrails" text
        const guardrailsText = Array.from(document.querySelectorAll('*')).find(el => 
            el.textContent && el.textContent.includes('Guardrails')
        );
        
        if (guardrailsText) {
            let parent = guardrailsText.parentElement;
            while (parent) {
                if (parent.querySelector('input[type="checkbox"]')) {
                    return parent;
                }
                parent = parent.parentElement;
            }
        }
        
        return null;
    }
    
    // Function to load MCP settings from the server
    async function loadMCPSettings() {
        try {
            const response = await fetch(`${RAG_SERVER_URL}/mcp/settings`);
            if (response.ok) {
                const settings = await response.json();
                mcpGlobalEnabled = settings.mcp_global_enabled;
                
                // Update UI
                const checkbox = document.getElementById('mcp-global-checkbox');
                const statusIndicator = document.getElementById('mcp-status-indicator');
                const disableBtn = document.getElementById('mcp-disable-btn');
                const enableBtn = document.getElementById('mcp-enable-btn');
                
                if (checkbox) checkbox.checked = mcpGlobalEnabled;
                
                if (mcpGlobalEnabled) {
                    if (statusIndicator) {
                        statusIndicator.textContent = 'Enabled';
                        statusIndicator.style.background = '#28a745';
                    }
                    if (disableBtn) disableBtn.style.display = 'inline-block';
                    if (enableBtn) enableBtn.style.display = 'none';
                } else {
                    if (statusIndicator) {
                        statusIndicator.textContent = 'Disabled';
                        statusIndicator.style.background = '#dc3545';
                    }
                    if (disableBtn) disableBtn.style.display = 'none';
                    if (enableBtn) enableBtn.style.display = 'inline-block';
                }
                
                console.log('📡 MCP settings loaded:', settings);
            }
        } catch (e) {
            console.error('❌ Error loading MCP settings:', e);
            const statusIndicator = document.getElementById('mcp-status-indicator');
            if (statusIndicator) {
                statusIndicator.textContent = 'Error';
                statusIndicator.style.background = '#ffc107';
            }
        }
    }
    
    // Function to update MCP settings
    async function updateMCPSettings() {
        const checkbox = document.getElementById('mcp-global-checkbox');
        if (!checkbox) return;
        
        mcpGlobalEnabled = checkbox.checked;
        
        try {
            const response = await fetch(`${RAG_SERVER_URL}/mcp/settings`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    mcp_global_enabled: mcpGlobalEnabled
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log('✅ MCP settings updated:', result);
                loadMCPSettings(); // Refresh UI
            }
        } catch (e) {
            console.error('❌ Error updating MCP settings:', e);
            // Revert checkbox state on error
            checkbox.checked = !mcpGlobalEnabled;
            mcpGlobalEnabled = !mcpGlobalEnabled;
        }
    }
    
    // Function to disable MCP
    async function disableMCP() {
        try {
            const response = await fetch(`${RAG_SERVER_URL}/mcp/disable`, {
                method: 'POST'
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log('🔴 MCP disabled:', result);
                loadMCPSettings(); // Refresh UI
                
                // Show visual feedback
                showNotification('MCP Services Disabled', 'warning');
            }
        } catch (e) {
            console.error('❌ Error disabling MCP:', e);
            showNotification('Error disabling MCP', 'error');
        }
    }
    
    // Function to enable MCP
    async function enableMCP() {
        try {
            const response = await fetch(`${RAG_SERVER_URL}/mcp/enable`, {
                method: 'POST'
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log('🟢 MCP enabled:', result);
                loadMCPSettings(); // Refresh UI
                
                // Show visual feedback
                showNotification('MCP Services Enabled', 'success');
            }
        } catch (e) {
            console.error('❌ Error enabling MCP:', e);
            showNotification('Error enabling MCP', 'error');
        }
    }
    
    // Function to show notification
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 16px;
            border-radius: 4px;
            color: white;
            font-size: 14px;
            font-weight: 500;
            z-index: 10000;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            animation: slideIn 0.3s ease-out;
        `;
        
        const colors = {
            success: '#28a745',
            warning: '#ffc107',
            error: '#dc3545',
            info: '#007bff'
        };
        
        notification.style.background = colors[type] || colors.info;
        notification.textContent = message;
        
        // Add animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
    
    // Function to periodically try to inject MCP controls
    function tryInject() {
        if (!isInjected) {
            isInjected = injectMCPControls();
        }
    }
    
    // Initialize when DOM is ready
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }
        
        console.log('🔌 MCP Settings Injector starting...');
        
        // Try to inject immediately
        tryInject();
        
        // Keep trying every 2 seconds until successful
        const interval = setInterval(() => {
            if (!isInjected) {
                tryInject();
            } else {
                clearInterval(interval);
                console.log('✅ MCP controls successfully injected into NVIDIA RAG Blueprint');
            }
        }, 2000);
        
        // Also try when the page content changes (for SPA navigation)
        const observer = new MutationObserver(() => {
            if (!isInjected) {
                tryInject();
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Clean up observer after 30 seconds
        setTimeout(() => {
            observer.disconnect();
        }, 30000);
    }
    
    // Start the injector
    init();
    
})();
