import typer
import secrets
import string
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
import httpx

app = typer.Typer(help="Interactive onboarding for Co-Op OS")
console = Console()

ROOT_DIR = Path(__file__).parent.parent.parent.parent
ENV_PATH = ROOT_DIR / ".env"

@app.command()
def setup():
    """Run the interactive onboarding wizard to configure Co-Op."""
    console.print("[bold blue]🌟 Welcome to Co-Op Autonomous Company OS Onboarding! 🌟[/bold blue]")
    
    if ENV_PATH.exists():
        if not Confirm.ask("An .env file already exists. Overwrite it?"):
            console.print("[yellow]Onboarding cancelled.[/yellow]")
            return

    # 1. Generate Secrets
    secret_key = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    db_pass = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))

    # 2. Gather User Input
    console.print("\n[bold]--- Configuration ---[/bold]")
    telegram_token = Prompt.ask("Enter your Telegram Bot Token (optional)", default="")
    
    if telegram_token:
        console.print("[yellow]Testing Telegram connection...[/yellow]")
        try:
            response = httpx.get(f"https://api.telegram.org/bot{telegram_token}/getMe", timeout=10.0)
            if response.status_code == 200:
                bot_name = response.json().get("result", {}).get("first_name", "Bot")
                console.print(f"[bold green]✅ Connected to {bot_name}[/bold green]")
            else:
                console.print("[bold red]❌ Invalid Telegram Token. Continuing anyway...[/bold red]")
        except Exception as e:
            console.print(f"[bold yellow]⚠️ Could not verify Telegram Token: {e}[/bold yellow]")

    sentry_dsn = Prompt.ask("Enter your Sentry DSN (optional)", default="")
    environment = Prompt.ask("Environment", choices=["local", "production"], default="local")

    # 3. Construct .env content
    env_content = f"""# Co-Op OS Environment Configuration
DB_PASS={db_pass}
DATABASE_URL=postgresql+asyncpg://coop:{db_pass}@localhost:5433/coop
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
LITELLM_URL=http://localhost:4000
SECRET_KEY={secret_key}
MINIO_URL=localhost:9000
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
ENVIRONMENT={environment}
TELEGRAM_BOT_TOKEN={telegram_token}
SENTRY_DSN={sentry_dsn}
NEXT_PUBLIC_API_URL=http://localhost:8000
"""

    try:
        with open(ENV_PATH, "w") as f:
            f.write(env_content)
        console.print(f"\n[bold green]✅ .env file created at {ENV_PATH}[/bold green]")
    except Exception as e:
        console.print(f"\n[bold red]❌ Failed to create .env file: {e}[/bold red]")
        return

    console.print("\n[bold green]🌟 Onboarding complete! 🌟[/bold green]")
    
    if Confirm.ask("Would you like to start the Co-Op Gateway now?"):
        console.print("[blue]Starting gateway...[/blue]")
        from .gateway import start
        start()
        console.print("\n[bold green]✅ Gateway started! Access your dashboard at http://localhost:3000[/bold green]")
    else:
        console.print("\n[bold blue]Next steps:[/bold blue]")
        console.print("1. Run [bold green]coop gateway start[/bold green] to launch services.")
        console.print("2. Run [bold green]coop gateway status[/bold green] to check health.")
