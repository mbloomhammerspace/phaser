# Web UI - Quick Start Guide

## 🚀 Getting Started

### 1. Install Dependencies

```bash
cd /Users/mike/phaser
source venv/bin/activate
pip install -r webui/requirements.txt
```

### 2. Start the Web Server

```bash
python3 webui/run.py
```

Or:

```bash
cd webui
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access the Web UI

Open your browser and navigate to:
```
http://localhost:8000
```

## 📋 Features

### Installation Wizard
- Step-by-step installation guide
- Prerequisites checking
- API key configuration
- Node configuration
- Blueprint configuration
- Review and confirm
- Real-time installation progress (WebSocket)

### Validation
- Pre-installation system checks
- Formatted results display
- Summary statistics

### API Key Management
- Set NVIDIA, OpenAI, and Anthropic API keys
- Test API keys
- List configured keys
- Remove keys

### Configuration Management
- Load configuration
- Generate template
- Edit configuration (JSON)
- Validate configuration
- Save configuration

### Diagnostics
- Pre-installation diagnostics
- System health checks
- Diagnostic reports

## 🎨 UI Features

- **Modern Bootstrap 5 Design**
- **Responsive Layout**
- **Real-time Updates** via WebSocket
- **Toast Notifications**
- **Progress Tracking**
- **Tabbed Interface**

## 🔧 API Endpoints

### Health
- `GET /api/health` - Health check

### Validation
- `POST /api/validate/preflight` - Run pre-installation validation
- `GET /api/validate/system` - Get system validation results

### API Keys
- `POST /api/keys/set` - Set an API key
- `GET /api/keys/list` - List configured keys
- `POST /api/keys/test` - Test an API key
- `DELETE /api/keys/{key_type}` - Remove an API key

### Configuration
- `GET /api/config` - Get current configuration
- `POST /api/config` - Save configuration
- `GET /api/config/template` - Get configuration template
- `POST /api/config/validate` - Validate configuration

### Installation
- `POST /api/install/validate` - Validate installation config
- `POST /api/install/start` - Start installation

### WebSocket
- `ws://localhost:8000/ws` - General WebSocket
- `ws://localhost:8000/ws/install` - Installation progress stream

## 📁 Project Structure

```
webui/
├── api/
│   └── main.py          # FastAPI backend
├── static/
│   ├── css/
│   │   └── style.css    # Custom styles
│   └── js/
│       └── app.js       # Frontend JavaScript
├── templates/
│   └── index.html       # Main HTML template
├── requirements.txt     # Python dependencies
└── run.py               # Server startup script
```

## 🛠️ Development

### Running in Development Mode

```bash
# Auto-reload on code changes
python3 webui/run.py
```

### Testing API Endpoints

```bash
# Health check
curl http://localhost:8000/api/health

# Run validation
curl -X POST http://localhost:8000/api/validate/preflight \
  -H "Content-Type: application/json" \
  -d '{}'

# List API keys
curl http://localhost:8000/api/keys/list
```

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Use a different port
uvicorn api.main:app --port 8001
```

### Module Not Found

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Install dependencies
pip install -r webui/requirements.txt
```

### CORS Issues

The API is configured to allow all origins in development. For production, update the CORS settings in `webui/api/main.py`.

## 📝 Next Steps

1. **Integrate Ansible Execution** - Connect to actual installation process
2. **Add Hardware Validation** - SSH to nodes and check resources
3. **Enhance Progress Tracking** - Real-time updates from Ansible
4. **Add Error Handling** - Better error messages and recovery
5. **Add Authentication** - Secure the web UI

## ✅ Status

- ✅ FastAPI backend with all endpoints
- ✅ Modern web UI with Bootstrap 5
- ✅ Installation wizard flow
- ✅ Validation UI
- ✅ API key management UI
- ✅ Configuration management UI
- ✅ WebSocket support for real-time updates
- ⏳ Ansible integration (next step)
- ⏳ Hardware validation (next step)

---

**Ready to use!** Start the server and open `http://localhost:8000` in your browser.

