"""Secret/API key management."""

import os
from pathlib import Path
from typing import Optional
import yaml


class SecretManager:
    """Manages API keys and secrets."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".phaser"
        self.secrets_file = self.config_dir / "secrets.yaml"
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def set_key(self, key_type: str, key_value: str):
        """Store an API key."""
        secrets = self._load_secrets()
        secrets[key_type] = key_value
        self._save_secrets(secrets)
    
    def get_key(self, key_type: str) -> Optional[str]:
        """Get an API key."""
        # First check environment variables
        env_key = os.getenv(f"{key_type.upper()}_API_KEY")
        if env_key:
            return env_key
        
        # Then check secrets file
        secrets = self._load_secrets()
        return secrets.get(key_type)
    
    def remove_key(self, key_type: str):
        """Remove an API key."""
        secrets = self._load_secrets()
        if key_type in secrets:
            del secrets[key_type]
            self._save_secrets(secrets)
    
    def list_keys(self) -> dict:
        """List all stored keys (without values)."""
        secrets = self._load_secrets()
        return {k: "***" for k in secrets.keys()}
    
    def _load_secrets(self) -> dict:
        """Load secrets from file."""
        if not self.secrets_file.exists():
            return {}
        
        try:
            with open(self.secrets_file) as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}
    
    def _save_secrets(self, secrets: dict):
        """Save secrets to file."""
        # Set restrictive permissions
        self.secrets_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.secrets_file, 'w') as f:
            yaml.dump(secrets, f, default_flow_style=False)
        
        # Set file permissions to 600 (read/write for owner only)
        self.secrets_file.chmod(0o600)

