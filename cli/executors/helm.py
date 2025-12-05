"""
Helm execution wrapper.
"""

import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class HelmExecutor:
    """Executes Helm commands."""
    
    def __init__(self, helm_path: Optional[str] = None):
        self.helm_path = helm_path or "helm"
    
    async def install(
        self,
        release_name: str,
        chart: str,
        namespace: Optional[str] = None,
        values: Optional[Dict[str, Any]] = None,
        values_file: Optional[str] = None,
        wait: bool = True,
        timeout: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Install a Helm chart.
        
        Args:
            release_name: Name of the release
            chart: Chart name or path
            namespace: Target namespace
            values: Values as dictionary
            values_file: Path to values file
            wait: Wait for deployment to complete
            timeout: Timeout for deployment
        
        Returns:
            Dictionary with execution results
        """
        cmd = [self.helm_path, "install", release_name, chart]
        
        if namespace:
            cmd.extend(["--namespace", namespace, "--create-namespace"])
        
        if values_file:
            cmd.extend(["--values", values_file])
        elif values:
            # Create temporary values file
            import tempfile
            import yaml
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(values, f)
                cmd.extend(["--values", f.name])
        
        if wait:
            cmd.append("--wait")
        
        if timeout:
            cmd.extend(["--timeout", timeout])
        
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
                "release_name": release_name,
                "command": " ".join(cmd)
            }
        
        except Exception as e:
            logger.error(f"Error installing Helm chart: {e}")
            return {
                "success": False,
                "error": str(e),
                "release_name": release_name
            }
    
    async def upgrade(
        self,
        release_name: str,
        chart: str,
        namespace: Optional[str] = None,
        values: Optional[Dict[str, Any]] = None,
        values_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upgrade a Helm release."""
        cmd = [self.helm_path, "upgrade", release_name, chart]
        
        if namespace:
            cmd.extend(["--namespace", namespace])
        
        if values_file:
            cmd.extend(["--values", values_file])
        elif values:
            import tempfile
            import yaml
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(values, f)
                cmd.extend(["--values", f.name])
        
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
                "stderr": stderr.decode() if stderr else ""
            }
        
        except Exception as e:
            logger.error(f"Error upgrading Helm release: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def uninstall(
        self,
        release_name: str,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """Uninstall a Helm release."""
        cmd = [self.helm_path, "uninstall", release_name]
        
        if namespace:
            cmd.extend(["--namespace", namespace])
        
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
                "stderr": stderr.decode() if stderr else ""
            }
        
        except Exception as e:
            logger.error(f"Error uninstalling Helm release: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_releases(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """List Helm releases."""
        cmd = [self.helm_path, "list", "--output", "json"]
        
        if namespace:
            cmd.extend(["--namespace", namespace])
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                import json
                releases = json.loads(stdout.decode())
                return releases
            else:
                return []
        
        except Exception as e:
            logger.error(f"Error listing Helm releases: {e}")
            return []

