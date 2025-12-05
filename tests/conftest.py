"""Pytest configuration and shared fixtures."""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_inventory():
    """Sample Ansible inventory for testing."""
    return {
        "all": {
            "children": {
                "kube_control_plane": {
                    "hosts": {
                        "master1": {
                            "ansible_host": "192.168.1.10",
                            "ansible_user": "ubuntu",
                            "ansible_ssh_private_key_file": "~/.ssh/id_rsa"
                        }
                    }
                },
                "kube_node": {
                    "hosts": {
                        "worker1": {
                            "ansible_host": "192.168.1.11",
                            "ansible_user": "ubuntu",
                            "ansible_ssh_private_key_file": "~/.ssh/id_rsa",
                            "gpu_enabled": True
                        }
                    }
                }
            }
        }
    }


@pytest.fixture
def inventory_file(temp_dir, sample_inventory):
    """Create a temporary inventory file."""
    inv_file = temp_dir / "inventory.yml"
    with open(inv_file, 'w') as f:
        yaml.dump(sample_inventory, f)
    return str(inv_file)


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "blueprint_version": "v2.2.1",
        "nodes": [
            {
                "hostname": "master1",
                "ip": "192.168.1.10",
                "username": "ubuntu",
                "is_master": True,
                "has_gpu": False
            }
        ],
        "gpu_count": 1,
        "memory_limit": "16Gi"
    }


@pytest.fixture
def config_file(temp_dir, sample_config):
    """Create a temporary config file."""
    config_file = temp_dir / "config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(sample_config, f)
    return str(config_file)


@pytest.fixture
def mock_ssh_key(tmp_path):
    """Create a mock SSH key file."""
    ssh_key = tmp_path / "id_rsa"
    ssh_key.write_text("mock ssh key")
    ssh_key.chmod(0o600)
    return str(ssh_key)


@pytest.fixture
def mock_secrets_dir(tmp_path):
    """Create a mock secrets directory."""
    secrets_dir = tmp_path / ".phaser"
    secrets_dir.mkdir()
    return secrets_dir


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for testing."""
    with patch('subprocess.run') as mock:
        yield mock


@pytest.fixture
def mock_asyncio_subprocess():
    """Mock asyncio subprocess for testing."""
    with patch('asyncio.create_subprocess_exec') as mock:
        yield mock

