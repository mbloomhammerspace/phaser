# CLI Wizard Strategy - Executive Summary

## Overview

This document provides a strategic overview for building a standalone CLI wizard to replace Cursor-dependent installation of NVIDIA RAG Blueprint on NVIDIA hardware.

## Current State

**What Exists**:
- Ansible playbooks for Kubernetes, GPU Operator, and RAG Blueprint deployment
- Preflight discovery tools for hardware detection
- AI-powered error handling (requires OpenAI API key)
- Helm charts and configuration files
- Documentation and guides

**What's Missing**:
- Standalone CLI tool (install.sh is archived)
- Centralized API key management
- Interactive installation wizard
- Comprehensive validation framework
- Unified diagnostic system

## Strategic Goals

1. **Eliminate Cursor Dependency**: Enable installation without Cursor IDE
2. **Simplify Installation**: Guide users through complex multi-step process
3. **Improve Diagnostics**: Help users identify and resolve issues
4. **Secure Key Management**: Handle API keys securely and validate them

## Key Requirements

### 1. Installation Orchestration
- Execute Ansible playbooks in sequence
- Handle errors gracefully with recovery
- Provide real-time progress feedback
- Support resume for interrupted installations

### 2. Requirements Validation
**Pre-Installation Checks**:
- System requirements (Python, Ansible, SSH)
- Hardware requirements (CPU, RAM, storage, GPU)
- Network connectivity
- Software prerequisites on target nodes

**Post-Installation Verification**:
- Kubernetes cluster health
- Service availability
- Resource allocation
- API endpoint accessibility

### 3. API Key Management
**Required Keys**:
- **NVIDIA API Key** (Required): For NGC registry and NVIDIA services
- **OpenAI API Key** (Optional): For AI-powered diagnostics
- **Anthropic API Key** (Optional): For alternative AI services

**Key Features**:
- Secure masked input
- Format validation
- Connectivity testing
- Secure storage (env vars, encrypted config, K8s secrets)

### 4. Configuration Wizard
- Interactive node discovery and configuration
- SSH key and access configuration
- Blueprint version and component selection
- Resource allocation (CPU, memory, GPU)
- Storage configuration
- Network settings

### 5. Diagnostic System
- Pre-installation system health checks
- Real-time installation monitoring
- Post-installation service verification
- Troubleshooting guidance with solutions

## Technical Approach

### Recommended Stack
- **CLI Framework**: Typer (modern, type-safe)
- **UI Enhancement**: Rich (beautiful terminal output)
- **Prompts**: Inquirer (interactive questions)
- **Execution**: Ansible-runner (Ansible wrapper)
- **Validation**: Custom modules + existing preflight tools

### Project Structure
```
cli/
├── commands/        # CLI commands (install, validate, diagnose)
├── wizard/          # Interactive wizards
├── validators/      # Validation modules
├── executors/       # Ansible/Helm/kubectl execution
├── diagnostics/     # Diagnostic tools
└── utils/          # Utilities (config, secrets, logging)
```

## Implementation Phases

### Phase 1: Foundation (2 weeks)
- CLI framework setup
- Basic commands structure
- Configuration management
- Basic validation

### Phase 2: Core Installation (2 weeks)
- Installation wizard
- Ansible integration
- Progress tracking
- Error handling

### Phase 3: Validation & Diagnostics (2 weeks)
- Comprehensive validation
- Diagnostic tools
- Health checks
- Troubleshooting integration

### Phase 4: API Key Management (1 week)
- Key wizard
- Validation
- Secure storage
- K8s secret integration

### Phase 5: Polish & Documentation (1 week)
- UX improvements
- Documentation
- Testing
- Bug fixes

**Total Timeline**: 8 weeks

## User Experience Flow

```
1. Welcome & Prerequisites Check
   ↓
2. System Validation
   ↓
3. API Key Configuration (NVIDIA required, others optional)
   ↓
4. Node Configuration (interactive or file-based)
   ↓
5. Blueprint Configuration
   ↓
6. Review & Confirm
   ↓
7. Installation Execution (with progress tracking)
   ↓
8. Post-Installation Verification & Access Info
```

## Command Structure

```bash
# Main commands
phaser install [OPTIONS]          # Installation wizard
phaser validate [OPTIONS]         # Run validation checks
phaser diagnose [TYPE] [OPTIONS]  # Run diagnostics
phaser config [COMMAND]           # Config management
phaser keys [COMMAND]             # API key management

# Examples
phaser install --interactive      # Interactive wizard
phaser install --config config.yaml  # Use existing config
phaser validate --preflight        # Pre-installation checks
phaser diagnose cluster           # Cluster diagnostics
phaser keys set nvidia            # Set NVIDIA API key
```

## Key Features

### 1. Interactive Wizard
- Step-by-step guidance
- Clear prompts and validation
- Configuration review before execution
- Estimated installation time

### 2. Comprehensive Validation
- Pre-installation system checks
- Hardware requirements verification
- Network connectivity testing
- Post-installation service verification

### 3. Secure API Key Management
- Masked input for security
- Format validation
- Connectivity testing
- Multiple storage options

### 4. Real-Time Progress
- Progress bars
- Step-by-step status
- Error detection and reporting
- Log aggregation

### 5. Diagnostic Tools
- Pre-installation diagnostics
- Installation monitoring
- Post-installation health checks
- Troubleshooting suggestions

## Success Metrics

- **Installation Success Rate**: >95%
- **Time to Install**: <30 minutes
- **Manual Intervention**: <5% of installations
- **User Satisfaction**: Positive feedback on ease of use

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Ansible execution complexity | Medium | Use ansible-runner wrapper |
| API key security | High | Follow security best practices |
| Cross-platform compatibility | Medium | Test on multiple OS |
| Configuration errors | Medium | Comprehensive validation |

## Recommendations

### Immediate Actions
1. ✅ **Assessment Complete** - This document
2. **Create CLI Structure** - Set up project framework
3. **Implement Core Commands** - Install, validate, diagnose
4. **Build Configuration Wizard** - Interactive setup

### Short-Term (1-2 months)
- API key management
- Progress reporting
- Error handling improvements
- User documentation

### Long-Term (3-6 months)
- AI-powered diagnostics enhancement
- Configuration templates
- Update/upgrade support
- Multi-cloud extensions

## Dependencies

**Required**:
- Python 3.8+
- Ansible 2.12+
- Access to NVIDIA hardware for testing
- Test Kubernetes clusters
- API keys for validation

**Python Packages**:
- typer, rich, inquirer (CLI)
- ansible, ansible-runner (execution)
- kubernetes, pyyaml (operations)
- paramiko, psutil (validation)

## Conclusion

Building a CLI wizard is **highly feasible** and will provide significant value:

✅ **Technical Feasibility**: High - All components can be built or integrated  
✅ **User Value**: High - Simplifies complex installation  
✅ **Maintenance**: Medium - Requires updates with blueprint changes  
✅ **Risk Level**: Low - Incremental development with backward compatibility  

**Recommended Approach**: Build incrementally, starting with core functionality, gathering user feedback, and iterating on improvements.

## Next Steps

1. **Review Assessment**: Review detailed assessment in `CLI_WIZARD_ASSESSMENT.md`
2. **Approve Approach**: Confirm technical approach and timeline
3. **Allocate Resources**: Assign developer(s) and testing resources
4. **Begin Phase 1**: Start with foundation and CLI framework setup

