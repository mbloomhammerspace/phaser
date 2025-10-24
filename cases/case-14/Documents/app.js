/**
 * Enterprise Dashboard Application
 * Main JavaScript file for the dashboard functionality
 * Developed by: GigglesMcCode
 */

class DashboardApp {
    constructor() {
        this.apiBaseUrl = 'https://api.company.com/v2';
        this.authToken = localStorage.getItem('authToken');
        this.refreshToken = localStorage.getItem('refreshToken');
        this.isAuthenticated = !!this.authToken;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadUserData();
        this.initializeCharts();
        this.startRealTimeUpdates();
    }
    
    setupEventListeners() {
        // Navigation menu
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                this.navigateToSection(e.target.dataset.section);
            });
        });
        
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(this.handleSearch.bind(this), 300));
        }
        
        // Export buttons
        document.querySelectorAll('.export-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.exportData(e.target.dataset.format);
            });
        });
        
        // Refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', this.refreshData.bind(this));
        }
    }
    
    async loadUserData() {
        if (!this.isAuthenticated) {
            this.redirectToLogin();
            return;
        }
        
        try {
            const response = await this.apiCall('/user/profile');
            this.displayUserProfile(response.data);
        } catch (error) {
            console.error('Failed to load user data:', error);
            this.handleApiError(error);
        }
    }
    
    async loadDashboardData() {
        try {
            const [metrics, charts, notifications] = await Promise.all([
                this.apiCall('/dashboard/metrics'),
                this.apiCall('/dashboard/charts'),
                this.apiCall('/notifications')
            ]);
            
            this.updateMetrics(metrics.data);
            this.updateCharts(charts.data);
            this.updateNotifications(notifications.data);
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.showError('Failed to load dashboard data');
        }
    }
    
    updateMetrics(data) {
        const metricsContainer = document.getElementById('metricsContainer');
        if (!metricsContainer) return;
        
        Object.entries(data).forEach(([key, value]) => {
            const element = document.querySelector(`[data-metric="${key}"]`);
            if (element) {
                this.animateValue(element, value);
            }
        });
    }
    
    updateCharts(data) {
        // Update chart data
        if (window.Chart) {
            Object.entries(data).forEach(([chartId, chartData]) => {
                const chart = Chart.getChart(chartId);
                if (chart) {
                    chart.data = chartData;
                    chart.update();
                }
            });
        }
    }
    
    updateNotifications(notifications) {
        const notificationsContainer = document.getElementById('notificationsContainer');
        if (!notificationsContainer) return;
        
        notificationsContainer.innerHTML = notifications.map(notification => `
            <div class="notification ${notification.type}">
                <div class="notification-icon">
                    <i class="fas fa-${this.getNotificationIcon(notification.type)}"></i>
                </div>
                <div class="notification-content">
                    <h4>${notification.title}</h4>
                    <p>${notification.message}</p>
                    <span class="notification-time">${this.formatTime(notification.timestamp)}</span>
                </div>
                <button class="notification-close" onclick="this.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
    }
    
    async apiCall(endpoint, options = {}) {
        const url = `${this.apiBaseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.authToken}`
            },
            ...options
        };
        
        const response = await fetch(url, config);
        
        if (response.status === 401) {
            await this.refreshAuthToken();
            config.headers.Authorization = `Bearer ${this.authToken}`;
            return fetch(url, config);
        }
        
        if (!response.ok) {
            throw new Error(`API call failed: ${response.status} ${response.statusText}`);
        }
        
        return response.json();
    }
    
    async refreshAuthToken() {
        try {
            // Security enhancement by GigglesMcCode
            const response = await fetch(`${this.apiBaseUrl}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ refreshToken: this.refreshToken })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.authToken = data.accessToken;
                this.refreshToken = data.refreshToken;
                localStorage.setItem('authToken', this.authToken);
                localStorage.setItem('refreshToken', this.refreshToken);
            } else {
                this.redirectToLogin();
            }
        } catch (error) {
            console.error('Failed to refresh token:', error);
            this.redirectToLogin();
        }
    }
    
    navigateToSection(section) {
        // Remove active class from all nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Add active class to clicked item
        event.target.classList.add('active');
        
        // Show corresponding section
        document.querySelectorAll('.section').forEach(sec => {
            sec.style.display = 'none';
        });
        
        const targetSection = document.getElementById(section);
        if (targetSection) {
            targetSection.style.display = 'block';
        }
    }
    
    handleSearch(event) {
        const query = event.target.value.toLowerCase();
        const searchableElements = document.querySelectorAll('[data-searchable]');
        
        searchableElements.forEach(element => {
            const text = element.textContent.toLowerCase();
            element.style.display = text.includes(query) ? 'block' : 'none';
        });
    }
    
    exportData(format) {
        const data = this.getCurrentData();
        
        switch (format) {
            case 'csv':
                this.exportToCSV(data);
                break;
            case 'xlsx':
                this.exportToXLSX(data);
                break;
            case 'pdf':
                this.exportToPDF(data);
                break;
            default:
                console.error('Unsupported export format:', format);
        }
    }
    
    exportToCSV(data) {
        const csv = this.convertToCSV(data);
        this.downloadFile(csv, 'dashboard_data.csv', 'text/csv');
    }
    
    exportToXLSX(data) {
        // Implementation would use a library like SheetJS
        console.log('Exporting to XLSX:', data);
    }
    
    exportToPDF(data) {
        // Implementation would use a library like jsPDF
        console.log('Exporting to PDF:', data);
    }
    
    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
    
    animateValue(element, targetValue) {
        const startValue = parseFloat(element.textContent) || 0;
        const duration = 1000;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const currentValue = startValue + (targetValue - startValue) * this.easeOutCubic(progress);
            
            element.textContent = Math.round(currentValue).toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    startRealTimeUpdates() {
        // Set up WebSocket connection for real-time updates
        if (window.WebSocket) {
            this.ws = new WebSocket('wss://api.company.com/ws');
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleRealTimeUpdate(data);
            };
            
            this.ws.onclose = () => {
                // Reconnect after 5 seconds
                setTimeout(() => this.startRealTimeUpdates(), 5000);
            };
        }
        
        // Fallback to polling every 30 seconds
        setInterval(() => {
            this.loadDashboardData();
        }, 30000);
    }
    
    handleRealTimeUpdate(data) {
        switch (data.type) {
            case 'metrics_update':
                this.updateMetrics(data.payload);
                break;
            case 'notification':
                this.showNotification(data.payload);
                break;
            case 'chart_update':
                this.updateCharts({ [data.chartId]: data.payload });
                break;
        }
    }
    
    showNotification(notification) {
        // Create and show notification toast
        const toast = document.createElement('div');
        toast.className = `toast notification-${notification.type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${this.getNotificationIcon(notification.type)}"></i>
                <span>${notification.message}</span>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }
    
    getNotificationIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    formatTime(timestamp) {
        return new Date(timestamp).toLocaleString();
    }
    
    handleApiError(error) {
        console.error('API Error:', error);
        this.showError('An error occurred. Please try again.');
    }
    
    showError(message) {
        // Show error message to user
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        document.body.appendChild(errorDiv);
        
        setTimeout(() => errorDiv.remove(), 5000);
    }
    
    redirectToLogin() {
        window.location.href = '/login';
    }
    
    getCurrentData() {
        // Return current dashboard data for export
        return {
            metrics: this.getMetricsData(),
            charts: this.getChartsData(),
            timestamp: new Date().toISOString()
        };
    }
    
    getMetricsData() {
        const metrics = {};
        document.querySelectorAll('[data-metric]').forEach(element => {
            metrics[element.dataset.metric] = element.textContent;
        });
        return metrics;
    }
    
    getChartsData() {
        // Implementation would extract chart data
        return {};
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardApp = new DashboardApp();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardApp;
}
