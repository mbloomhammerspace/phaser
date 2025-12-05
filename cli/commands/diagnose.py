"""Diagnostic command module."""

import typer
from rich.console import Console
from pathlib import Path
from typing import Optional

from cli.diagnostics.preflight import PreflightDiagnostics
from cli.diagnostics.installation import InstallationDiagnostics
from cli.diagnostics.post_install import PostInstallDiagnostics

app = typer.Typer(name="diagnose", help="Run diagnostic checks")
console = Console()


@app.command()
def preflight(
    export: Optional[Path] = typer.Option(
        None, "--export", "-e", help="Export diagnostic report to file"
    ),
):
    """
    Run pre-installation diagnostics.
    
    Performs comprehensive system health checks, network diagnostics,
    and hardware detection before installation.
    """
    console.print("\n[bold cyan]Pre-Installation Diagnostics[/bold cyan]\n")
    
    try:
        diagnostics = PreflightDiagnostics()
        report = diagnostics.run_all()
        
        # Display report
        diagnostics.display_report(report)
        
        # Export if requested
        if export:
            diagnostics.export_report(report, export)
            console.print(f"\n[green]Diagnostic report exported to: {export}[/green]")
            
    except Exception as e:
        console.print(f"[bold red]Diagnostics failed:[/bold red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def installation(
    export: Optional[Path] = typer.Option(
        None, "--export", "-e", help="Export diagnostic report to file"
    ),
):
    """
    Run installation diagnostics.
    
    Monitors installation progress, checks for errors, and provides
    troubleshooting suggestions.
    """
    console.print("\n[bold cyan]Installation Diagnostics[/bold cyan]\n")
    
    try:
        diagnostics = InstallationDiagnostics()
        report = diagnostics.run_all()
        
        # Display report
        diagnostics.display_report(report)
        
        # Export if requested
        if export:
            diagnostics.export_report(report, export)
            console.print(f"\n[green]Diagnostic report exported to: {export}[/green]")
            
    except Exception as e:
        console.print(f"[bold red]Diagnostics failed:[/bold red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def cluster(
    export: Optional[Path] = typer.Option(
        None, "--export", "-e", help="Export diagnostic report to file"
    ),
):
    """
    Run cluster diagnostics.
    
    Performs comprehensive health checks on the Kubernetes cluster,
    services, and RAG components.
    """
    console.print("\n[bold cyan]Cluster Diagnostics[/bold cyan]\n")
    
    try:
        diagnostics = PostInstallDiagnostics()
        report = diagnostics.run_all()
        
        # Display report
        diagnostics.display_report(report)
        
        # Export if requested
        if export:
            diagnostics.export_report(report, export)
            console.print(f"\n[green]Diagnostic report exported to: {export}[/green]")
            
    except Exception as e:
        console.print(f"[bold red]Diagnostics failed:[/bold red] {str(e)}")
        raise typer.Exit(1)

