"""Installation command module."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from typing import Optional
from pathlib import Path

from cli.wizard.installer import InstallationWizard

app = typer.Typer(name="install", help="Install NVIDIA RAG Blueprint")
console = Console()


@app.command()
def interactive(
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to configuration file"
    ),
    resume: bool = typer.Option(
        False, "--resume", help="Resume interrupted installation"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Validate configuration without installing"
    ),
):
    """
    Run interactive installation wizard.
    
    This command guides you through the installation process step by step,
    collecting all necessary information and validating requirements.
    """
    console.print("\n[bold cyan]NVIDIA RAG Blueprint Installation Wizard[/bold cyan]\n")
    
    try:
        wizard = InstallationWizard(
            config_file=config_file,
            resume=resume,
            dry_run=dry_run
        )
        wizard.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Installation cancelled by user.[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Installation failed:[/bold red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def from_config(
    config_file: Path = typer.Argument(..., help="Path to configuration file"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Validate configuration without installing"
    ),
):
    """
    Install from existing configuration file.
    
    Use this command when you have a previously generated configuration file
    and want to install without going through the interactive wizard.
    """
    if not config_file.exists():
        console.print(f"[bold red]Error:[/bold red] Configuration file not found: {config_file}")
        raise typer.Exit(1)
    
    console.print(f"\n[bold cyan]Installing from configuration:[/bold cyan] {config_file}\n")
    
    try:
        wizard = InstallationWizard(
            config_file=config_file,
            resume=False,
            dry_run=dry_run
        )
        wizard.run()
    except Exception as e:
        console.print(f"\n[bold red]Installation failed:[/bold red] {str(e)}")
        raise typer.Exit(1)

