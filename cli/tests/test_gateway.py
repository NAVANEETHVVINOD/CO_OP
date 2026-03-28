"""Tests for gateway command."""
import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from coop.commands.gateway import app

runner = CliRunner()


class TestGatewayStart:
    """Tests for gateway start command."""

    @patch("coop.commands.gateway.subprocess.run")
    @patch("coop.commands.gateway.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    @patch("coop.commands.gateway.ENV_FILE", Path("/fake/.env"))
    def test_start_success(self, mock_run, tmp_path):
        """Test successful gateway start."""
        # Create fake files
        compose_file = tmp_path / "docker-compose.yml"
        env_file = tmp_path / ".env"
        compose_file.touch()
        env_file.touch()

        with patch("coop.commands.gateway.COMPOSE_FILE", compose_file):
            with patch("coop.commands.gateway.ENV_FILE", env_file):
                mock_run.return_value = MagicMock(returncode=0)
                result = runner.invoke(app, ["start"])

                assert result.exit_code == 0
                assert "Starting Co-Op Gateway" in result.stdout
                assert "SUCCESS" in result.stdout
                mock_run.assert_called_once()

    @patch("coop.commands.gateway.COMPOSE_FILE", Path("/nonexistent/docker-compose.yml"))
    def test_start_missing_compose_file(self):
        """Test start fails when compose file is missing."""
        result = runner.invoke(app, ["start"])
        assert result.exit_code == 1
        assert "ERROR: Compose file not found" in result.stdout

    @patch("coop.commands.gateway.subprocess.run")
    @patch("coop.commands.gateway.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    @patch("coop.commands.gateway.ENV_FILE", Path("/fake/.env"))
    def test_start_docker_failure(self, mock_run, tmp_path):
        """Test start handles Docker command failure."""
        compose_file = tmp_path / "docker-compose.yml"
        env_file = tmp_path / ".env"
        compose_file.touch()
        env_file.touch()

        with patch("coop.commands.gateway.COMPOSE_FILE", compose_file):
            with patch("coop.commands.gateway.ENV_FILE", env_file):
                mock_run.side_effect = subprocess.CalledProcessError(1, "docker")
                result = runner.invoke(app, ["start"])

                assert result.exit_code == 1
                assert "ERROR: Failed to start services" in result.stdout

    @patch("coop.commands.gateway.subprocess.run")
    @patch("coop.commands.gateway.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    def test_start_missing_env_file_warning(self, mock_run, tmp_path):
        """Test start shows warning when .env file is missing."""
        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        with patch("coop.commands.gateway.COMPOSE_FILE", compose_file):
            with patch("coop.commands.gateway.ENV_FILE", Path("/nonexistent/.env")):
                mock_run.return_value = MagicMock(returncode=0)
                result = runner.invoke(app, ["start"])

                assert "WARNING: .env file not found" in result.stdout


class TestGatewayStop:
    """Tests for gateway stop command."""

    @patch("coop.commands.gateway.subprocess.run")
    @patch("coop.commands.gateway.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    def test_stop_success(self, mock_run, tmp_path):
        """Test successful gateway stop."""
        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        with patch("coop.commands.gateway.COMPOSE_FILE", compose_file):
            mock_run.return_value = MagicMock(returncode=0)
            result = runner.invoke(app, ["stop"])

            assert result.exit_code == 0
            assert "Stopping Co-Op Gateway" in result.stdout
            assert "SUCCESS: Services stopped" in result.stdout
            mock_run.assert_called_once()

    @patch("coop.commands.gateway.COMPOSE_FILE", Path("/nonexistent/docker-compose.yml"))
    def test_stop_missing_compose_file(self):
        """Test stop fails when compose file is missing."""
        result = runner.invoke(app, ["stop"])
        assert result.exit_code == 1
        assert "ERROR: Compose file not found" in result.stdout

    @patch("coop.commands.gateway.subprocess.run")
    @patch("coop.commands.gateway.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    def test_stop_docker_failure(self, mock_run, tmp_path):
        """Test stop handles Docker command failure."""
        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        with patch("coop.commands.gateway.COMPOSE_FILE", compose_file):
            mock_run.side_effect = subprocess.CalledProcessError(1, "docker")
            result = runner.invoke(app, ["stop"])

            assert result.exit_code == 1
            assert "ERROR: Failed to stop services" in result.stdout


class TestGatewayStatus:
    """Tests for gateway status command."""

    @patch("coop.commands.gateway.httpx.Client")
    @patch("coop.commands.gateway.subprocess.run")
    @patch("coop.commands.gateway.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    def test_status_all_healthy(self, mock_run, mock_client, tmp_path):
        """Test status shows all services healthy."""
        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        # Mock Docker ps output
        mock_run.return_value = MagicMock(
            stdout='[{"Name":"co-op-api","State":"running"}]',
            returncode=0
        )

        # Mock API health check
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "healthy",
            "services": {
                "postgres": "healthy",
                "redis": "healthy",
                "qdrant": "healthy",
                "minio": "healthy"
            }
        }
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        with patch("coop.commands.gateway.COMPOSE_FILE", compose_file):
            result = runner.invoke(app, ["status"])

            assert result.exit_code == 0
            assert "Checking Gateway Status" in result.stdout
            assert "SUCCESS: API is Healthy" in result.stdout

    @patch("coop.commands.gateway.httpx.Client")
    @patch("coop.commands.gateway.subprocess.run")
    @patch("coop.commands.gateway.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    def test_status_api_unreachable(self, mock_run, mock_client, tmp_path):
        """Test status handles unreachable API."""
        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        mock_run.return_value = MagicMock(stdout="", returncode=0)
        mock_client.return_value.__enter__.return_value.get.side_effect = Exception("Connection refused")

        with patch("coop.commands.gateway.COMPOSE_FILE", compose_file):
            result = runner.invoke(app, ["status"])

            assert result.exit_code == 0
            assert "ERROR: API is unreachable" in result.stdout

    @patch("coop.commands.gateway.httpx.Client")
    @patch("coop.commands.gateway.subprocess.run")
    @patch("coop.commands.gateway.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    def test_status_json_output(self, mock_run, mock_client, tmp_path):
        """Test status with JSON output format."""
        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        # Mock Docker ps output
        mock_run.return_value = MagicMock(
            stdout='[{"Name":"co-op-api","State":"running"}]',
            returncode=0
        )

        # Mock API health check
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "healthy",
            "services": {"postgres": "healthy"}
        }
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        with patch("coop.commands.gateway.COMPOSE_FILE", compose_file):
            result = runner.invoke(app, ["status", "--json"])

            assert result.exit_code == 0
            # Should contain JSON output
            output_data = json.loads(result.stdout)
            assert "containers" in output_data
            assert "api" in output_data

    @patch("coop.commands.gateway.COMPOSE_FILE", Path("/nonexistent/docker-compose.yml"))
    def test_status_missing_compose_file(self):
        """Test status fails when compose file is missing."""
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 1
        assert "ERROR: Compose file not found" in result.stdout

    @patch("coop.commands.gateway.httpx.Client")
    @patch("coop.commands.gateway.subprocess.run")
    @patch("coop.commands.gateway.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    def test_status_unhealthy_service(self, mock_run, mock_client, tmp_path):
        """Test status shows unhealthy services."""
        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        mock_run.return_value = MagicMock(stdout="", returncode=0)

        # Mock API health check with unhealthy service
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "degraded",
            "services": {
                "postgres": "healthy",
                "redis": "unhealthy"
            }
        }
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        with patch("coop.commands.gateway.COMPOSE_FILE", compose_file):
            result = runner.invoke(app, ["status"])

            assert result.exit_code == 0
            assert "redis" in result.stdout


class TestGatewayEnvironmentVariables:
    """Tests for environment variable handling."""

    @patch("coop.commands.gateway.subprocess.run")
    def test_custom_compose_path(self, mock_run, tmp_path, monkeypatch):
        """Test using custom compose path from environment."""
        compose_file = tmp_path / "custom-compose.yml"
        env_file = tmp_path / ".env"
        compose_file.touch()
        env_file.touch()

        monkeypatch.setenv("COOP_COMPOSE_PATH", str(compose_file))
        monkeypatch.setenv("COOP_ENV_FILE", str(env_file))

        # Reload module to pick up new env vars
        from importlib import reload
        from coop.commands import gateway
        reload(gateway)

        mock_run.return_value = MagicMock(returncode=0)
        result = runner.invoke(gateway.app, ["start"])

        assert result.exit_code == 0

    @patch("coop.commands.gateway.httpx.Client")
    @patch("coop.commands.gateway.subprocess.run")
    def test_custom_api_url(self, mock_run, mock_client, tmp_path, monkeypatch):
        """Test using custom API URL from environment."""
        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        custom_url = "http://custom-api:9000"
        monkeypatch.setenv("COOP_API_URL", custom_url)

        mock_run.return_value = MagicMock(stdout="", returncode=0)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy", "services": {}}
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        with patch("coop.commands.gateway.COMPOSE_FILE", compose_file):
            with patch("coop.commands.gateway.API_URL", custom_url):
                result = runner.invoke(app, ["status"])

                assert result.exit_code == 0
                # Verify custom URL was used
                mock_client.return_value.__enter__.return_value.get.assert_called_with(
                    f"{custom_url}/health"
                )
