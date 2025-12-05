# Test Suite Documentation

## Overview

Comprehensive test suite for the NVIDIA RAG Blueprint Installer, covering both CLI and WebUI components.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── cli/
│   ├── test_validators_*.py # Validator tests
│   ├── test_utils_*.py      # Utility tests
│   └── test_executors_*.py  # Executor tests
└── webui/
    ├── test_agents_*.py     # Agent tests
    └── test_api_endpoints.py # API endpoint tests
```

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# CLI tests only
pytest tests/cli/

# WebUI tests only
pytest tests/webui/

# Specific test file
pytest tests/cli/test_validators_system.py

# Specific test function
pytest tests/cli/test_validators_system.py::TestSystemValidator::test_check_python_version_pass
```

### Run with Coverage

```bash
pytest --cov=cli --cov=webui --cov-report=html
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Marked Tests

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## Test Categories

### Unit Tests

Fast, isolated tests that test individual components:
- Validators (system, hardware, network, API keys)
- Utilities (config, secrets)
- Executors (Ansible, Helm, kubectl)
- Agents (base, installation, management, configuration)
- API endpoints

### Integration Tests

Tests that verify interactions between components:
- End-to-end installation flows
- Agent task execution
- WebSocket communication
- Full API workflows

## Writing Tests

### Test Naming Convention

- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test functions: `test_<function_name>_<condition>`

### Example Test

```python
import pytest
from cli.validators.system import SystemValidator

class TestSystemValidator:
    """Test SystemValidator class."""
    
    def test_check_python_version_pass(self):
        """Test Python version check passes for Python 3.8+."""
        validator = SystemValidator()
        result = validator.check_python_version()
        
        assert result["status"] == "pass"
        assert "Python" in result["message"]
```

### Using Fixtures

```python
def test_with_fixture(sample_config, temp_dir):
    """Test using fixtures."""
    # Use sample_config and temp_dir fixtures
    pass
```

### Async Tests

```python
@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await some_async_function()
    assert result is not None
```

### Mocking

```python
from unittest.mock import patch, MagicMock

@patch('subprocess.run')
def test_with_mock(mock_run):
    """Test with mocked subprocess."""
    mock_run.return_value = MagicMock(returncode=0)
    # Test code here
```

## Test Coverage Goals

- **CLI Components**: >80% coverage
- **WebUI Components**: >80% coverage
- **Critical Paths**: >90% coverage

## Continuous Integration

Tests should be run:
- Before every commit
- In CI/CD pipeline
- Before releases

## Troubleshooting

### Import Errors

If you get import errors, make sure the project root is in Python path:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Async Test Issues

Make sure `pytest-asyncio` is installed and `asyncio_mode = auto` is set in `pytest.ini`.

### Mock Issues

Ensure you're patching the correct import path. Use the path where the function is used, not where it's defined.

## Adding New Tests

1. Create test file in appropriate directory
2. Follow naming conventions
3. Use fixtures from `conftest.py`
4. Add appropriate markers
5. Ensure tests are fast and isolated
6. Update this README if adding new test categories

