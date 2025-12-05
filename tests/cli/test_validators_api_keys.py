"""Tests for API key validator."""

import pytest
from unittest.mock import patch, Mock
from cli.validators.api_keys import APIKeyValidator


class TestAPIKeyValidator:
    """Test APIKeyValidator class."""
    
    def test_validate_format_nvidia_pass(self):
        """Test NVIDIA API key format validation passes."""
        validator = APIKeyValidator()
        assert validator.validate_format("nvidia", "nvapi-1234567890abcdef")
        assert validator.validate_format("nvidia", "some-long-key-value-12345")
    
    def test_validate_format_nvidia_fail(self):
        """Test NVIDIA API key format validation fails for short keys."""
        validator = APIKeyValidator()
        assert not validator.validate_format("nvidia", "short")
    
    def test_validate_format_openai_pass(self):
        """Test OpenAI API key format validation passes."""
        validator = APIKeyValidator()
        assert validator.validate_format("openai", "sk-1234567890abcdef")
    
    def test_validate_format_openai_fail(self):
        """Test OpenAI API key format validation fails."""
        validator = APIKeyValidator()
        assert not validator.validate_format("openai", "invalid-key")
    
    def test_validate_format_anthropic_pass(self):
        """Test Anthropic API key format validation passes."""
        validator = APIKeyValidator()
        assert validator.validate_format("anthropic", "sk-ant-1234567890abcdef")
    
    def test_validate_format_anthropic_fail(self):
        """Test Anthropic API key format validation fails."""
        validator = APIKeyValidator()
        assert not validator.validate_format("anthropic", "invalid-key")
    
    @patch('requests.get')
    def test_test_key_nvidia_pass(self, mock_get):
        """Test NVIDIA API key test passes."""
        mock_get.return_value = Mock(status_code=200)
        
        validator = APIKeyValidator()
        result = validator.test_key("nvidia", "nvapi-test-key")
        
        assert result is True
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_test_key_nvidia_fail(self, mock_get):
        """Test NVIDIA API key test fails."""
        mock_get.side_effect = Exception("Connection error")
        
        validator = APIKeyValidator()
        result = validator.test_key("nvidia", "nvapi-test-key")
        
        assert result is False
    
    @patch('requests.get')
    def test_test_key_openai_pass(self, mock_get):
        """Test OpenAI API key test passes."""
        mock_get.return_value = Mock(status_code=200)
        
        validator = APIKeyValidator()
        result = validator.test_key("openai", "sk-test-key")
        
        assert result is True
    
    @patch('requests.get')
    def test_test_key_openai_fail(self, mock_get):
        """Test OpenAI API key test fails."""
        mock_get.return_value = Mock(status_code=401)
        
        validator = APIKeyValidator()
        result = validator.test_key("openai", "sk-invalid-key")
        
        assert result is False
    
    @patch('requests.get')
    def test_test_key_anthropic_pass(self, mock_get):
        """Test Anthropic API key test passes."""
        mock_get.return_value = Mock(status_code=400)  # 400 is expected for GET
        
        validator = APIKeyValidator()
        result = validator.test_key("anthropic", "sk-ant-test-key")
        
        assert result is True

