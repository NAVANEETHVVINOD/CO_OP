import typer
import httpx
import os
from rich.console import Console

console = Console()

def approve(approval_id: str):
    """Approve a queued action by its ID."""
    console.print(f"[bold blue]👍 Approving action {approval_id}...[/bold blue]")
    
    # In a real CLI, we would use a stored token or prompt for one
    api_url = os.getenv("NEXT_PUBLIC_API_URL", "http://localhost:8000")
    
    try:
        with httpx.Client() as client:
            resp = client.post(f"{api_url}/v1/approvals/{approval_id}/approve")
            if resp.status_code == 200:
                console.print(f"[bold green]✅ Action Approved.[/bold green]")
            else:
                console.print(f"[bold red]❌ Request failed ({resp.status_code}): {resp.text}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]❌ Connection error: {e}[/bold red]")
