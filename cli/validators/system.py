"""System requirements validation."""

import sys
import shutil
import subprocess
from typing import List, Dict, Any
from pathlib import Path


class SystemValidator:
    """Validates system requirements."""
    
    def validate_all(self) -> List[Dict[str, Any]]:
        """Run all system validation checks."""
        results = []
        
        results.append(self.check_python_version())
        results.append(self.check_ansible())
        results.append(self.check_ssh_key())
        results.append(self.check_git())
        results.append(self.check_kubectl())
        results.append(self.check_helm())
        
        return results
    
    def check_python_version(self) -> Dict[str, Any]:
        """Check Python version."""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            return {
                "name": "Python Version",
                "status": "pass",
                "message": f"Python {version.major}.{version.minor}.{version.micro}"
            }
        else:
            return {
                "name": "Python Version",
                "status": "fail",
                "message": f"Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)"
            }
    
    def check_ansible(self) -> Dict[str, Any]:
        """Check if Ansible is installed."""
        ansible_path = shutil.which("ansible")
        if ansible_path:
            try:
                result = subprocess.run(
                    ["ansible", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                version_line = result.stdout.split('\n')[0] if result.stdout else "Unknown"
                return {
                    "name": "Ansible",
                    "status": "pass",
                    "message": version_line
                }
            except Exception:
                pass
        
        return {
            "name": "Ansible",
            "status": "fail",
            "message": "Ansible not found (requires 2.12+)"
        }
    
    def check_ssh_key(self) -> Dict[str, Any]:
        """Check if SSH key exists."""
        ssh_key_path = Path.home() / ".ssh" / "id_rsa"
        if ssh_key_path.exists():
            # Check permissions
            stat = ssh_key_path.stat()
            if stat.st_mode & 0o077 == 0:  # Only owner can read/write
                return {
                    "name": "SSH Key",
                    "status": "pass",
                    "message": f"SSH key found: {ssh_key_path}"
                }
            else:
                return {
                    "name": "SSH Key",
                    "status": "warn",
                    "message": f"SSH key permissions too open: {ssh_key_path}"
                }
        else:
            return {
                "name": "SSH Key",
                "status": "fail",
                "message": "SSH key not found at ~/.ssh/id_rsa"
            }
    
    def check_git(self) -> Dict[str, Any]:
        """Check if Git is installed."""
        git_path = shutil.which("git")
        if git_path:
            try:
                result = subprocess.run(
                    ["git", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                version = result.stdout.strip() if result.stdout else "Unknown"
                return {
                    "name": "Git",
                    "status": "pass",
                    "message": version
                }
            except Exception:
                pass
        
        return {
            "name": "Git",
            "status": "fail",
            "message": "Git not found"
        }
    
    def check_kubectl(self) -> Dict[str, Any]:
        """Check if kubectl is installed (optional)."""
        kubectl_path = shutil.which("kubectl")
        if kubectl_path:
            try:
                result = subprocess.run(
                    ["kubectl", "version", "--client"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return {
                    "name": "kubectl",
                    "status": "pass",
                    "message": "kubectl installed (optional)"
                }
            except Exception:
                pass
        
        return {
            "name": "kubectl",
            "status": "warn",
            "message": "kubectl not found (will be needed after installation)"
        }
    
    def check_helm(self) -> Dict[str, Any]:
        """Check if Helm is installed (optional)."""
        helm_path = shutil.which("helm")
        if helm_path:
            try:
                result = subprocess.run(
                    ["helm", "version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return {
                    "name": "Helm",
                    "status": "pass",
                    "message": "Helm installed (optional)"
                }
            except Exception:
                pass
        
        return {
            "name": "Helm",
            "status": "warn",
            "message": "Helm not found (will be needed for blueprint installation)"
        }

