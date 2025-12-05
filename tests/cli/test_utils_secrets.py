"""Tests for secret manager."""

import pytest
import yaml
from pathlib import Path
from unittest.mock import patch
from cli.utils.secrets import SecretManager


class TestSecretManager:
    """Test SecretManager class."""
    
    def test_set_and_get_key(self, tmp_path):
        """Test setting and getting a key."""
        with patch('cli.utils.secrets.Path.home', return_value=tmp_path):
            manager = SecretManager()
            manager.set_key("nvidia", "test-key-value")
            
            key_value = manager.get_key("nvidia")
            assert key_value == "test-key-value"
    
    def test_get_key_from_env(self, tmp_path, monkeypatch):
        """Test getting key from environment variable."""
        monkeypatch.setenv("NVIDIA_API_KEY", "env-key-value")
        
        with patch('cli.utils.secrets.Path.home', return_value=tmp_path):
            manager = SecretManager()
            key_value = manager.get_key("nvidia")
            assert key_value == "env-key-value"
    
    def test_remove_key(self, tmp_path):
        """Test removing a key."""
        with patch('cli.utils.secrets.Path.home', return_value=tmp_path):
            manager = SecretManager()
            manager.set_key("nvidia", "test-key")
            manager.remove_key("nvidia")
            
            key_value = manager.get_key("nvidia")
            assert key_value is None
    
    def test_list_keys(self, tmp_path):
        """Test listing keys."""
        with patch('cli.utils.secrets.Path.home', return_value=tmp_path):
            manager = SecretManager()
            manager.set_key("nvidia", "nvidia-key")
            manager.set_key("openai", "openai-key")
            
            keys = manager.list_keys()
            assert "nvidia" in keys
            assert "openai" in keys
            # Values should be masked
            assert keys["nvidia"] == "***"
    
    def test_secrets_file_permissions(self, tmp_path):
        """Test that secrets file has correct permissions."""
        with patch('cli.utils.secrets.Path.home', return_value=tmp_path):
            manager = SecretManager()
            manager.set_key("nvidia", "test-key")
            
            secrets_file = tmp_path / ".phaser" / "secrets.yaml"
            assert secrets_file.exists()
            # Check permissions (should be 0o600)
            assert oct(secrets_file.stat().st_mode)[-3:] == "600"

