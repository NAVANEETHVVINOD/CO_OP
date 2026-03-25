import typer
import subprocess
import os
from pathlib import Path
from rich.console import Console

console = Console()

def run_test():
    """Run the 'Gold Path' E2E test suite."""
    console.print("[bold blue]🧪 Running Gold Path E2E Verification...[/bold blue]")
    
    test_script = Path(__file__).parent.parent.parent.parent / "services" / "api" / "scripts" / "gold_path_test.py"
    
    if not test_script.exists():
        console.print(f"[bold red]❌ Test script not found at {test_script}[/bold red]")
        raise typer.Exit(code=1)

    try:
        # We try to run it via docker exec if possible, otherwise locally
        console.print("[dim]Attempting to run inside 'co-op-api' container...[/dim]")
        res = subprocess.run([
            "docker", "exec", "co-op-api", 
            "python", "app/scripts/gold_path_test.py"
        ], capture_output=True, text=True)
        
        if res.returncode == 0:
            console.print(res.stdout)
            console.print("[bold green]✅ E2E Test Passed![/bold green]")
        else:
            console.print("[yellow]⚠️ Container run failed, trying local execution...[/yellow]")
            res = subprocess.run(["python", str(test_script)], capture_output=True, text=True)
            console.print(res.stdout)
            if res.returncode == 0:
                console.print("[bold green]✅ E2E Test Passed (Local)![/bold green]")
            else:
                console.print(f"[bold red]❌ E2E Test Failed (Local). Error: {res.stderr}[/bold red]")
                
    except Exception as e:
        console.print(f"[bold red]❌ Execution error: {e}[/bold red]")
