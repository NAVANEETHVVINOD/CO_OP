import typer
import subprocess
import os
import psutil
import shutil
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(help="System diagnostics and environment check")
console = Console()

# Configurable API URL
API_URL = os.getenv("COOP_API_URL", "http://localhost:8000")

@app.command()
def check():
    """Run full system diagnostics."""
    console.print(Panel("[bold blue]Co-Op Doctor: System Diagnostic[/bold blue]"))
    
    # 1. Check Docker
    docker_bin = shutil.which("docker")
    if docker_bin:
        try:
            res = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            console.print(f"[green]OK[/green] Docker found: [dim]{res.stdout.strip()}[/dim]")
        except Exception:
            console.print("[red]ERROR[/red] Docker is installed but daemon is not responding.")
    else:
        console.print("[red]ERROR[/red] Docker NOT found in PATH.")

    # 2. Check Resources
    mem = psutil.virtual_memory()
    mem_gb = mem.total / (1024**3)
    if mem_gb < 8:
        console.print(f"[yellow]WARN[/yellow] Low Memory: {mem_gb:.1f}GB (Recommended: 16GB for LLM workloads)")
    else:
        console.print(f"[green]OK[/green] Memory: {mem_gb:.1f}GB")

    # 3. Check Environment Variables
    root_env = os.path.join(os.getcwd(), ".env")
    if os.path.exists(root_env):
        console.print("[green]OK[/green] Root .env file found.")
    else:
        console.print("[red]ERROR[/red] Root .env file MISSING. Run setup first.")

    # 4. Check API Connectivity
    try:
        import httpx
        with httpx.Client(timeout=2.0) as client:
            client.get(f"{API_URL}/health")
            console.print(f"[green]OK[/green] Backend API ({API_URL}) is reachable.")
    except Exception:
        console.print(f"[yellow]WARN[/yellow] Backend API ({API_URL}) unreachable (gateway might be stopped).")
        console.print("[dim]Set COOP_API_URL environment variable to override[/dim]")

    console.print("\n[bold green]Doctor check complete.[/bold green]")
