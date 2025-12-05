"""
Ansible execution wrapper.
"""

import subprocess
import asyncio
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class AnsibleExecutor:
    """Executes Ansible playbooks."""
    
    def __init__(self, ansible_path: Optional[str] = None):
        self.ansible_path = ansible_path or "ansible-playbook"
        self.playbooks_dir = Path(__file__).parent.parent.parent / "playbooks"
    
    async def run_playbook(
        self,
        playbook: str,
        inventory: Optional[str] = None,
        extra_vars: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        skip_tags: Optional[List[str]] = None,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Run an Ansible playbook.
        
        Args:
            playbook: Playbook filename or path
            inventory: Inventory file path
            extra_vars: Extra variables to pass to playbook
            tags: Tags to run
            skip_tags: Tags to skip
            verbose: Enable verbose output
        
        Returns:
            Dictionary with execution results
        """
        # Resolve playbook path
        if Path(playbook).is_absolute():
            playbook_path = Path(playbook)
        else:
            playbook_path = self.playbooks_dir / playbook
        
        if not playbook_path.exists():
            raise FileNotFoundError(f"Playbook not found: {playbook_path}")
        
        # Build command
        cmd = [self.ansible_path, str(playbook_path)]
        
        # Add inventory
        if inventory:
            if Path(inventory).exists():
                cmd.extend(["-i", str(inventory)])
            else:
                # Try to find inventory in common locations
                inv_path = self._find_inventory(inventory)
                if inv_path:
                    cmd.extend(["-i", str(inv_path)])
        
        # Add extra vars
        if extra_vars:
            cmd.extend(["--extra-vars", json.dumps(extra_vars)])
        
        # Add tags
        if tags:
            cmd.extend(["--tags", ",".join(tags)])
        
        # Add skip tags
        if skip_tags:
            cmd.extend(["--skip-tags", ",".join(skip_tags)])
        
        # Verbose mode
        if verbose:
            cmd.append("-vvv")
        
        # Execute playbook
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.playbooks_dir.parent)
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
                "playbook": str(playbook_path),
                "command": " ".join(cmd)
            }
        
        except Exception as e:
            logger.error(f"Error executing playbook: {e}")
            return {
                "success": False,
                "error": str(e),
                "playbook": str(playbook_path)
            }
    
    def _find_inventory(self, inventory_name: str) -> Optional[Path]:
        """Find inventory file in common locations."""
        search_paths = [
            Path(".") / inventory_name,
            Path(".") / "inventory" / inventory_name,
            Path(".") / "discovery" / inventory_name,
            Path.home() / ".phaser" / inventory_name
        ]
        
        for path in search_paths:
            if path.exists():
                return path
        
        return None
    
    async def run_ad_hoc(
        self,
        hosts: str,
        module: str,
        args: Optional[str] = None,
        inventory: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run an ad-hoc Ansible command.
        
        Args:
            hosts: Host pattern
            module: Ansible module name
            args: Module arguments
            inventory: Inventory file path
        
        Returns:
            Dictionary with execution results
        """
        cmd = ["ansible", hosts, "-m", module]
        
        if args:
            cmd.extend(["-a", args])
        
        if inventory:
            cmd.extend(["-i", str(inventory)])
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
                "command": " ".join(cmd)
            }
        
        except Exception as e:
            logger.error(f"Error executing ad-hoc command: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_playbook(self, playbook: str) -> Dict[str, Any]:
        """Validate an Ansible playbook syntax."""
        if Path(playbook).is_absolute():
            playbook_path = Path(playbook)
        else:
            playbook_path = self.playbooks_dir / playbook
        
        if not playbook_path.exists():
            return {
                "valid": False,
                "error": f"Playbook not found: {playbook_path}"
            }
        
        try:
            result = subprocess.run(
                ["ansible-playbook", "--syntax-check", str(playbook_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "valid": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def list_playbooks(self) -> List[str]:
        """List available playbooks."""
        playbooks = []
        if self.playbooks_dir.exists():
            for playbook in self.playbooks_dir.glob("*.yml"):
                playbooks.append(playbook.name)
        return sorted(playbooks)

