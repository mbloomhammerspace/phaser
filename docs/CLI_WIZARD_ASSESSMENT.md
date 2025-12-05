# CLI Wizard Assessment for NVIDIA Blueprint Installation

## Executive Summary

This document provides a comprehensive assessment of building a standalone CLI wizard interface to replace the current Cursor-dependent installation process for NVIDIA RAG Blueprint deployment on NVIDIA hardware. The wizard will guide users through installation, requirements validation, API key configuration, and diagnostic capabilities.

## Current State Analysis

### Current Installation Process

The project currently relies on:
1. **Ansible Playbooks** (`playbooks/` directory):
   - `01-kubespray.yml` - Kubernetes cluster deployment
   - `03-gpu-operator.yml` - NVIDIA GPU Operator installation
   - `04-rag-blueprint.yml` - RAG Blueprint deployment
   - `05-validate.yml` - Post-installation validation
   - `06-hammerspace-tier0.yml` - Storage configuration

2. **Installation Scripts** (referenced but not present):
   - `install.sh` - Main installer (currently in archive)
   - `utils/preflight.sh` - Hardware discovery
   - `utils/preflight_checker.py` - Python-based preflight checks
   - `utils/ai_debugger.py` - AI-powered error handling

3. **Configuration Files**:
   - `rag-blueprint-values.yaml` - Helm values for RAG blueprint
   - `charts/` - Helm charts for various components
   - Inventory files (YAML format) for Ansible

### Current Dependencies

**Python Dependencies** (from documentation):
- `ansible` >= 2.12.0
- `kubernetes` >= 28.0.0
- `PyYAML` >= 6.0
- `jinja2` >= 3.1.0
- `requests` >= 2.28.0
- `openai` >= 1.0.0 (for AI error handling)

**System Requirements**:
- Python 3.8+
- Git
- SSH client
- kubectl (post-installation)
- Helm (for blueprint deployment)
- Ansible (for cluster deployment)

**API Keys Currently Used**:
- `OPENAI_API_KEY` - For AI-powered error handling (optional)
- `NVIDIA_API_KEY` / `NGC_API_KEY` - For NVIDIA services and container registry
- `ANTHROPIC_API_KEY` - Referenced in some workflows (optional)

## CLI Wizard Requirements Assessment

### 1. Core Functionality Requirements

#### 1.1 Installation Orchestration
**Current State**: Ansible playbooks orchestrate the installation
**Wizard Needs**:
- Execute Ansible playbooks in correct sequence
- Handle playbook execution errors gracefully
- Provide real-time progress feedback
- Support rollback on failure
- Resume capability for interrupted installations

**Implementation Approach**:
- Python-based CLI using `click` or `typer` for command-line interface
- Subprocess management for Ansible execution
- Progress tracking via Ansible callbacks
- State management (JSON/YAML) for resume capability

#### 1.2 Requirements Validation
**Current State**: Preflight checker exists but may need enhancement
**Wizard Needs**:
- Pre-installation system checks:
  - Python version verification
  - Ansible installation check
  - SSH key availability and permissions
  - Network connectivity to target nodes
  - Target node prerequisites (Python, packages)
  - GPU detection and driver verification
  - Storage availability
  - Kubernetes cluster readiness (if upgrading)
- Hardware requirements validation:
  - CPU cores per node
  - RAM per node
  - Storage per node
  - GPU availability and specifications
- Software requirements validation:
  - OS compatibility
  - Container runtime (containerd/docker)
  - Kubernetes version compatibility

**Implementation Approach**:
- Extend `utils/preflight_checker.py`
- Add comprehensive validation modules
- Create validation report generator
- Interactive prompts for missing requirements

#### 1.3 API Key Management
**Current State**: Keys are referenced but not centrally managed
**Wizard Needs**:
- Secure key input (masked prompts)
- Key validation:
  - OpenAI API key format validation
  - NVIDIA API key format validation
  - Anthropic API key format validation (if needed)
- Key storage options:
  - Environment variables
  - Encrypted local config file
  - Kubernetes secrets (post-installation)
- Key testing:
  - Verify API key validity before proceeding
  - Test API connectivity

**Implementation Approach**:
- Use `getpass` for secure input
- API key validation functions
- Config file management with encryption (optional)
- Integration with Kubernetes secret creation

#### 1.4 Configuration Management
**Current State**: Configuration scattered across multiple files
**Wizard Needs**:
- Interactive configuration wizard:
  - Node inventory collection
  - SSH key path and username
  - Blueprint version selection
  - Resource allocation (CPU, memory, GPU)
  - Storage configuration
  - Network settings
- Configuration file generation:
  - Ansible inventory file
  - Helm values files
  - Environment variable files
- Configuration validation:
  - Syntax checking
  - Resource availability verification
  - Network connectivity testing

**Implementation Approach**:
- Interactive prompts using `inquirer` or `rich`
- Template-based file generation
- YAML validation using `ruamel.yaml` or `pyyaml`
- Configuration schema validation

#### 1.5 Diagnostic and Troubleshooting
**Current State**: AI debugger exists but may need enhancement
**Wizard Needs**:
- Pre-installation diagnostics:
  - System health checks
  - Network diagnostics
  - Storage diagnostics
  - GPU diagnostics
- Installation diagnostics:
  - Real-time error detection
  - Log aggregation
  - Error categorization
- Post-installation diagnostics:
  - Service health checks
  - Resource utilization
  - Performance metrics
- Troubleshooting guidance:
  - Common issue detection
  - Solution suggestions
  - AI-powered analysis (optional, requires API keys)

**Implementation Approach**:
- Extend `utils/ai_debugger.py`
- Create diagnostic modules
- Log aggregation and analysis
- Integration with existing error handler

### 2. Technical Architecture

#### 2.1 CLI Framework Selection

**Recommended: Typer + Rich**
- **Typer**: Modern Python CLI framework built on Click
  - Type hints for automatic validation
  - Easy command structure
  - Built-in help generation
- **Rich**: Beautiful terminal output
  - Progress bars
  - Tables and formatted output
  - Syntax highlighting
  - Spinner animations

**Alternative: Click**
- More mature and widely used
- Extensive plugin ecosystem
- Slightly more verbose syntax

#### 2.2 Project Structure

```
phaser/
├── cli/
│   ├── __init__.py
│   ├── main.py              # CLI entry point
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── install.py       # Installation command
│   │   ├── validate.py      # Validation command
│   │   ├── diagnose.py      # Diagnostics command
│   │   ├── config.py        # Configuration management
│   │   └── keys.py          # API key management
│   ├── wizard/
│   │   ├── __init__.py
│   │   ├── installer.py     # Installation wizard
│   │   ├── config_wizard.py # Configuration wizard
│   │   └── key_wizard.py    # API key wizard
│   ├── validators/
│   │   ├── __init__.py
│   │   ├── system.py        # System requirements
│   │   ├── hardware.py      # Hardware validation
│   │   ├── network.py       # Network validation
│   │   └── api_keys.py      # API key validation
│   ├── executors/
│   │   ├── __init__.py
│   │   ├── ansible.py       # Ansible execution
│   │   ├── helm.py          # Helm execution
│   │   └── kubectl.py       # kubectl execution
│   ├── diagnostics/
│   │   ├── __init__.py
│   │   ├── preflight.py     # Pre-installation checks
│   │   ├── installation.py  # Installation monitoring
│   │   └── post_install.py  # Post-installation checks
│   └── utils/
│       ├── __init__.py
│       ├── config.py        # Config file management
│       ├── secrets.py        # Secret management
│       └── logging.py       # Logging utilities
├── templates/
│   ├── inventory.j2         # Ansible inventory template
│   ├── values.j2            # Helm values template
│   └── config.j2            # Config file template
└── requirements-cli.txt     # CLI-specific dependencies
```

#### 2.3 Key Dependencies

**Core CLI Dependencies**:
```python
typer>=0.9.0          # CLI framework
rich>=13.0.0          # Terminal formatting
inquirer>=3.1.0       # Interactive prompts
pyyaml>=6.0           # YAML handling
ruamel.yaml>=0.18.0   # Advanced YAML (optional)
click>=8.1.0          # CLI utilities (typer dependency)
```

**Validation Dependencies**:
```python
psutil>=5.9.0         # System information
netifaces>=0.11.0     # Network interface info
requests>=2.28.0      # API testing
paramiko>=3.0.0       # SSH connectivity testing
```

**Execution Dependencies**:
```python
ansible>=2.12.0       # Ansible execution
ansible-runner>=2.3.0 # Ansible execution wrapper
kubernetes>=28.0.0     # Kubernetes API
pyhelm>=3.0.0         # Helm operations (or subprocess)
```

**Security Dependencies**:
```python
cryptography>=41.0.0  # Encryption for secrets
keyring>=24.0.0      # Secure key storage (optional)
```

### 3. Implementation Phases

#### Phase 1: Foundation (Week 1-2)
**Goals**:
- Set up CLI framework structure
- Implement basic commands (install, validate, diagnose)
- Create configuration management system
- Implement basic validation framework

**Deliverables**:
- CLI entry point with basic commands
- Configuration file management
- Basic system validation
- Project structure

#### Phase 2: Core Installation (Week 3-4)
**Goals**:
- Implement installation wizard
- Integrate Ansible execution
- Add progress tracking
- Implement error handling

**Deliverables**:
- Interactive installation wizard
- Ansible playbook execution wrapper
- Progress reporting
- Basic error handling

#### Phase 3: Validation & Diagnostics (Week 5-6)
**Goals**:
- Comprehensive validation system
- Pre-installation diagnostics
- Post-installation verification
- Troubleshooting guidance

**Deliverables**:
- Complete validation framework
- Diagnostic tools
- Health check system
- Troubleshooting guide integration

#### Phase 4: API Key Management (Week 7)
**Goals**:
- API key wizard
- Key validation
- Secure storage
- Kubernetes secret integration

**Deliverables**:
- API key management commands
- Key validation system
- Secure storage implementation
- Kubernetes secret creation

#### Phase 5: Polish & Documentation (Week 8)
**Goals**:
- User experience improvements
- Comprehensive documentation
- Error message improvements
- Testing and bug fixes

**Deliverables**:
- User guide
- Developer documentation
- Error handling improvements
- Test suite

### 4. Key Features Specification

#### 4.1 Installation Wizard Flow

```
1. Welcome & Overview
   └─> Display installation overview
   └─> Check prerequisites

2. System Validation
   └─> Run preflight checks
   └─> Display validation results
   └─> Prompt to fix issues or continue

3. API Key Configuration
   └─> Prompt for NVIDIA API key (required)
   └─> Prompt for OpenAI API key (optional, for diagnostics)
   └─> Prompt for Anthropic API key (optional, if needed)
   └─> Validate keys
   └─> Store keys securely

4. Node Configuration
   └─> Discover nodes (interactive or file-based)
   └─> Configure SSH access
   └─> Assign node roles (master, worker, GPU worker)
   └─> Configure resource allocation

5. Blueprint Configuration
   └─> Select blueprint version
   └─> Configure component options
   └─> Set resource limits
   └─> Configure storage

6. Review & Confirm
   └─> Display configuration summary
   └─> Show estimated installation time
   └─> Confirm installation

7. Installation Execution
   └─> Generate configuration files
   └─> Execute installation steps
   └─> Monitor progress
   └─> Handle errors

8. Post-Installation
   └─> Verify installation
   └─> Display access information
   └─> Run health checks
   └─> Provide next steps
```

#### 4.2 Validation System

**Pre-Installation Checks**:
- [ ] Python 3.8+ installed
- [ ] Ansible 2.12+ installed
- [ ] SSH key exists and has correct permissions
- [ ] SSH connectivity to all nodes
- [ ] Target nodes have Python 3.8+
- [ ] Target nodes have required packages
- [ ] Network connectivity between nodes
- [ ] GPU detection (if GPU nodes specified)
- [ ] NVIDIA drivers (if GPU nodes specified)
- [ ] Storage availability
- [ ] DNS resolution
- [ ] Firewall rules
- [ ] API key validity (if provided)

**Post-Installation Checks**:
- [ ] Kubernetes cluster healthy
- [ ] All pods running
- [ ] GPU operator installed
- [ ] RAG services accessible
- [ ] Storage classes available
- [ ] Observability stack running
- [ ] API endpoints responding

#### 4.3 API Key Management

**Supported Keys**:
1. **NVIDIA API Key** (Required)
   - Format: `nvapi-*` or similar
   - Used for: NGC container registry, NVIDIA services
   - Validation: Test NGC API access

2. **OpenAI API Key** (Optional)
   - Format: `sk-*`
   - Used for: AI-powered error handling
   - Validation: Test OpenAI API access

3. **Anthropic API Key** (Optional)
   - Format: `sk-ant-*`
   - Used for: Alternative AI services (if configured)
   - Validation: Test Anthropic API access

**Storage Options**:
- Environment variables (`.env` file)
- Encrypted config file (`.phaser/config.yaml.enc`)
- Kubernetes secrets (post-installation)
- System keyring (optional, OS-dependent)

#### 4.4 Diagnostic Commands

**Pre-Installation Diagnostics**:
```bash
phaser diagnose preflight
  - System requirements check
  - Network connectivity test
  - Storage availability
  - GPU detection
  - Generate diagnostic report
```

**Installation Diagnostics**:
```bash
phaser diagnose installation
  - Check installation progress
  - View recent errors
  - Analyze logs
  - Get troubleshooting suggestions
```

**Post-Installation Diagnostics**:
```bash
phaser diagnose cluster
  - Cluster health check
  - Service status
  - Resource utilization
  - Performance metrics
  - Generate health report
```

### 5. User Experience Design

#### 5.1 Command Structure

```bash
# Main commands
phaser install [OPTIONS]          # Run installation wizard
phaser validate [OPTIONS]         # Run validation checks
phaser diagnose [TYPE] [OPTIONS]  # Run diagnostics
phaser config [COMMAND]           # Configuration management
phaser keys [COMMAND]             # API key management

# Installation options
phaser install --interactive      # Interactive wizard (default)
phaser install --config FILE      # Use existing config
phaser install --resume           # Resume interrupted installation
phaser install --dry-run          # Validate without installing

# Validation options
phaser validate --preflight       # Pre-installation checks
phaser validate --post-install    # Post-installation checks
phaser validate --all             # All checks

# Diagnostic options
phaser diagnose preflight         # Pre-installation diagnostics
phaser diagnose installation     # Installation diagnostics
phaser diagnose cluster          # Cluster diagnostics
phaser diagnose --export FILE    # Export diagnostic report
```

#### 5.2 Interactive Prompts

**Node Discovery**:
- Interactive: Prompt for each node (IP, hostname, role, GPU)
- File-based: Read from inventory file
- Auto-discovery: SSH scan and hardware detection

**API Key Input**:
- Masked input (password-style)
- Option to skip optional keys
- Validation feedback
- Option to test keys

**Configuration Review**:
- Formatted table display
- Edit capability before confirmation
- Estimated installation time
- Resource requirements summary

#### 5.3 Progress Reporting

**Installation Progress**:
- Progress bar for overall installation
- Step-by-step status updates
- Real-time log streaming (optional)
- Estimated time remaining
- Current operation description

**Error Reporting**:
- Clear error messages
- Error categorization (critical, warning, info)
- Suggested solutions
- Log file locations
- Support information

### 6. Security Considerations

#### 6.1 API Key Security
- Never log API keys
- Mask keys in all output
- Use secure input methods
- Encrypt stored keys (optional)
- Support for key rotation

#### 6.2 SSH Key Security
- Verify SSH key permissions
- Never expose private keys
- Support for SSH agent
- Option to use different keys per node

#### 6.3 Configuration Security
- Validate configuration before execution
- Sanitize user input
- Prevent command injection
- Secure temporary file handling

### 7. Testing Strategy

#### 7.1 Unit Tests
- Validation functions
- Configuration parsing
- API key validation
- Error handling

#### 7.2 Integration Tests
- Ansible execution
- Helm operations
- Kubernetes API interactions
- SSH connectivity

#### 7.3 End-to-End Tests
- Complete installation flow
- Error recovery
- Resume functionality
- Post-installation verification

### 8. Documentation Requirements

#### 8.1 User Documentation
- Quick start guide
- Installation guide
- Configuration reference
- Troubleshooting guide
- API key management guide

#### 8.2 Developer Documentation
- Architecture overview
- Contributing guide
- Extension points
- Testing guide

#### 8.3 CLI Help
- Comprehensive command help
- Example usage
- Configuration examples
- Common scenarios

### 9. Migration Strategy

#### 9.1 Backward Compatibility
- Support existing inventory files
- Support existing configuration files
- Maintain Ansible playbook compatibility
- Support existing Helm values

#### 9.2 Gradual Migration
- CLI wizard as optional enhancement
- Existing scripts continue to work
- CLI can call existing scripts
- Gradual feature migration

### 10. Success Metrics

#### 10.1 Installation Success Rate
- Target: >95% successful installations
- Track: Installation completion rate
- Monitor: Common failure points

#### 10.2 User Experience
- Target: <30 minutes to complete installation
- Track: Time to first successful installation
- Monitor: User feedback and issues

#### 10.3 Error Resolution
- Target: <5% installations require manual intervention
- Track: Error frequency and types
- Monitor: Diagnostic effectiveness

### 11. Risk Assessment

#### 11.1 Technical Risks
- **Ansible Execution Complexity**: Mitigation - Use ansible-runner for better control
- **API Key Management**: Mitigation - Follow security best practices
- **Cross-Platform Compatibility**: Mitigation - Test on multiple OS
- **Error Handling**: Mitigation - Comprehensive error categorization

#### 11.2 User Experience Risks
- **Complexity**: Mitigation - Clear wizard flow and documentation
- **Error Messages**: Mitigation - User-friendly error messages with solutions
- **Configuration Errors**: Mitigation - Validation before execution

### 12. Recommendations

#### 12.1 Immediate Actions
1. **Create CLI Project Structure**: Set up the directory structure and basic framework
2. **Implement Core Commands**: Start with install, validate, and diagnose commands
3. **Build Configuration Wizard**: Create interactive configuration collection
4. **Integrate Existing Tools**: Wrap existing preflight and validation tools

#### 12.2 Short-Term Enhancements
1. **API Key Management**: Implement secure key input and validation
2. **Progress Reporting**: Add real-time progress tracking
3. **Error Handling**: Improve error messages and recovery
4. **Documentation**: Create user and developer guides

#### 12.3 Long-Term Enhancements
1. **AI-Powered Diagnostics**: Enhance existing AI debugger integration
2. **Configuration Templates**: Pre-built configurations for common scenarios
3. **Update/Upgrade Support**: Support for updating existing installations
4. **Multi-Cloud Support**: Extend to cloud deployments

### 13. Estimated Effort

**Total Development Time**: 8 weeks (1 developer)

**Breakdown**:
- Phase 1 (Foundation): 2 weeks
- Phase 2 (Core Installation): 2 weeks
- Phase 3 (Validation & Diagnostics): 2 weeks
- Phase 4 (API Key Management): 1 week
- Phase 5 (Polish & Documentation): 1 week

**Dependencies**:
- Access to NVIDIA hardware for testing
- Test Kubernetes clusters
- API keys for validation testing

### 14. Conclusion

Building a CLI wizard for NVIDIA Blueprint installation is feasible and will significantly improve the user experience. The assessment shows that:

1. **Technical Feasibility**: High - All required components exist or can be built
2. **User Value**: High - Simplifies complex installation process
3. **Maintenance**: Medium - Requires ongoing updates with blueprint changes
4. **Risk Level**: Low - Can be built incrementally with backward compatibility

The recommended approach is to build the CLI wizard incrementally, starting with core functionality and gradually adding advanced features. This allows for early user feedback and iterative improvement.

