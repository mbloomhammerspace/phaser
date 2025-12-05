"""API key management command module."""

import typer
from rich.console import Console
from typing import Optional
import getpass

from cli.utils.secrets import SecretManager
from cli.validators.api_keys import APIKeyValidator

app = typer.Typer(name="keys", help="API key management")
console = Console()


@app.command()
def set(
    key_type: str = typer.Argument(..., help="Key type: nvidia, openai, or anthropic"),
    key_value: Optional[str] = typer.Option(
        None, "--value", "-v", help="API key value (if not provided, will prompt)"
    ),
    test: bool = typer.Option(
        True, "--test/--no-test", help="Test API key after setting"
    ),
):
    """
    Set an API key.
    
    Supported key types:
    - nvidia: NVIDIA API key (required for NGC registry)
    - openai: OpenAI API key (optional, for AI diagnostics)
    - anthropic: Anthropic API key (optional, for alternative AI services)
    """
    if key_type not in ["nvidia", "openai", "anthropic"]:
        console.print(f"[bold red]Error:[/bold red] Invalid key type: {key_type}")
        console.print("Supported types: nvidia, openai, anthropic")
        raise typer.Exit(1)
    
    # Get key value
    if not key_value:
        key_value = getpass.getpass(f"Enter {key_type.upper()} API key: ")
    
    if not key_value:
        console.print("[bold red]Error:[/bold red] API key cannot be empty")
        raise typer.Exit(1)
    
    # Validate format
    validator = APIKeyValidator()
    if not validator.validate_format(key_type, key_value):
        console.print(f"[bold red]Error:[/bold red] Invalid {key_type} API key format")
        raise typer.Exit(1)
    
    # Test key if requested
    if test:
        console.print(f"[yellow]Testing {key_type} API key...[/yellow]")
        if not validator.test_key(key_type, key_value):
            console.print(f"[bold red]Error:[/bold red] API key test failed")
            console.print("Please verify your API key is correct and has the required permissions.")
            raise typer.Exit(1)
        console.print(f"[green]✓ API key test passed[/green]")
    
    # Store key
    try:
        secret_manager = SecretManager()
        secret_manager.set_key(key_type, key_value)
        console.print(f"[green]✓ {key_type.upper()} API key stored successfully[/green]\n")
        
    except Exception as e:
        console.print(f"[bold red]Error storing key:[/bold red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def list():
    """
    List configured API keys (without showing values).
    """
    try:
        secret_manager = SecretManager()
        keys = secret_manager.list_keys()
        
        if not keys:
            console.print("\n[yellow]No API keys configured[/yellow]\n")
            return
        
        console.print("\n[bold cyan]Configured API Keys[/bold cyan]\n")
        for key_type in ["nvidia", "openai", "anthropic"]:
            if key_type in keys:
                status = "[green]✓ Configured[/green]"
            else:
                status = "[yellow]Not set[/yellow]"
            
            required = "[red](required)[/red]" if key_type == "nvidia" else "[dim](optional)[/dim]"
            console.print(f"  {key_type.upper():12} {status} {required}")
        
        console.print()
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def test(
    key_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Key type to test (default: all)"
    ),
):
    """
    Test configured API keys.
    """
    try:
        secret_manager = SecretManager()
        validator = APIKeyValidator()
        
        key_types = [key_type] if key_type else ["nvidia", "openai", "anthropic"]
        
        console.print("\n[bold cyan]Testing API Keys[/bold cyan]\n")
        
        for kt in key_types:
            key_value = secret_manager.get_key(kt)
            if not key_value:
                console.print(f"  {kt.upper():12} [yellow]Not configured[/yellow]")
                continue
            
            console.print(f"  {kt.upper():12} ", end="")
            if validator.test_key(kt, key_value):
                console.print("[green]✓ Test passed[/green]")
            else:
                console.print("[red]✗ Test failed[/red]")
        
        console.print()
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def remove(
    key_type: str = typer.Argument(..., help="Key type to remove"),
):
    """
    Remove a stored API key.
    """
    if key_type not in ["nvidia", "openai", "anthropic"]:
        console.print(f"[bold red]Error:[/bold red] Invalid key type: {key_type}")
        raise typer.Exit(1)
    
    try:
        secret_manager = SecretManager()
        secret_manager.remove_key(key_type)
        console.print(f"[green]✓ {key_type.upper()} API key removed[/green]\n")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)

