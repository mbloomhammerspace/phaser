"""
kubectl execution wrapper.
"""

import subprocess
import asyncio
import json
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class KubectlExecutor:
    """Executes kubectl commands."""
    
    def __init__(self, kubectl_path: Optional[str] = None, kubeconfig: Optional[str] = None):
        self.kubectl_path = kubectl_path or "kubectl"
        self.kubeconfig = kubeconfig
    
    async def run_command(
        self,
        command: List[str],
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run a kubectl command.
        
        Args:
            command: kubectl command as list
            namespace: Target namespace
        
        Returns:
            Dictionary with execution results
        """
        cmd = [self.kubectl_path]
        
        if self.kubeconfig:
            cmd.extend(["--kubeconfig", self.kubeconfig])
        
        if namespace:
            cmd.extend(["--namespace", namespace])
        
        cmd.extend(command)
        
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
            logger.error(f"Error executing kubectl command: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_nodes(self) -> List[Dict[str, Any]]:
        """Get cluster nodes."""
        result = await self.run_command(["get", "nodes", "-o", "json"])
        
        if result["success"]:
            try:
                data = json.loads(result["stdout"])
                return data.get("items", [])
            except json.JSONDecodeError:
                return []
        return []
    
    async def get_pods(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get pods."""
        result = await self.run_command(
            ["get", "pods", "-o", "json"],
            namespace=namespace
        )
        
        if result["success"]:
            try:
                data = json.loads(result["stdout"])
                return data.get("items", [])
            except json.JSONDecodeError:
                return []
        return []
    
    async def get_services(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get services."""
        result = await self.run_command(
            ["get", "services", "-o", "json"],
            namespace=namespace
        )
        
        if result["success"]:
            try:
                data = json.loads(result["stdout"])
                return data.get("items", [])
            except json.JSONDecodeError:
                return []
        return []
    
    async def apply(self, manifest: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Apply a Kubernetes manifest."""
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(manifest)
            temp_file = f.name
        
        try:
            result = await self.run_command(
                ["apply", "-f", temp_file],
                namespace=namespace
            )
            return result
        finally:
            import os
            os.unlink(temp_file)
    
    async def delete(self, resource_type: str, resource_name: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Delete a Kubernetes resource."""
        return await self.run_command(
            ["delete", resource_type, resource_name],
            namespace=namespace
        )
    
    async def wait_for_deployment(
        self,
        deployment_name: str,
        namespace: Optional[str] = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """Wait for a deployment to be ready."""
        return await self.run_command(
            ["wait", "--for=condition=available", f"--timeout={timeout}s", f"deployment/{deployment_name}"],
            namespace=namespace
        )
    
    async def get_cluster_info(self) -> Dict[str, Any]:
        """Get cluster information."""
        result = await self.run_command(["cluster-info"])
        
        version_result = await self.run_command(["version", "-o", "json"])
        
        info = {
            "cluster_info": result["stdout"] if result["success"] else "",
            "version": {}
        }
        
        if version_result["success"]:
            try:
                info["version"] = json.loads(version_result["stdout"])
            except json.JSONDecodeError:
                pass
        
        return info

