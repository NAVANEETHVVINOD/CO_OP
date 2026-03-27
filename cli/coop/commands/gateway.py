import typer
import subprocess
import httpx
import os
from pathlib import Path
from rich.console import Console

app = typer.Typer(help="Manage the Co-Op Gateway (Docker Stack)")
console = Console()

# Configurable paths via environment variables
DEFAULT_COMPOSE = Path(__file__).parent.parent.parent.parent / "infrastructure" / "docker" / "docker-compose.yml"
COMPOSE_FILE = Path(os.getenv("COOP_COMPOSE_PATH", str(DEFAULT_COMPOSE)))

DEFAULT_ENV = Path(__file__).parent.parent.parent.parent / "infrastructure" / "docker" / ".env"
ENV_FILE = Path(os.getenv("COOP_ENV_FILE", str(DEFAULT_ENV)))

API_URL = os.getenv("COOP_API_URL", "http://localhost:8000")

@app.command()
def start():
    """Start all Co-Op services using Docker Compose."""
    if not COMPOSE_FILE.exists():
        console.print(f"[bold red]ERROR: Compose file not found: {COMPOSE_FILE}[/bold red]")
        console.print("[dim]Set COOP_COMPOSE_PATH environment variable to override[/dim]")
        raise typer.Exit(1)
    
    if not ENV_FILE.exists():
        console.print(f"[bold yellow]WARNING: .env file not found: {ENV_FILE}[/bold yellow]")
        console.print("[dim]Set COOP_ENV_FILE environment variable to override[/dim]")
    
    console.print("[bold blue]Starting Co-Op Gateway...[/bold blue]")
    console.print(f"[dim]Compose file: {COMPOSE_FILE}[/dim]")
    console.print(f"[dim]Env file: {ENV_FILE}[/dim]")
    
    try:
        subprocess.run(
            ["docker", "compose", "-f", str(COMPOSE_FILE), "--env-file", str(ENV_FILE), "up", "-d"],
            check=True
        )
        console.print("[bold green]SUCCESS: Services are starting in the background.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]ERROR: Failed to start services: {e}[/bold red]")
        raise typer.Exit(1)

@app.command()
def stop():
    """Stop all Co-Op services."""
    if not COMPOSE_FILE.exists():
        console.print(f"[bold red]ERROR: Compose file not found: {COMPOSE_FILE}[/bold red]")
        console.print("[dim]Set COOP_COMPOSE_PATH environment variable to override[/dim]")
        raise typer.Exit(1)
    
    console.print("[bold yellow]Stopping Co-Op Gateway...[/bold yellow]")
    console.print(f"[dim]Compose file: {COMPOSE_FILE}[/dim]")
    
    try:
        subprocess.run(["docker", "compose", "-f", str(COMPOSE_FILE), "down"], check=True)
        console.print("[bold green]SUCCESS: Services stopped.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]ERROR: Failed to stop services: {e}[/bold red]")
        raise typer.Exit(1)

@app.command()
def status(
    json: bool = typer.Option(False, "--json", help="Output status in JSON format for machine reading")
):
    """Check status of services and API health."""
    if not COMPOSE_FILE.exists():
        console.print(f"[bold red]ERROR: Compose file not found: {COMPOSE_FILE}[/bold red]")
        console.print("[dim]Set COOP_COMPOSE_PATH environment variable to override[/dim]")
        raise typer.Exit(1)
    
    if not json:
        console.print("[bold blue]Checking Gateway Status...[/bold blue]")
    
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
            except Exception:
                # Fallback for older versions or line-delimited JSON
                status_data["containers"] = [json_lib.loads(line) for line in res.stdout.splitlines() if line.strip()]
        else:
            console.print("[dim]Container Status:[/dim]")
            subprocess.run(["docker", "compose", "-f", str(COMPOSE_FILE), "ps"])
    except Exception as e:
        if not json:
            console.print(f"[bold red]ERROR: Docker check failed: {e}[/bold red]")

    # Check API Health
    if not json:
        console.print(f"\n[dim]API Health Check ({API_URL}/health):[/dim]")
    
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{API_URL}/health")
            if resp.status_code == 200:
                health = resp.json()
                status_data["api"]["healthy"] = True
                status_data["api"]["services"] = health.get("services", {})
                if not json:
                    console.print("[bold green]SUCCESS: API is Healthy[/bold green]")
                    for svc, s in health.get("services", {}).items():
                        color = "green" if s == "healthy" else "red"
                        console.print(f"  - {svc}: [{color}]{s}[/{color}]")
            else:
                if not json:
                    console.print(f"[bold red]ERROR: API returned status {resp.status_code}[/bold red]")
    except Exception as e:
        if not json:
            console.print(f"[bold red]ERROR: API is unreachable: {e}[/bold red]")

    if json:
        import json as json_lib
        console.print(json_lib.dumps(status_data))
