"""Configuration file management."""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.syntax import Syntax

console = Console()


class ConfigManager:
    """Manages configuration files."""
    
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or Path("phaser-config.yaml")
        self.default_config = {
            "blueprint_version": "v2.2.1",
            "nodes": [],
            "gpu_count": 1,
            "memory_limit": "16Gi",
            "storage": {
                "enabled": True,
                "type": "nfs"
            },
            "observability": {
                "enabled": True,
                "prometheus": True,
                "grafana": True,
                "jaeger": True
            }
        }
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_file.exists():
            return self.default_config.copy()
        
        try:
            with open(self.config_file) as f:
                config = yaml.safe_load(f) or {}
            # Merge with defaults
            merged = self.default_config.copy()
            merged.update(config)
            return merged
        except Exception as e:
            console.print(f"[red]Error loading config: {e}[/red]")
            return self.default_config.copy()
    
    def save(self, config: Dict[str, Any], file_path: Optional[Path] = None):
        """Save configuration to file."""
        target_file = file_path or self.config_file
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(target_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            console.print(f"[red]Error saving config: {e}[/red]")
            raise
    
    def validate(self, config: Dict[str, Any]) -> List[str]:
        """Validate configuration."""
        errors = []
        
        # Validate blueprint version
        if "blueprint_version" not in config:
            errors.append("Missing blueprint_version")
        
        # Validate nodes
        if "nodes" not in config or not config["nodes"]:
            if "inventory_file" not in config:
                errors.append("No nodes or inventory_file specified")
        
        return errors
    
    def format_config(self, config: Dict[str, Any]) -> str:
        """Format configuration for display."""
        yaml_str = yaml.dump(config, default_flow_style=False, sort_keys=False)
        syntax = Syntax(yaml_str, "yaml", theme="monokai", line_numbers=True)
        return str(syntax)
    
    def generate_template(self, output_file: Path):
        """Generate a configuration template."""
        template = {
            "blueprint_version": "v2.2.1",
            "nodes": [
                {
                    "hostname": "master1",
                    "ip": "192.168.1.10",
                    "username": "ubuntu",
                    "is_master": True,
                    "has_gpu": False
                },
                {
                    "hostname": "worker1",
                    "ip": "192.168.1.11",
                    "username": "ubuntu",
                    "is_master": False,
                    "has_gpu": True
                }
            ],
            "gpu_count": 1,
            "memory_limit": "16Gi",
            "storage": {
                "enabled": True,
                "type": "nfs"
            },
            "observability": {
                "enabled": True,
                "prometheus": True,
                "grafana": True,
                "jaeger": True
            }
        }
        
        self.save(template, output_file)

