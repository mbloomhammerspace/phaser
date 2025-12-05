#!/usr/bin/env python3
"""
Main CLI entry point for NVIDIA RAG Blueprint installer.
"""

import sys
import typer
from rich.console import Console
from rich.text import Text
from typing import Optional

from cli.commands import install, validate, diagnose, config, keys

# Initialize Typer app
app = typer.Typer(
    name="phaser",
    help="NVIDIA RAG Blueprint Installation Wizard",
    add_completion=False,
    rich_markup_mode="rich",
)

# Initialize Rich console
console = Console()

# Add command groups
app.add_typer(install.app, name="install", help="Install NVIDIA RAG Blueprint")
app.add_typer(validate.app, name="validate", help="Validate system requirements")
app.add_typer(diagnose.app, name="diagnose", help="Run diagnostics")
app.add_typer(config.app, name="config", help="Configuration management")
app.add_typer(keys.app, name="keys", help="API key management")


@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(False, "--version", "-v", help="Show version and exit"),
    ctx: typer.Context = typer.Context,
):
    """
    NVIDIA RAG Blueprint Installation Wizard
    
    A comprehensive CLI tool for installing and managing NVIDIA RAG Blueprint
    deployments on Kubernetes clusters with GPU support.
    """
    if version:
        from cli import __version__
        console.print(f"[bold green]phaser[/bold green] version [cyan]{__version__}[/cyan]")
        raise typer.Exit()
    
    # If no command provided, show help
    if ctx.invoked_subcommand is None:
        console.print("\n[bold cyan]NVIDIA RAG Blueprint Installation Wizard[/bold cyan]\n")
        console.print("Use [bold]phaser --help[/bold] to see available commands.")
        console.print("Use [bold]phaser install[/bold] to start the installation wizard.\n")


def cli():
    """Entry point for the CLI."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Installation cancelled by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    cli()

