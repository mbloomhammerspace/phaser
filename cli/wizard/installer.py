"""Installation wizard implementation."""

from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
import yaml

from cli.utils.config import ConfigManager
from cli.validators.system import SystemValidator
from cli.utils.secrets import SecretManager

console = Console()


class InstallationWizard:
    """Interactive installation wizard."""
    
    def __init__(
        self,
        config_file: Optional[Path] = None,
        resume: bool = False,
        dry_run: bool = False
    ):
        self.config_file = config_file
        self.resume = resume
        self.dry_run = dry_run
        self.config_manager = ConfigManager(config_file)
        self.config: Dict[str, Any] = {}
        
    def run(self):
        """Run the installation wizard."""
        console.print(Panel.fit(
            "[bold cyan]Welcome to NVIDIA RAG Blueprint Installation Wizard[/bold cyan]\n\n"
            "This wizard will guide you through the installation process.\n"
            "You'll be asked to provide:\n"
            "  • System configuration\n"
            "  • API keys\n"
            "  • Node information\n"
            "  • Blueprint settings",
            border_style="cyan"
        ))
        
        # Step 1: Prerequisites check
        if not self._check_prerequisites():
            console.print("\n[bold red]Prerequisites check failed. Please fix issues and try again.[/bold red]")
            return False
        
        # Step 2: API Key Configuration
        self._configure_api_keys()
        
        # Step 3: Node Configuration
        self._configure_nodes()
        
        # Step 4: Blueprint Configuration
        self._configure_blueprint()
        
        # Step 5: Review and Confirm
        if not self._review_and_confirm():
            console.print("\n[yellow]Installation cancelled.[/yellow]")
            return False
        
        # Step 6: Execute Installation
        if not self.dry_run:
            return self._execute_installation()
        else:
            console.print("\n[green]Dry run completed. Configuration is valid![/green]")
            return True
    
    def _check_prerequisites(self) -> bool:
        """Check system prerequisites."""
        console.print("\n[bold cyan]Step 1: Checking Prerequisites[/bold cyan]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Validating system requirements...", total=None)
            
            validator = SystemValidator()
            results = validator.validate_all()
            
            progress.update(task, completed=True)
        
        # Display results
        all_passed = all(check["status"] == "pass" for check in results)
        
        for check in results:
            status_icon = "✓" if check["status"] == "pass" else "✗"
            status_color = "green" if check["status"] == "pass" else "red"
            console.print(f"  [{status_color}]{status_icon}[/{status_color}] {check['name']}: {check.get('message', '')}")
        
        if not all_passed:
            console.print("\n[yellow]Some prerequisites are missing. You can continue, but installation may fail.[/yellow]")
            return Confirm.ask("\nContinue anyway?", default=False)
        
        return True
    
    def _configure_api_keys(self):
        """Configure API keys."""
        console.print("\n[bold cyan]Step 2: API Key Configuration[/bold cyan]\n")
        
        secret_manager = SecretManager()
        
        # NVIDIA API Key (required)
        console.print("[bold]NVIDIA API Key[/bold] [red](required)[/red]")
        nvidia_key = secret_manager.get_key("nvidia")
        if nvidia_key:
            console.print("[green]NVIDIA API key already configured[/green]")
            if not Confirm.ask("Update NVIDIA API key?", default=False):
                nvidia_key = None
        
        if not nvidia_key:
            from cli.commands.keys import set as set_key
            console.print("Please set your NVIDIA API key:")
            console.print("  Run: [cyan]phaser keys set nvidia[/cyan]")
            if Confirm.ask("Set NVIDIA API key now?", default=True):
                import getpass
                key_value = getpass.getpass("Enter NVIDIA API key: ")
                if key_value:
                    secret_manager.set_key("nvidia", key_value)
        
        # OpenAI API Key (optional)
        console.print("\n[bold]OpenAI API Key[/bold] [dim](optional, for AI diagnostics)[/dim]")
        if Confirm.ask("Configure OpenAI API key?", default=False):
            import getpass
            key_value = getpass.getpass("Enter OpenAI API key: ")
            if key_value:
                secret_manager.set_key("openai", key_value)
    
    def _configure_nodes(self):
        """Configure node information."""
        console.print("\n[bold cyan]Step 3: Node Configuration[/bold cyan]\n")
        
        console.print("How would you like to configure nodes?")
        method = Prompt.ask(
            "Method",
            choices=["interactive", "file"],
            default="interactive"
        )
        
        if method == "interactive":
            self._configure_nodes_interactive()
        else:
            self._configure_nodes_from_file()
    
    def _configure_nodes_interactive(self):
        """Configure nodes interactively."""
        console.print("\nEnter node information (press Enter twice when done):")
        
        nodes = []
        while True:
            hostname = Prompt.ask("\nHostname", default="")
            if not hostname:
                break
            
            ip = Prompt.ask("IP Address")
            username = Prompt.ask("SSH Username", default="ubuntu")
            is_master = Confirm.ask("Is this a master node?", default=False)
            has_gpu = Confirm.ask("Does this node have GPU?", default=False)
            
            nodes.append({
                "hostname": hostname,
                "ip": ip,
                "username": username,
                "is_master": is_master,
                "has_gpu": has_gpu
            })
        
        self.config["nodes"] = nodes
    
    def _configure_nodes_from_file(self):
        """Configure nodes from inventory file."""
        inventory_path = Prompt.ask("Path to inventory file")
        inventory_file = Path(inventory_path)
        
        if not inventory_file.exists():
            console.print(f"[red]Error: File not found: {inventory_file}[/red]")
            self._configure_nodes_interactive()
            return
        
        # Parse inventory file (simplified)
        try:
            with open(inventory_file) as f:
                inventory = yaml.safe_load(f)
            self.config["inventory_file"] = str(inventory_file)
            console.print(f"[green]Loaded inventory from: {inventory_file}[/green]")
        except Exception as e:
            console.print(f"[red]Error parsing inventory file: {e}[/red]")
            self._configure_nodes_interactive()
    
    def _configure_blueprint(self):
        """Configure blueprint settings."""
        console.print("\n[bold cyan]Step 4: Blueprint Configuration[/bold cyan]\n")
        
        version = Prompt.ask("Blueprint version", default="v2.2.1")
        self.config["blueprint_version"] = version
        
        # Resource configuration
        console.print("\n[bold]Resource Configuration[/bold]")
        gpu_count = Prompt.ask("GPU count per GPU node", default="1")
        self.config["gpu_count"] = int(gpu_count)
        
        memory_limit = Prompt.ask("Memory limit (e.g., 16Gi)", default="16Gi")
        self.config["memory_limit"] = memory_limit
    
    def _review_and_confirm(self) -> bool:
        """Review configuration and confirm."""
        console.print("\n[bold cyan]Step 5: Review Configuration[/bold cyan]\n")
        
        # Display configuration summary
        console.print("[bold]Configuration Summary:[/bold]")
        console.print(f"  Blueprint Version: {self.config.get('blueprint_version', 'N/A')}")
        console.print(f"  Nodes: {len(self.config.get('nodes', []))}")
        console.print(f"  GPU Count: {self.config.get('gpu_count', 'N/A')}")
        
        if self.dry_run:
            console.print("\n[yellow]DRY RUN MODE - No changes will be made[/yellow]")
        
        return Confirm.ask("\nProceed with installation?", default=True)
    
    def _execute_installation(self) -> bool:
        """Execute the installation."""
        console.print("\n[bold cyan]Step 6: Installation Execution[/bold cyan]\n")
        
        console.print("[yellow]Installation execution not yet implemented.[/yellow]")
        console.print("This will execute Ansible playbooks to install:")
        console.print("  1. Kubernetes cluster (Kubespray)")
        console.print("  2. NVIDIA GPU Operator")
        console.print("  3. NVIDIA RAG Blueprint")
        console.print("  4. Observability stack")
        
        # Save configuration
        if self.config_file:
            self.config_manager.save(self.config, self.config_file)
            console.print(f"\n[green]Configuration saved to: {self.config_file}[/green]")
        
        return True

