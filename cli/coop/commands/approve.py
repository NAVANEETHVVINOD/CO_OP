import httpx
import os
from rich.console import Console

console = Console()

# Configurable API URL
API_URL = os.getenv("COOP_API_URL", "http://localhost:8000")

def approve(approval_id: str):
    """Approve a queued action by its ID."""
    console.print(f"[bold blue]👍 Approving action {approval_id}...[/bold blue]")
    
    try:
        with httpx.Client() as client:
            resp = client.post(f"{API_URL}/v1/approvals/{approval_id}/approve")
            if resp.status_code == 200:
                console.print("[bold green]✅ Action Approved.[/bold green]")
            else:
                console.print(f"[bold red]❌ Request failed ({resp.status_code}): {resp.text}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]❌ Connection error: {e}[/bold red]")
        console.print(f"[dim]API URL: {API_URL} (set COOP_API_URL to override)[/dim]")
