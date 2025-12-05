"""Configuration management command module."""

import typer
from rich.console import Console
from pathlib import Path
from typing import Optional

from cli.utils.config import ConfigManager

app = typer.Typer(name="config", help="Configuration management")
console = Console()


@app.command()
def show(
    config_file: Optional[Path] = typer.Option(
        None, "--file", "-f", help="Path to configuration file"
    ),
):
    """
    Display current configuration.
    """
    try:
        config_manager = ConfigManager(config_file)
        config = config_manager.load()
        
        console.print("\n[bold cyan]Current Configuration[/bold cyan]\n")
        console.print(config_manager.format_config(config))
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def validate(
    config_file: Path = typer.Argument(..., help="Path to configuration file"),
):
    """
    Validate configuration file.
    """
    console.print(f"\n[bold cyan]Validating configuration:[/bold cyan] {config_file}\n")
    
    try:
        config_manager = ConfigManager(config_file)
        config = config_manager.load()
        errors = config_manager.validate(config)
        
        if errors:
            console.print("[bold red]Configuration validation failed:[/bold red]\n")
            for error in errors:
                console.print(f"  [red]✗[/red] {error}")
            raise typer.Exit(1)
        else:
            console.print("[bold green]✓ Configuration is valid![/bold green]\n")
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def generate(
    output_file: Path = typer.Option(
        Path("phaser-config.yaml"), "--output", "-o", help="Output file path"
    ),
):
    """
    Generate a configuration file template.
    """
    console.print(f"\n[bold cyan]Generating configuration template:[/bold cyan] {output_file}\n")
    
    try:
        config_manager = ConfigManager()
        config_manager.generate_template(output_file)
        console.print(f"[green]Configuration template created: {output_file}[/green]\n")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)

