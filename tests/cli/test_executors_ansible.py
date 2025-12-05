"""Tests for Ansible executor."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from pathlib import Path
from cli.executors.ansible import AnsibleExecutor


class TestAnsibleExecutor:
    """Test AnsibleExecutor class."""
    
    @pytest.fixture
    def executor(self):
        """Create AnsibleExecutor instance."""
        return AnsibleExecutor()
    
    @pytest.mark.asyncio
    async def test_run_playbook_success(self, executor, inventory_file):
        """Test successful playbook execution."""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(return_value=(b"stdout", b""))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await executor.run_playbook(
                playbook="01-kubespray.yml",
                inventory=inventory_file
            )
            
            assert result["success"] is True
            assert result["returncode"] == 0
    
    @pytest.mark.asyncio
    async def test_run_playbook_failure(self, executor, inventory_file):
        """Test failed playbook execution."""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(return_value=(b"", b"error"))
            mock_process.returncode = 1
            mock_subprocess.return_value = mock_process
            
            result = await executor.run_playbook(
                playbook="01-kubespray.yml",
                inventory=inventory_file
            )
            
            assert result["success"] is False
            assert result["returncode"] == 1
    
    @pytest.mark.asyncio
    async def test_run_playbook_with_extra_vars(self, executor, inventory_file):
        """Test playbook execution with extra variables."""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(return_value=(b"stdout", b""))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await executor.run_playbook(
                playbook="01-kubespray.yml",
                inventory=inventory_file,
                extra_vars={"version": "v1.28.0"}
            )
            
            assert result["success"] is True
            # Verify extra-vars was included in command
            call_args = mock_subprocess.call_args[0]
            assert "--extra-vars" in call_args
    
    @pytest.mark.asyncio
    async def test_run_ad_hoc_success(self, executor):
        """Test successful ad-hoc command execution."""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(return_value=(b"output", b""))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await executor.run_ad_hoc(
                hosts="all",
                module="ping"
            )
            
            assert result["success"] is True
    
    def test_validate_playbook_pass(self, executor, temp_dir):
        """Test playbook validation passes."""
        playbook = temp_dir / "test.yml"
        playbook.write_text("---\n- hosts: all\n  tasks: []\n")
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            
            result = executor.validate_playbook(str(playbook))
            assert result["valid"] is True
    
    def test_validate_playbook_fail(self, executor, temp_dir):
        """Test playbook validation fails."""
        playbook = temp_dir / "test.yml"
        playbook.write_text("invalid yaml")
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="",
                stderr="syntax error"
            )
            
            result = executor.validate_playbook(str(playbook))
            assert result["valid"] is False
    
    def test_list_playbooks(self, executor):
        """Test listing available playbooks."""
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = [
                Path("01-kubespray.yml"),
                Path("03-gpu-operator.yml")
            ]
            
            playbooks = executor.list_playbooks()
            assert len(playbooks) == 2
            assert "01-kubespray.yml" in playbooks

