import typer
from rich.console import Console
from .commands import gateway, doctor, backup, approve, test, onboard

app = typer.Typer(
    name="coop",
    help="Co-Op Autonomous Company OS CLI Tool",
    add_completion=False,
)

# Add subcommands
app.add_typer(gateway.app, name="gateway")
app.add_typer(doctor.app, name="doctor")
app.add_typer(backup.app, name="backup")
app.add_typer(onboard.app, name="onboard")
app.command(name="approve")(approve.approve)
app.command(name="test")(test.run_test)

console = Console()

@app.callback()
def callback():
    """
    Control and manage your Co-Op Autonomous Company OS.
    """
    pass

if __name__ == "__main__":
    app()
