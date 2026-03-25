import typer
import subprocess
import httpx
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Manage the Co-Op Gateway (Docker Stack)")
console = Console()

COMPOSE_FILE = Path(__file__).parent.parent.parent.parent / "infrastructure" / "docker" / "docker-compose.yml"

@app.command()
def start():
    """Start all Co-Op services using Docker Compose."""
    console.print("[bold blue]🚀 Starting Co-Op Gateway...[/bold blue]")
    try:
        subprocess.run(["docker", "compose", "-f", str(COMPOSE_FILE), "up", "-d"], check=True)
        console.print("[bold green]✅ Services are starting in the background.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]❌ Failed to start services: {e}[/bold red]")

@app.command()
def stop():
    """Stop all Co-Op services."""
    console.print("[bold yellow]🛑 Stopping Co-Op Gateway...[/bold yellow]")
    try:
        subprocess.run(["docker", "compose", "-f", str(COMPOSE_FILE), "down"], check=True)
        console.print("[bold green]✅ Services stopped.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]❌ Failed to stop services: {e}[/bold red]")

@app.command()
def status(
    json: bool = typer.Option(False, "--json", help="Output status in JSON format for machine reading")
):
    """Check status of services and API health."""
    if not json:
        console.print("[bold blue]🔍 Checking Gateway Status...[/bold blue]")
    
    status_data = {
        "containers": [],
        "api": {"healthy": False, "services": {}}
    }

    # Check Docker containers
    try:
        res = subprocess.run(["docker", "compose", "-f", str(COMPOSE_FILE), "ps", "--format", "json"], capture_output=True, text=True)
        if json:
            import json as json_lib
            # Docker ps format can be multiple lines of JSON or a single array
            try:
                status_data["containers"] = json_lib.loads(res.stdout)
            except:
                # Fallback for older versions or line-delimited JSON
                status_data["containers"] = [json_lib.loads(l) for l in res.stdout.splitlines() if l.strip()]
        else:
            console.print("[dim]Container Status:[/dim]")
            subprocess.run(["docker", "compose", "-f", str(COMPOSE_FILE), "ps"])
    except Exception as e:
        if not json:
            console.print(f"[bold red]❌ Docker check failed: {e}[/bold red]")

    # Check API Health
    if not json:
        console.print("\n[dim]API Health Check (http://localhost:8000/health):[/dim]")
    
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get("http://localhost:8000/health")
            if resp.status_code == 200:
                health = resp.json()
                status_data["api"]["healthy"] = True
                status_data["api"]["services"] = health.get("services", {})
                if not json:
                    console.print(f"[bold green]✅ API is Healthy[/bold green]")
                    for svc, s in health.get("services", {}).items():
                        color = "green" if s == "healthy" else "red"
                        console.print(f"  - {svc}: [{color}]{s}[/{color}]")
            else:
                if not json:
                    console.print(f"[bold red]❌ API returned status {resp.status_code}[/bold red]")
    except Exception as e:
        if not json:
            console.print(f"[bold red]❌ API is unreachable: {e}[/bold red]")

    if json:
        import json as json_lib
        console.print(json_lib.dumps(status_data))
