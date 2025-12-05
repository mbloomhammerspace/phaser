"""Validation command module."""

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional

from cli.validators.system import SystemValidator
from cli.validators.hardware import HardwareValidator
from cli.validators.network import NetworkValidator

app = typer.Typer(name="validate", help="Validate system requirements")
console = Console()


@app.command()
def preflight(
    inventory_file: Optional[str] = typer.Option(
        None, "--inventory", "-i", help="Path to Ansible inventory file"
    ),
):
    """
    Run pre-installation validation checks.
    
    Validates system requirements, hardware capabilities, and network connectivity
    before starting the installation process.
    """
    console.print("\n[bold cyan]Running Pre-Installation Validation[/bold cyan]\n")
    
    results = {
        "system": [],
        "hardware": [],
        "network": []
    }
    
    # System validation
    console.print("[yellow]Checking system requirements...[/yellow]")
    system_validator = SystemValidator()
    system_results = system_validator.validate_all()
    results["system"] = system_results
    
    # Hardware validation (if inventory provided)
    if inventory_file:
        console.print("[yellow]Checking hardware requirements...[/yellow]")
        hardware_validator = HardwareValidator(inventory_file)
        hardware_results = hardware_validator.validate_all()
        results["hardware"] = hardware_results
    
    # Network validation (if inventory provided)
    if inventory_file:
        console.print("[yellow]Checking network connectivity...[/yellow]")
        network_validator = NetworkValidator(inventory_file)
        network_results = network_validator.validate_all()
        results["network"] = network_results
    
    # Display results
    _display_validation_results(results)
    
    # Summary
    all_passed = all(
        all(check["status"] == "pass" for check in category)
        for category in results.values()
        if category
    )
    
    if all_passed:
        console.print("\n[bold green]✓ All validation checks passed![/bold green]\n")
        raise typer.Exit(0)
    else:
        console.print("\n[bold red]✗ Some validation checks failed. Please fix issues before proceeding.[/bold red]\n")
        raise typer.Exit(1)


@app.command()
def post_install():
    """
    Run post-installation validation checks.
    
    Validates that the installation completed successfully and all services
    are running correctly.
    """
    console.print("\n[bold cyan]Running Post-Installation Validation[/bold cyan]\n")
    console.print("[yellow]Post-installation validation not yet implemented.[/yellow]\n")


@app.command()
def all(
    inventory_file: Optional[str] = typer.Option(
        None, "--inventory", "-i", help="Path to Ansible inventory file"
    ),
):
    """
    Run all validation checks (preflight and post-install).
    """
    console.print("\n[bold cyan]Running All Validation Checks[/bold cyan]\n")
    
    # Run preflight
    try:
        preflight(inventory_file=inventory_file)
    except SystemExit:
        pass  # preflight may exit with code 1 if checks fail
    
    # Run post-install (if cluster exists)
    try:
        post_install()
    except Exception as e:
        console.print(f"[yellow]Post-installation checks skipped: {str(e)}[/yellow]")


def _display_validation_results(results: dict):
    """Display validation results in a formatted table."""
    table = Table(title="Validation Results", show_header=True, header_style="bold cyan")
    table.add_column("Category", style="cyan")
    table.add_column("Check", style="white")
    table.add_column("Status", style="white")
    table.add_column("Message", style="dim")
    
    for category, checks in results.items():
        if not checks:
            continue
        
        for i, check in enumerate(checks):
            status_icon = "✓" if check["status"] == "pass" else "✗"
            status_color = "green" if check["status"] == "pass" else "red"
            status_text = f"[{status_color}]{status_icon} {check['status'].upper()}[/{status_color}]"
            
            category_name = category.capitalize() if i == 0 else ""
            table.add_row(
                category_name,
                check["name"],
                status_text,
                check.get("message", "")
            )
    
    console.print(table)

