import subprocess
import sys
from pathlib import Path

# CLI root directory (cli/)
CLI_DIR = Path(__file__).parent.parent
# CLI source directory (cli/coop)
APP_DIR = CLI_DIR / "coop"

def run_coop(args):
    """Run coop CLI as a subprocess."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(CLI_DIR)
    
    # We use 'python -m coop.main' equivalent
    return subprocess.run(
        [sys.executable, "-m", "coop.main"] + args,
        capture_output=True,
        text=True,
        env=env
    )

import os

def test_cli_help():
    res = run_coop(["--help"])
    assert res.returncode == 0
    assert "Co-Op Autonomous Company OS" in res.stdout

def test_cli_doctor():
    # Note: doctor might fail if no .env exists, but should return a clean error message
    res = run_coop(["doctor"])
    # We don't necessarily assert returncode 0 as it depends on system state
    assert "Co-Op System Health" in res.stdout or "Error" in res.stderr

def test_cli_gateway_status():
    res = run_coop(["gateway", "status"])
    assert "Gateway Status" in res.stdout

def test_cli_onboard_help():
    res = run_coop(["onboard", "--help"])
    assert res.returncode == 0
    assert "setup" in res.stdout
