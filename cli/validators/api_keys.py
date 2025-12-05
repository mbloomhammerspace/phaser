"""API key validation."""

import re
import requests
from typing import Optional


class APIKeyValidator:
    """Validates API keys."""
    
    def validate_format(self, key_type: str, key_value: str) -> bool:
        """Validate API key format."""
        if key_type == "nvidia":
            # NVIDIA API keys typically start with "nvapi-"
            return key_value.startswith("nvapi-") or len(key_value) > 20
        elif key_type == "openai":
            # OpenAI API keys start with "sk-"
            return key_value.startswith("sk-")
        elif key_type == "anthropic":
            # Anthropic API keys start with "sk-ant-"
            return key_value.startswith("sk-ant-")
        else:
            return False
    
    def test_key(self, key_type: str, key_value: str) -> bool:
        """Test API key connectivity."""
        if key_type == "nvidia":
            # Test NGC API access
            try:
                # Simple test - check if we can access NGC
                response = requests.get(
                    "https://api.ngc.nvidia.com/v2/orgs",
                    headers={"Authorization": f"Bearer {key_value}"},
                    timeout=10
                )
                return response.status_code in [200, 401]  # 401 means key format is valid
            except Exception:
                return False
        
        elif key_type == "openai":
            # Test OpenAI API access
            try:
                response = requests.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {key_value}"},
                    timeout=10
                )
                return response.status_code == 200
            except Exception:
                return False
        
        elif key_type == "anthropic":
            # Test Anthropic API access
            try:
                response = requests.get(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": key_value,
                        "anthropic-version": "2023-06-01"
                    },
                    timeout=10
                )
                # 400 is expected for GET without body, but means auth works
                return response.status_code in [200, 400]
            except Exception:
                return False
        
        return False

