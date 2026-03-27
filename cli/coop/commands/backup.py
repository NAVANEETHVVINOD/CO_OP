import typer
import subprocess
import datetime
import os
from pathlib import Path
from rich.console import Console

app = typer.Typer(help="Backup database and snapshots")
console = Console()

BACKUP_DIR = Path("backups")

# Configurable compose path
DEFAULT_COMPOSE = Path(__file__).parent.parent.parent.parent / "infrastructure" / "docker" / "docker-compose.yml"
COMPOSE_FILE = Path(os.getenv("COOP_COMPOSE_PATH", str(DEFAULT_COMPOSE)))

@app.command()
def create():
    """Create a full system backup (Postgres, Qdrant, MinIO)."""
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    console.print(f"[bold blue]💾 Creating backup: {timestamp}...[/bold blue]")

    # 1. Postgres Dump
    try:
        console.print(" - Backing up PostgreSQL...")
        # Note: This assumes container 'co-op-db' is running
        subprocess.run([
            "docker", "exec", "co-op-db", 
            "pg_dump", "-U", "postgres", "co_op"
        ], stdout=open(BACKUP_DIR / f"db_{timestamp}.sql", "w"), check=True)
        console.print("   ✅ Postgres dump complete.")
    except Exception as e:
        console.print(f"   ❌ Postgres backup failed: {e}")

    # 2. Qdrant Snapshot
    try:
        console.print(" - Creating Qdrant Snapshot...")
        # Simple placeholder for Stage 3
        console.print("   ⚠️ Qdrant snapshotting via API not yet implemented in CLI.")
    except Exception as e:
        console.print(f"   ⚠️ Qdrant snapshot failed: {e}")

    # 3. MinIO Sync
    try:
        console.print(" - Syncing MinIO artifacts...")
        # Placeholder
        console.print("   ⚠️ MinIO sync not yet implemented in CLI.")
    except Exception as e:
        console.print(f"   ⚠️ MinIO sync failed: {e}")

    console.print(f"\n[bold green]✅ Backup stored in {BACKUP_DIR}/[/bold green]")
