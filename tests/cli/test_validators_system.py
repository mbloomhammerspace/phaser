"""Tests for system validator."""

import pytest
from unittest.mock import patch, MagicMock
from cli.validators.system import SystemValidator


class TestSystemValidator:
    """Test SystemValidator class."""
    
    def test_check_python_version_pass(self):
        """Test Python version check passes for Python 3.8+."""
        validator = SystemValidator()
        result = validator.check_python_version()
        
        assert result["status"] == "pass"
        assert "Python" in result["message"]
    
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_check_ansible_pass(self, mock_run, mock_which):
        """Test Ansible check passes when Ansible is installed."""
        mock_which.return_value = "/usr/bin/ansible"
        mock_run.return_value = MagicMock(
            stdout="ansible 2.12.0\n",
            returncode=0
        )
        
        validator = SystemValidator()
        result = validator.check_ansible()
        
        assert result["status"] == "pass"
        assert "ansible" in result["message"].lower()
    
    @patch('shutil.which')
    def test_check_ansible_fail(self, mock_which):
        """Test Ansible check fails when Ansible is not installed."""
        mock_which.return_value = None
        
        validator = SystemValidator()
        result = validator.check_ansible()
        
        assert result["status"] == "fail"
        assert "not found" in result["message"].lower()
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_check_ssh_key_pass(self, mock_stat, mock_exists):
        """Test SSH key check passes when key exists with correct permissions."""
        mock_exists.return_value = True
        mock_stat.return_value = MagicMock(st_mode=0o600)
        
        validator = SystemValidator()
        result = validator.check_ssh_key()
        
        assert result["status"] == "pass"
        assert "SSH key found" in result["message"]
    
    @patch('pathlib.Path.exists')
    def test_check_ssh_key_fail(self, mock_exists):
        """Test SSH key check fails when key doesn't exist."""
        mock_exists.return_value = False
        
        validator = SystemValidator()
        result = validator.check_ssh_key()
        
        assert result["status"] == "fail"
        assert "not found" in result["message"].lower()
    
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_check_git_pass(self, mock_run, mock_which):
        """Test Git check passes when Git is installed."""
        mock_which.return_value = "/usr/bin/git"
        mock_run.return_value = MagicMock(
            stdout="git version 2.30.0\n",
            returncode=0
        )
        
        validator = SystemValidator()
        result = validator.check_git()
        
        assert result["status"] == "pass"
        assert "git" in result["message"].lower()
    
    @patch('shutil.which')
    def test_check_git_fail(self, mock_which):
        """Test Git check fails when Git is not installed."""
        mock_which.return_value = None
        
        validator = SystemValidator()
        result = validator.check_git()
        
        assert result["status"] == "fail"
    
    def test_validate_all(self):
        """Test validate_all returns list of results."""
        validator = SystemValidator()
        results = validator.validate_all()
        
        assert isinstance(results, list)
        assert len(results) > 0
        for result in results:
            assert "name" in result
            assert "status" in result
            assert "message" in result

