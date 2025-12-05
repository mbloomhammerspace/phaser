# CLI Wizard - Quick Start

## Installation

Install the required dependencies:

```bash
pip3 install -r requirements-cli.txt
```

Or install minimal dependencies for testing:

```bash
pip3 install typer rich pyyaml requests
```

## Usage

### Basic Commands

```bash
# Show help
python3 phaser.py --help

# Show version
python3 phaser.py --version

# Run installation wizard
python3 phaser.py install

# Run validation checks
python3 phaser.py validate preflight

# Run diagnostics
python3 phaser.py diagnose preflight

# Manage API keys
python3 phaser.py keys set nvidia
python3 phaser.py keys list
python3 phaser.py keys test

# Configuration management
python3 phaser.py config show
python3 phaser.py config generate
python3 phaser.py config validate config.yaml
```

### Installation Wizard

The interactive installation wizard guides you through:

1. **Prerequisites Check** - Validates system requirements
2. **API Key Configuration** - Sets up NVIDIA, OpenAI, and Anthropic keys
3. **Node Configuration** - Configures Kubernetes nodes
4. **Blueprint Configuration** - Sets blueprint version and resources
5. **Review & Confirm** - Reviews configuration before installation
6. **Installation Execution** - Runs Ansible playbooks

```bash
# Interactive wizard
python3 phaser.py install

# Use existing config
python3 phaser.py install --config my-config.yaml

# Dry run (validate without installing)
python3 phaser.py install --dry-run
```

### API Key Management

```bash
# Set NVIDIA API key (required)
python3 phaser.py keys set nvidia

# Set OpenAI API key (optional)
python3 phaser.py keys set openai

# List configured keys
python3 phaser.py keys list

# Test API keys
python3 phaser.py keys test

# Remove a key
python3 phaser.py keys remove nvidia
```

### Validation

```bash
# Pre-installation checks
python3 phaser.py validate preflight

# Post-installation checks
python3 phaser.py validate post-install

# All checks
python3 phaser.py validate all --inventory inventory.yml
```

### Diagnostics

```bash
# Pre-installation diagnostics
python3 phaser.py diagnose preflight

# Installation diagnostics
python3 phaser.py diagnose installation

# Cluster diagnostics
python3 phaser.py diagnose cluster

# Export diagnostic report
python3 phaser.py diagnose preflight --export report.json
```

## Project Structure

```
cli/
├── main.py              # CLI entry point
├── commands/            # Command modules
│   ├── install.py      # Installation command
│   ├── validate.py     # Validation command
│   ├── diagnose.py     # Diagnostics command
│   ├── config.py       # Config management
│   └── keys.py         # API key management
├── wizard/             # Interactive wizards
│   └── installer.py    # Installation wizard
├── validators/         # Validation modules
│   ├── system.py       # System validation
│   ├── hardware.py     # Hardware validation
│   ├── network.py      # Network validation
│   └── api_keys.py     # API key validation
├── executors/          # Execution modules (TODO)
│   ├── ansible.py      # Ansible execution
│   ├── helm.py         # Helm execution
│   └── kubectl.py      # kubectl execution
├── diagnostics/        # Diagnostic modules
│   ├── preflight.py    # Pre-installation diagnostics
│   ├── installation.py # Installation diagnostics
│   └── post_install.py # Post-installation diagnostics
└── utils/              # Utilities
    ├── config.py       # Config file management
    └── secrets.py      # Secret management
```

## Configuration

Configuration files are stored in:
- **User config**: `~/.phaser/config.yaml`
- **Secrets**: `~/.phaser/secrets.yaml` (encrypted, 600 permissions)
- **Project config**: `phaser-config.yaml` (in project directory)

## Development

### Running Tests

```bash
# Test CLI structure
python3 phaser.py --help

# Test installation wizard (dry run)
python3 phaser.py install --dry-run

# Test validation
python3 phaser.py validate preflight
```

### Adding New Commands

1. Create command module in `cli/commands/`
2. Import and register in `cli/main.py`
3. Add help text and options

### Adding New Validators

1. Create validator class in `cli/validators/`
2. Implement `validate_all()` method
3. Return list of check results

## Status

**Current Status**: Prototype - Core structure and basic commands implemented

**Implemented**:
- ✅ CLI framework with Typer
- ✅ Command structure (install, validate, diagnose, config, keys)
- ✅ Installation wizard (interactive flow)
- ✅ System validation
- ✅ API key management
- ✅ Configuration management
- ✅ Basic diagnostics

**In Progress**:
- ⏳ Ansible execution integration
- ⏳ Hardware validation
- ⏳ Network validation
- ⏳ Installation execution
- ⏳ Post-installation verification

**Planned**:
- 📋 Helm integration
- 📋 kubectl integration
- 📋 Comprehensive error handling
- 📋 Progress tracking
- 📋 Resume capability

## Next Steps

1. Install full dependencies: `pip3 install -r requirements-cli.txt`
2. Test the CLI: `python3 phaser.py --help`
3. Run installation wizard: `python3 phaser.py install --dry-run`
4. Integrate with existing Ansible playbooks
5. Add hardware and network validation
6. Implement installation execution

