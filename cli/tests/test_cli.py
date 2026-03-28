import os
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


class TestCLIMain:
    """Tests for main CLI entry point."""

    def test_cli_help(self):
        """Test CLI help command."""
        res = run_coop(["--help"])
        assert res.returncode == 0
        assert "Co-Op Autonomous Company OS" in res.stdout

    def test_cli_version(self):
        """Test CLI version display."""
        res = run_coop(["--version"])
        # Should show version or help
        assert res.returncode == 0 or "version" in res.stdout.lower()

    def test_cli_no_args(self):
        """Test CLI with no arguments shows help."""
        res = run_coop([])
        assert res.returncode == 0
        assert "Co-Op" in res.stdout or "Usage" in res.stdout


class TestCLIDoctorCommand:
    """Tests for doctor command integration."""

    def test_cli_doctor(self):
        """Test doctor command runs."""
        res = run_coop(["doctor", "check"])
        # Doctor might fail if no .env exists, but should return clean output
        assert "Co-Op Doctor" in res.stdout or "System Diagnostic" in res.stdout

    def test_cli_doctor_help(self):
        """Test doctor help command."""
        res = run_coop(["doctor", "--help"])
        assert res.returncode == 0
        assert "diagnostic" in res.stdout.lower() or "health" in res.stdout.lower()


class TestCLIGatewayCommand:
    """Tests for gateway command integration."""

    def test_cli_gateway_status(self):
        """Test gateway status command."""
        res = run_coop(["gateway", "status"])
        # Should show status output or error
        assert "Gateway" in res.stdout or "status" in res.stdout.lower()

    def test_cli_gateway_help(self):
        """Test gateway help command."""
        res = run_coop(["gateway", "--help"])
        assert res.returncode == 0
        assert "gateway" in res.stdout.lower() or "docker" in res.stdout.lower()

    def test_cli_gateway_start_help(self):
        """Test gateway start help."""
        res = run_coop(["gateway", "start", "--help"])
        assert res.returncode == 0
        assert "start" in res.stdout.lower()

    def test_cli_gateway_stop_help(self):
        """Test gateway stop help."""
        res = run_coop(["gateway", "stop", "--help"])
        assert res.returncode == 0
        assert "stop" in res.stdout.lower()


class TestCLIOnboardCommand:
    """Tests for onboard command integration."""

    def test_cli_onboard_help(self):
        """Test onboard help command."""
        res = run_coop(["onboard", "--help"])
        assert res.returncode == 0
        assert "setup" in res.stdout

    def test_cli_onboard_setup_help(self):
        """Test onboard setup help."""
        res = run_coop(["onboard", "setup", "--help"])
        assert res.returncode == 0


class TestCLIBackupCommand:
    """Tests for backup command integration."""

    def test_cli_backup_help(self):
        """Test backup help command."""
        res = run_coop(["backup", "--help"])
        assert res.returncode == 0
        assert "backup" in res.stdout.lower()

    def test_cli_backup_create_help(self):
        """Test backup create help."""
        res = run_coop(["backup", "create", "--help"])
        assert res.returncode == 0
        assert "create" in res.stdout.lower() or "backup" in res.stdout.lower()


class TestCLIErrorHandling:
    """Tests for CLI error handling."""

    def test_cli_invalid_command(self):
        """Test CLI with invalid command."""
        res = run_coop(["invalid-command"])
        assert res.returncode != 0 or "Error" in res.stderr or "Usage" in res.stdout

    def test_cli_invalid_subcommand(self):
        """Test CLI with invalid subcommand."""
        res = run_coop(["gateway", "invalid-subcommand"])
        assert res.returncode != 0 or "Error" in res.stderr or "Usage" in res.stdout


class TestCLIEnvironmentVariables:
    """Tests for environment variable handling."""

    def test_cli_custom_api_url(self, monkeypatch):
        """Test CLI respects COOP_API_URL environment variable."""
        monkeypatch.setenv("COOP_API_URL", "http://custom-api:9000")
        res = run_coop(["gateway", "status"])
        # Should run without error (actual connection may fail)
        assert res.returncode == 0 or "custom-api" in res.stdout

    def test_cli_custom_compose_path(self, monkeypatch, tmp_path):
        """Test CLI respects COOP_COMPOSE_PATH environment variable."""
        compose_file = tmp_path / "custom-compose.yml"
        compose_file.touch()
        monkeypatch.setenv("COOP_COMPOSE_PATH", str(compose_file))
        res = run_coop(["gateway", "status"])
        # Should run without error
        assert res.returncode == 0 or "compose" in res.stdout.lower()


class TestCLIOutputFormatting:
    """Tests for CLI output formatting."""

    def test_cli_help_formatting(self):
        """Test CLI help output is well-formatted."""
        res = run_coop(["--help"])
        assert res.returncode == 0
        # Should have proper formatting
        assert len(res.stdout) > 0
        assert "\n" in res.stdout  # Multi-line output

    def test_cli_command_help_formatting(self):
        """Test command help output is well-formatted."""
        res = run_coop(["gateway", "--help"])
        assert res.returncode == 0
        assert len(res.stdout) > 0
        assert "\n" in res.stdout


class TestCLIIntegration:
    """Integration tests for CLI commands."""

    def test_cli_command_chain(self):
        """Test running multiple CLI commands in sequence."""
        # Run help
        res1 = run_coop(["--help"])
        assert res1.returncode == 0

        # Run gateway status
        res2 = run_coop(["gateway", "status"])
        # Should complete (may fail if services not running)
        assert res2.returncode == 0 or len(res2.stdout) > 0

        # Run doctor check
        res3 = run_coop(["doctor", "check"])
        # Should complete
        assert len(res3.stdout) > 0

    def test_cli_all_commands_accessible(self):
        """Test all main commands are accessible."""
        commands = ["gateway", "doctor", "onboard", "backup"]
        for cmd in commands:
            res = run_coop([cmd, "--help"])
            assert res.returncode == 0, f"Command {cmd} failed"
            assert len(res.stdout) > 0, f"Command {cmd} produced no output"
