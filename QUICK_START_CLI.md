# CLI Wizard - Quick Start Guide

## 🚀 Get Started in 2 Minutes

### 1. Activate Virtual Environment

```bash
cd /Users/mike/phaser
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Minimal dependencies (for testing)
pip install typer rich pyyaml requests

# Or full dependencies
pip install -r requirements-cli.txt
```

### 3. Test the CLI

```bash
# Show help
python3 phaser.py --help

# Show version
python3 phaser.py --version
```

### 4. Run Installation Wizard

```bash
# Interactive wizard (dry run)
python3 phaser.py install interactive --dry-run

# Or full installation
python3 phaser.py install interactive
```

## 📋 Common Commands

### Installation

```bash
# Interactive installation wizard
python3 phaser.py install interactive

# Install from config file
python3 phaser.py install from-config my-config.yaml

# Dry run (validate without installing)
python3 phaser.py install interactive --dry-run
```

### Validation

```bash
# Pre-installation checks
python3 phaser.py validate preflight

# All validation checks
python3 phaser.py validate all
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
```

### Configuration

```bash
# Generate config template
python3 phaser.py config generate --output my-config.yaml

# Show current config
python3 phaser.py config show

# Validate config file
python3 phaser.py config validate my-config.yaml
```

### Diagnostics

```bash
# Pre-installation diagnostics
python3 phaser.py diagnose preflight

# Export diagnostic report
python3 phaser.py diagnose preflight --export report.json
```

## 🎯 Installation Wizard Flow

When you run `python3 phaser.py install interactive`, the wizard will:

1. **Welcome Screen** - Overview of installation process
2. **Prerequisites Check** - Validates system requirements
3. **API Key Configuration** - Sets up NVIDIA, OpenAI, Anthropic keys
4. **Node Configuration** - Configures Kubernetes nodes
5. **Blueprint Configuration** - Sets blueprint version and resources
6. **Review & Confirm** - Reviews configuration before installation
7. **Installation Execution** - Runs Ansible playbooks (when implemented)

## 📁 Configuration Files

- **User Config**: `~/.phaser/config.yaml`
- **Secrets**: `~/.phaser/secrets.yaml` (encrypted, 600 permissions)
- **Project Config**: `phaser-config.yaml` (in project directory)

## 🔧 Troubleshooting

### Module Not Found

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Install dependencies
pip install typer rich pyyaml requests
```

### Permission Errors

```bash
# Make scripts executable
chmod +x phaser.py cli/main.py
```

### SSH Key Not Found

The validation may fail if your SSH key is in a different location. You can:
- Create a key: `ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa`
- Or continue anyway (the wizard will prompt you)

## 📚 Next Steps

1. **Test the CLI**: Run `python3 phaser.py --help`
2. **Try the wizard**: Run `python3 phaser.py install interactive --dry-run`
3. **Set API keys**: Run `python3 phaser.py keys set nvidia`
4. **Generate config**: Run `python3 phaser.py config generate`

## 📖 Documentation

- **Full Assessment**: `docs/CLI_WIZARD_ASSESSMENT.md`
- **Strategy Document**: `docs/CLI_WIZARD_STRATEGY.md`
- **CLI README**: `cli/README.md`
- **Prototype Summary**: `CLI_PROTOTYPE_SUMMARY.md`

## ✅ What's Working

- ✅ CLI framework and commands
- ✅ Interactive installation wizard
- ✅ System validation
- ✅ API key management
- ✅ Configuration management
- ✅ Diagnostics framework

## ⏳ Coming Soon

- ⏳ Ansible integration
- ⏳ Hardware validation
- ⏳ Network validation
- ⏳ Installation execution
- ⏳ Progress tracking

---

**Ready to install?** Run `python3 phaser.py install interactive` and follow the prompts!

