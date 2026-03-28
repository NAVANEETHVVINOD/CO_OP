"""Tests for doctor command."""
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from coop.commands.doctor import app

runner = CliRunner()


class TestDoctorCheck:
    """Tests for doctor check command."""

    @patch("coop.commands.doctor.httpx.Client")
    @patch("coop.commands.doctor.psutil.virtual_memory")
    @patch("coop.commands.doctor.subprocess.run")
    @patch("coop.commands.doctor.shutil.which")
    def test_check_all_healthy(self, mock_which, mock_run, mock_memory, mock_client, tmp_path):
        """Test doctor check with all systems healthy."""
        # Mock Docker installed
        mock_which.return_value = "/usr/bin/docker"
        mock_run.return_value = MagicMock(
            stdout="Docker version 24.0.0",
            returncode=0
        )

        # Mock sufficient memory (16GB)
        mock_mem = MagicMock()
        mock_mem.total = 16 * 1024 ** 3
        mock_memory.return_value = mock_mem

        # Mock .env file exists
        env_file = tmp_path / ".env"
        env_file.touch()

        # Mock API reachable
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        with patch("coop.commands.doctor.os.getcwd", return_value=str(tmp_path)):
            result = runner.invoke(app)

            assert result.exit_code == 0
            assert "Co-Op Doctor: System Diagnostic" in result.stdout
            assert "OK" in result.stdout
            assert "Docker found" in result.stdout
            assert "Memory:" in result.stdout
            assert "Root .env file found" in result.stdout
            assert "Backend API" in result.stdout
            assert "Doctor check complete" in result.stdout

    @patch("coop.commands.doctor.shutil.which")
    def test_check_docker_not_found(self, mock_which):
        """Test doctor check when Docker is not installed."""
        mock_which.return_value = None

        result = runner.invoke(app)

        assert result.exit_code == 0
        assert "ERROR" in result.stdout
        assert "Docker NOT found in PATH" in result.stdout

    @patch("coop.commands.doctor.subprocess.run")
    @patch("coop.commands.doctor.shutil.which")
    def test_check_docker_daemon_not_running(self, mock_which, mock_run):
        """Test doctor check when Docker daemon is not running."""
        mock_which.return_value = "/usr/bin/docker"
        mock_run.side_effect = Exception("Cannot connect to Docker daemon")

        result = runner.invoke(app)

        assert result.exit_code == 0
        assert "ERROR" in result.stdout
        assert "Docker is installed but daemon is not responding" in result.stdout

    @patch("coop.commands.doctor.psutil.virtual_memory")
    @patch("coop.commands.doctor.subprocess.run")
    @patch("coop.commands.doctor.shutil.which")
    def test_check_low_memory_warning(self, mock_which, mock_run, mock_memory):
        """Test doctor check shows warning for low memory."""
        mock_which.return_value = "/usr/bin/docker"
        mock_run.return_value = MagicMock(stdout="Docker version 24.0.0", returncode=0)

        # Mock low memory (4GB)
        mock_mem = MagicMock()
        mock_mem.total = 4 * 1024 ** 3
        mock_memory.return_value = mock_mem

        result = runner.invoke(app)

        assert result.exit_code == 0
        assert "WARN" in result.stdout
        assert "Low Memory" in result.stdout
        assert "Recommended: 16GB" in result.stdout

    @patch("coop.commands.doctor.psutil.virtual_memory")
    @patch("coop.commands.doctor.subprocess.run")
    @patch("coop.commands.doctor.shutil.which")
    def test_check_sufficient_memory(self, mock_which, mock_run, mock_memory):
        """Test doctor check with sufficient memory."""
        mock_which.return_value = "/usr/bin/docker"
        mock_run.return_value = MagicMock(stdout="Docker version 24.0.0", returncode=0)

        # Mock sufficient memory (16GB)
        mock_mem = MagicMock()
        mock_mem.total = 16 * 1024 ** 3
        mock_memory.return_value = mock_mem

        result = runner.invoke(app)

        assert result.exit_code == 0
        assert "OK" in result.stdout
        assert "Memory: 16.0GB" in result.stdout

    @patch("coop.commands.doctor.subprocess.run")
    @patch("coop.commands.doctor.shutil.which")
    def test_check_missing_env_file(self, mock_which, mock_run, tmp_path):
        """Test doctor check when .env file is missing."""
        mock_which.return_value = "/usr/bin/docker"
        mock_run.return_value = MagicMock(stdout="Docker version 24.0.0", returncode=0)

        with patch("coop.commands.doctor.os.getcwd", return_value=str(tmp_path)):
            result = runner.invoke(app)

            assert result.exit_code == 0
            assert "ERROR" in result.stdout
            assert "Root .env file MISSING" in result.stdout
            assert "Run setup first" in result.stdout

    @patch("coop.commands.doctor.subprocess.run")
    @patch("coop.commands.doctor.shutil.which")
    def test_check_env_file_exists(self, mock_which, mock_run, tmp_path):
        """Test doctor check when .env file exists."""
        mock_which.return_value = "/usr/bin/docker"
        mock_run.return_value = MagicMock(stdout="Docker version 24.0.0", returncode=0)

        env_file = tmp_path / ".env"
        env_file.touch()

        with patch("coop.commands.doctor.os.getcwd", return_value=str(tmp_path)):
            result = runner.invoke(app)

            assert result.exit_code == 0
            assert "OK" in result.stdout
            assert "Root .env file found" in result.stdout

    @patch("coop.commands.doctor.httpx.Client")
    @patch("coop.commands.doctor.subprocess.run")
    @patch("coop.commands.doctor.shutil.which")
    def test_check_api_reachable(self, mock_which, mock_run, mock_client):
        """Test doctor check when API is reachable."""
        mock_which.return_value = "/usr/bin/docker"
        mock_run.return_value = MagicMock(stdout="Docker version 24.0.0", returncode=0)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = runner.invoke(app)

        assert result.exit_code == 0
        assert "OK" in result.stdout
        assert "Backend API" in result.stdout
        assert "is reachable" in result.stdout

    @patch("coop.commands.doctor.httpx.Client")
    @patch("coop.commands.doctor.subprocess.run")
    @patch("coop.commands.doctor.shutil.which")
    def test_check_api_unreachable(self, mock_which, mock_run, mock_client):
        """Test doctor check when API is unreachable."""
        mock_which.return_value = "/usr/bin/docker"
        mock_run.return_value = MagicMock(stdout="Docker version 24.0.0", returncode=0)

        mock_client.return_value.__enter__.return_value.get.side_effect = Exception("Connection refused")

        result = runner.invoke(app)

        assert result.exit_code == 0
        assert "WARN" in result.stdout
        assert "Backend API" in result.stdout
        assert "unreachable" in result.stdout

    @patch("coop.commands.doctor.httpx.Client")
    @patch("coop.commands.doctor.subprocess.run")
    @patch("coop.commands.doctor.shutil.which")
    def test_check_custom_api_url(self, mock_which, mock_run, mock_client, monkeypatch):
        """Test doctor check with custom API URL."""
        mock_which.return_value = "/usr/bin/docker"
        mock_run.return_value = MagicMock(stdout="Docker version 24.0.0", returncode=0)

        custom_url = "http://custom-api:9000"
        monkeypatch.setenv("COOP_API_URL", custom_url)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        with patch("coop.commands.doctor.API_URL", custom_url):
            result = runner.invoke(app)

            assert result.exit_code == 0
            assert custom_url in result.stdout

    @patch("coop.commands.doctor.psutil.virtual_memory")
    @patch("coop.commands.doctor.subprocess.run")
    @patch("coop.commands.doctor.shutil.which")
    def test_check_memory_calculation(self, mock_which, mock_run, mock_memory):
        """Test doctor check memory calculation accuracy."""
        mock_which.return_value = "/usr/bin/docker"
        mock_run.return_value = MagicMock(stdout="Docker version 24.0.0", returncode=0)

        # Mock 8GB memory
        mock_mem = MagicMock()
        mock_mem.total = 8 * 1024 ** 3
        mock_memory.return_value = mock_mem

        result = runner.invoke(app)

        assert result.exit_code == 0
        assert "Memory: 8.0GB" in result.stdout

    @patch("coop.commands.doctor.httpx.Client")
    @patch("coop.commands.doctor.psutil.virtual_memory")
    @patch("coop.commands.doctor.subprocess.run")
    @patch("coop.commands.doctor.shutil.which")
    def test_check_complete_flow(self, mock_which, mock_run, mock_memory, mock_client, tmp_path):
        """Test complete doctor check flow with all checks."""
        # Setup all mocks for successful check
        mock_which.return_value = "/usr/bin/docker"
        mock_run.return_value = MagicMock(stdout="Docker version 24.0.0", returncode=0)

        mock_mem = MagicMock()
        mock_mem.total = 16 * 1024 ** 3
        mock_memory.return_value = mock_mem

        env_file = tmp_path / ".env"
        env_file.touch()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        with patch("coop.commands.doctor.os.getcwd", return_value=str(tmp_path)):
            result = runner.invoke(app)

            # Verify all checks are performed
            assert result.exit_code == 0
            assert "Docker found" in result.stdout
            assert "Memory:" in result.stdout
            assert ".env file found" in result.stdout
            assert "Backend API" in result.stdout
            assert "Doctor check complete" in result.stdout

    @patch("coop.commands.doctor.subprocess.run")
    @patch("coop.commands.doctor.shutil.which")
    def test_check_docker_version_output(self, mock_which, mock_run):
        """Test doctor check displays Docker version."""
        mock_which.return_value = "/usr/bin/docker"
        mock_run.return_value = MagicMock(
            stdout="Docker version 24.0.5, build abc123",
            returncode=0
        )

        result = runner.invoke(app)

        assert result.exit_code == 0
        assert "Docker version 24.0.5" in result.stdout

    @patch("coop.commands.doctor.httpx.Client")
    @patch("coop.commands.doctor.subprocess.run")
    @patch("coop.commands.doctor.shutil.which")
    def test_check_api_timeout(self, mock_which, mock_run, mock_client):
        """Test doctor check handles API timeout gracefully."""
        mock_which.return_value = "/usr/bin/docker"
        mock_run.return_value = MagicMock(stdout="Docker version 24.0.0", returncode=0)

        # Mock timeout exception
        import httpx
        mock_client.return_value.__enter__.return_value.get.side_effect = httpx.TimeoutException("Request timeout")

        result = runner.invoke(app)

        assert result.exit_code == 0
        assert "WARN" in result.stdout
        assert "unreachable" in result.stdout

    @patch("coop.commands.doctor.httpx.Client")
    @patch("coop.commands.doctor.subprocess.run")
    @patch("coop.commands.doctor.shutil.which")
    def test_check_api_connection_error(self, mock_which, mock_run, mock_client):
        """Test doctor check handles connection errors."""
        mock_which.return_value = "/usr/bin/docker"
        mock_run.return_value = MagicMock(stdout="Docker version 24.0.0", returncode=0)

        # Mock connection error
        import httpx
        mock_client.return_value.__enter__.return_value.get.side_effect = httpx.ConnectError("Connection failed")

        result = runner.invoke(app)

        assert result.exit_code == 0
        assert "WARN" in result.stdout
        assert "unreachable" in result.stdout

    @patch("coop.commands.doctor.psutil.virtual_memory")
    @patch("coop.commands.doctor.subprocess.run")
    @patch("coop.commands.doctor.shutil.which")
    def test_check_edge_case_memory_threshold(self, mock_which, mock_run, mock_memory):
        """Test doctor check at exact memory threshold (8GB)."""
        mock_which.return_value = "/usr/bin/docker"
        mock_run.return_value = MagicMock(stdout="Docker version 24.0.0", returncode=0)

        # Mock exactly 8GB memory (threshold)
        mock_mem = MagicMock()
        mock_mem.total = 8 * 1024 ** 3
        mock_memory.return_value = mock_mem

        result = runner.invoke(app)

        assert result.exit_code == 0
        # At 8GB, should show OK (not low)
        assert "Memory: 8.0GB" in result.stdout

    @patch("coop.commands.doctor.psutil.virtual_memory")
    @patch("coop.commands.doctor.subprocess.run")
    @patch("coop.commands.doctor.shutil.which")
    def test_check_very_low_memory(self, mock_which, mock_run, mock_memory):
        """Test doctor check with very low memory (2GB)."""
        mock_which.return_value = "/usr/bin/docker"
        mock_run.return_value = MagicMock(stdout="Docker version 24.0.0", returncode=0)

        # Mock very low memory (2GB)
        mock_mem = MagicMock()
        mock_mem.total = 2 * 1024 ** 3
        mock_memory.return_value = mock_mem

        result = runner.invoke(app)

        assert result.exit_code == 0
        assert "WARN" in result.stdout
        assert "Low Memory: 2.0GB" in result.stdout

    @patch("coop.commands.doctor.subprocess.run")
    @patch("coop.commands.doctor.shutil.which")
    def test_check_docker_version_parsing(self, mock_which, mock_run):
        """Test doctor check handles various Docker version formats."""
        mock_which.return_value = "/usr/bin/docker"
        
        # Test with different version formats
        version_formats = [
            "Docker version 20.10.21, build baeda1f",
            "Docker version 24.0.0",
            "Docker version 25.0.0-rc.1, build 1234567"
        ]
        
        for version_str in version_formats:
            mock_run.return_value = MagicMock(stdout=version_str, returncode=0)
            result = runner.invoke(app)
            assert result.exit_code == 0
            assert "Docker found" in result.stdout

    @patch("coop.commands.doctor.subprocess.run")
    @patch("coop.commands.doctor.shutil.which")
    def test_check_docker_command_failure(self, mock_which, mock_run):
        """Test doctor check when docker --version command fails."""
        mock_which.return_value = "/usr/bin/docker"
        mock_run.return_value = MagicMock(
            stdout="",
            stderr="permission denied",
            returncode=1
        )

        result = runner.invoke(app)

        assert result.exit_code == 0
        # Should still complete but may show error

    @patch("coop.commands.doctor.httpx.Client")
    @patch("coop.commands.doctor.psutil.virtual_memory")
    @patch("coop.commands.doctor.subprocess.run")
    @patch("coop.commands.doctor.shutil.which")
    def test_check_all_failures(self, mock_which, mock_run, mock_memory, mock_client, tmp_path):
        """Test doctor check when all systems fail."""
        # Docker not found
        mock_which.return_value = None
        
        # Low memory
        mock_mem = MagicMock()
        mock_mem.total = 2 * 1024 ** 3
        mock_memory.return_value = mock_mem
        
        # No .env file (tmp_path is empty)
        
        # API unreachable
        mock_client.return_value.__enter__.return_value.get.side_effect = Exception("Connection failed")

        with patch("coop.commands.doctor.os.getcwd", return_value=str(tmp_path)):
            result = runner.invoke(app)

            # Should complete but show multiple errors
            assert result.exit_code == 0
            assert "ERROR" in result.stdout or "WARN" in result.stdout
            assert "Doctor check complete" in result.stdout

    @patch("coop.commands.doctor.subprocess.run")
    @patch("coop.commands.doctor.shutil.which")
    def test_check_env_file_permissions(self, mock_which, mock_run, tmp_path):
        """Test doctor check with .env file that exists but may have permission issues."""
        mock_which.return_value = "/usr/bin/docker"
        mock_run.return_value = MagicMock(stdout="Docker version 24.0.0", returncode=0)

        # Create .env file
        env_file = tmp_path / ".env"
        env_file.write_text("TEST=value")

        with patch("coop.commands.doctor.os.getcwd", return_value=str(tmp_path)):
            result = runner.invoke(app)

            assert result.exit_code == 0
            assert "OK" in result.stdout
            assert ".env file found" in result.stdout
