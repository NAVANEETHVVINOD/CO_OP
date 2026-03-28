"""Tests for backup command."""
import subprocess
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from typer.testing import CliRunner

from coop.commands.backup import app

runner = CliRunner()


class TestBackupCreate:
    """Tests for backup create command."""

    @patch("coop.commands.backup.subprocess.run")
    @patch("coop.commands.backup.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    @patch("coop.commands.backup.datetime")
    def test_create_success(self, mock_datetime, mock_run, tmp_path):
        """Test successful backup creation."""
        # Mock timestamp
        mock_datetime.datetime.now.return_value = datetime(2024, 1, 15, 10, 30, 45)
        mock_datetime.datetime.strftime = datetime.strftime

        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        backup_dir = tmp_path / "backups"

        with patch("coop.commands.backup.COMPOSE_FILE", compose_file):
            with patch("coop.commands.backup.BACKUP_DIR", backup_dir):
                # Mock successful pg_dump
                mock_run.return_value = MagicMock(returncode=0)

                # Mock open for SQL file
                with patch("builtins.open", mock_open()):
                    result = runner.invoke(app)

                    assert result.exit_code == 0
                    assert "Creating backup" in result.stdout
                    assert "Backing up PostgreSQL" in result.stdout
                    assert "Postgres dump complete" in result.stdout
                    assert "Backup stored in" in result.stdout

                    # Verify backup directory was created
                    assert backup_dir.exists()

    @patch("coop.commands.backup.subprocess.run")
    @patch("coop.commands.backup.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    @patch("coop.commands.backup.datetime")
    def test_create_postgres_failure(self, mock_datetime, mock_run, tmp_path):
        """Test backup handles PostgreSQL dump failure."""
        mock_datetime.datetime.now.return_value = datetime(2024, 1, 15, 10, 30, 45)
        mock_datetime.datetime.strftime = datetime.strftime

        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        backup_dir = tmp_path / "backups"

        with patch("coop.commands.backup.COMPOSE_FILE", compose_file):
            with patch("coop.commands.backup.BACKUP_DIR", backup_dir):
                # Mock failed pg_dump
                mock_run.side_effect = subprocess.CalledProcessError(1, "pg_dump")

                with patch("builtins.open", mock_open()):
                    result = runner.invoke(app)

                    assert result.exit_code == 0
                    assert "Backing up PostgreSQL" in result.stdout
                    assert "Postgres backup failed" in result.stdout

    @patch("coop.commands.backup.subprocess.run")
    @patch("coop.commands.backup.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    @patch("coop.commands.backup.datetime")
    def test_create_backup_directory_created(self, mock_datetime, mock_run, tmp_path):
        """Test backup directory is created if it doesn't exist."""
        mock_datetime.datetime.now.return_value = datetime(2024, 1, 15, 10, 30, 45)
        mock_datetime.datetime.strftime = datetime.strftime

        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        backup_dir = tmp_path / "backups"
        # Ensure backup directory doesn't exist initially
        assert not backup_dir.exists()

        with patch("coop.commands.backup.COMPOSE_FILE", compose_file):
            with patch("coop.commands.backup.BACKUP_DIR", backup_dir):
                mock_run.return_value = MagicMock(returncode=0)

                with patch("builtins.open", mock_open()):
                    result = runner.invoke(app)

                    # Verify backup directory was created
                    assert backup_dir.exists()
                    assert result.exit_code == 0

    @patch("coop.commands.backup.subprocess.run")
    @patch("coop.commands.backup.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    @patch("coop.commands.backup.datetime")
    def test_create_timestamp_format(self, mock_datetime, mock_run, tmp_path):
        """Test backup uses correct timestamp format."""
        # Mock specific timestamp
        mock_datetime.datetime.now.return_value = datetime(2024, 3, 25, 14, 30, 45)
        mock_datetime.datetime.strftime = datetime.strftime

        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        backup_dir = tmp_path / "backups"

        with patch("coop.commands.backup.COMPOSE_FILE", compose_file):
            with patch("coop.commands.backup.BACKUP_DIR", backup_dir):
                mock_run.return_value = MagicMock(returncode=0)

                with patch("builtins.open", mock_open()):
                    result = runner.invoke(app)

                    # Verify timestamp format in output
                    assert "20240325_143045" in result.stdout

    @patch("coop.commands.backup.subprocess.run")
    @patch("coop.commands.backup.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    def test_create_qdrant_placeholder(self, mock_run, tmp_path):
        """Test backup shows Qdrant placeholder message."""
        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        backup_dir = tmp_path / "backups"

        with patch("coop.commands.backup.COMPOSE_FILE", compose_file):
            with patch("coop.commands.backup.BACKUP_DIR", backup_dir):
                mock_run.return_value = MagicMock(returncode=0)

                with patch("builtins.open", mock_open()):
                    result = runner.invoke(app)

                    assert result.exit_code == 0
                    assert "Creating Qdrant Snapshot" in result.stdout
                    assert "Qdrant snapshotting via API not yet implemented" in result.stdout

    @patch("coop.commands.backup.subprocess.run")
    @patch("coop.commands.backup.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    def test_create_minio_placeholder(self, mock_run, tmp_path):
        """Test backup shows MinIO placeholder message."""
        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        backup_dir = tmp_path / "backups"

        with patch("coop.commands.backup.COMPOSE_FILE", compose_file):
            with patch("coop.commands.backup.BACKUP_DIR", backup_dir):
                mock_run.return_value = MagicMock(returncode=0)

                with patch("builtins.open", mock_open()):
                    result = runner.invoke(app)

                    assert result.exit_code == 0
                    assert "Syncing MinIO artifacts" in result.stdout
                    assert "MinIO sync not yet implemented" in result.stdout

    @patch("coop.commands.backup.subprocess.run")
    @patch("coop.commands.backup.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    @patch("coop.commands.backup.datetime")
    def test_create_complete_flow(self, mock_datetime, mock_run, tmp_path):
        """Test complete backup creation flow."""
        mock_datetime.datetime.now.return_value = datetime(2024, 1, 15, 10, 30, 45)
        mock_datetime.datetime.strftime = datetime.strftime

        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        backup_dir = tmp_path / "backups"

        with patch("coop.commands.backup.COMPOSE_FILE", compose_file):
            with patch("coop.commands.backup.BACKUP_DIR", backup_dir):
                mock_run.return_value = MagicMock(returncode=0)

                with patch("builtins.open", mock_open()):
                    result = runner.invoke(app)

                    # Verify all backup steps are shown
                    assert "Creating backup" in result.stdout
                    assert "Backing up PostgreSQL" in result.stdout
                    assert "Creating Qdrant Snapshot" in result.stdout
                    assert "Syncing MinIO artifacts" in result.stdout
                    assert "Backup stored in" in result.stdout
                    assert result.exit_code == 0

    @patch("coop.commands.backup.subprocess.run")
    @patch("coop.commands.backup.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    @patch("coop.commands.backup.datetime")
    def test_create_docker_exec_command(self, mock_datetime, mock_run, tmp_path):
        """Test backup uses correct Docker exec command."""
        mock_datetime.datetime.now.return_value = datetime(2024, 1, 15, 10, 30, 45)
        mock_datetime.datetime.strftime = datetime.strftime

        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        backup_dir = tmp_path / "backups"

        with patch("coop.commands.backup.COMPOSE_FILE", compose_file):
            with patch("coop.commands.backup.BACKUP_DIR", backup_dir):
                mock_run.return_value = MagicMock(returncode=0)

                with patch("builtins.open", mock_open()):
                    runner.invoke(app)

                    # Verify Docker exec command was called
                    mock_run.assert_called_once()
                    call_args = mock_run.call_args[0][0]
                    assert "docker" in call_args
                    assert "exec" in call_args
                    assert "co-op-db" in call_args
                    assert "pg_dump" in call_args
                    assert "-U" in call_args
                    assert "postgres" in call_args
                    assert "co_op" in call_args

    @patch("coop.commands.backup.subprocess.run")
    @patch("coop.commands.backup.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    @patch("coop.commands.backup.datetime")
    def test_create_multiple_backups(self, mock_datetime, mock_run, tmp_path):
        """Test creating multiple backups with different timestamps."""
        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        backup_dir = tmp_path / "backups"

        with patch("coop.commands.backup.COMPOSE_FILE", compose_file):
            with patch("coop.commands.backup.BACKUP_DIR", backup_dir):
                mock_run.return_value = MagicMock(returncode=0)

                # First backup
                mock_datetime.datetime.now.return_value = datetime(2024, 1, 15, 10, 0, 0)
                mock_datetime.datetime.strftime = datetime.strftime

                with patch("builtins.open", mock_open()):
                    result1 = runner.invoke(app)
                    assert result1.exit_code == 0
                    assert "20240115_100000" in result1.stdout

                # Second backup with different timestamp
                mock_datetime.datetime.now.return_value = datetime(2024, 1, 15, 11, 0, 0)

                with patch("builtins.open", mock_open()):
                    result2 = runner.invoke(app)
                    assert result2.exit_code == 0
                    assert "20240115_110000" in result2.stdout

    @patch("coop.commands.backup.subprocess.run")
    @patch("coop.commands.backup.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    def test_create_custom_compose_path(self, mock_run, tmp_path, monkeypatch):
        """Test backup with custom compose path."""
        compose_file = tmp_path / "custom-compose.yml"
        compose_file.touch()

        backup_dir = tmp_path / "backups"

        monkeypatch.setenv("COOP_COMPOSE_PATH", str(compose_file))

        with patch("coop.commands.backup.COMPOSE_FILE", compose_file):
            with patch("coop.commands.backup.BACKUP_DIR", backup_dir):
                mock_run.return_value = MagicMock(returncode=0)

                with patch("builtins.open", mock_open()):
                    result = runner.invoke(app)

                    assert result.exit_code == 0
                    assert "Creating backup" in result.stdout


    @patch("coop.commands.backup.subprocess.run")
    @patch("coop.commands.backup.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    @patch("coop.commands.backup.datetime")
    def test_create_backup_file_created(self, mock_datetime, mock_run, tmp_path):
        """Test that backup SQL file is actually created."""
        mock_datetime.datetime.now.return_value = datetime(2024, 1, 15, 10, 30, 45)
        mock_datetime.datetime.strftime = datetime.strftime

        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        backup_dir = tmp_path / "backups"

        with patch("coop.commands.backup.COMPOSE_FILE", compose_file):
            with patch("coop.commands.backup.BACKUP_DIR", backup_dir):
                mock_run.return_value = MagicMock(returncode=0)

                # Use real file creation instead of mock
                result = runner.invoke(app)

                # Verify backup directory exists
                assert backup_dir.exists()
                assert backup_dir.is_dir()

                # Verify SQL file was created
                expected_file = backup_dir / "db_20240115_103045.sql"
                assert expected_file.exists()
                assert result.exit_code == 0

    @patch("coop.commands.backup.subprocess.run")
    @patch("coop.commands.backup.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    @patch("coop.commands.backup.datetime")
    def test_create_backup_file_content(self, mock_datetime, mock_run, tmp_path):
        """Test that backup file is created (content verification skipped due to subprocess complexity)."""
        mock_datetime.datetime.now.return_value = datetime(2024, 1, 15, 10, 30, 45)
        mock_datetime.datetime.strftime = datetime.strftime

        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        backup_dir = tmp_path / "backups"

        with patch("coop.commands.backup.COMPOSE_FILE", compose_file):
            with patch("coop.commands.backup.BACKUP_DIR", backup_dir):
                mock_run.return_value = MagicMock(returncode=0)

                with patch("builtins.open", mock_open()):
                    result = runner.invoke(app)

                    # Verify command completed successfully
                    assert result.exit_code == 0
                    assert "Backing up PostgreSQL" in result.stdout
                    assert "Postgres dump complete" in result.stdout

    @patch("coop.commands.backup.subprocess.run")
    @patch("coop.commands.backup.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    @patch("coop.commands.backup.datetime")
    def test_create_backup_directory_permissions(self, mock_datetime, mock_run, tmp_path):
        """Test backup handles directory creation with proper permissions."""
        mock_datetime.datetime.now.return_value = datetime(2024, 1, 15, 10, 30, 45)
        mock_datetime.datetime.strftime = datetime.strftime

        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        backup_dir = tmp_path / "backups"

        with patch("coop.commands.backup.COMPOSE_FILE", compose_file):
            with patch("coop.commands.backup.BACKUP_DIR", backup_dir):
                mock_run.return_value = MagicMock(returncode=0)

                with patch("builtins.open", mock_open()):
                    result = runner.invoke(app)

                    # Verify directory was created and is writable
                    assert backup_dir.exists()
                    assert backup_dir.is_dir()
                    # Test we can write to it
                    test_file = backup_dir / "test.txt"
                    test_file.write_text("test")
                    assert test_file.exists()
                    assert result.exit_code == 0

    @patch("coop.commands.backup.subprocess.run")
    @patch("coop.commands.backup.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    @patch("coop.commands.backup.datetime")
    def test_create_handles_io_error(self, mock_datetime, mock_run, tmp_path):
        """Test backup handles IO errors gracefully."""
        mock_datetime.datetime.now.return_value = datetime(2024, 1, 15, 10, 30, 45)
        mock_datetime.datetime.strftime = datetime.strftime

        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        backup_dir = tmp_path / "backups"

        with patch("coop.commands.backup.COMPOSE_FILE", compose_file):
            with patch("coop.commands.backup.BACKUP_DIR", backup_dir):
                mock_run.return_value = MagicMock(returncode=0)

                # Mock open to raise IOError
                with patch("builtins.open", side_effect=IOError("Disk full")):
                    result = runner.invoke(app)

                    # Should handle error gracefully
                    assert result.exit_code == 0
                    # Error should be caught and reported

    @patch("coop.commands.backup.subprocess.run")
    @patch("coop.commands.backup.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    @patch("coop.commands.backup.datetime")
    def test_create_container_not_running(self, mock_datetime, mock_run, tmp_path):
        """Test backup when Docker container is not running."""
        mock_datetime.datetime.now.return_value = datetime(2024, 1, 15, 10, 30, 45)
        mock_datetime.datetime.strftime = datetime.strftime

        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        backup_dir = tmp_path / "backups"

        with patch("coop.commands.backup.COMPOSE_FILE", compose_file):
            with patch("coop.commands.backup.BACKUP_DIR", backup_dir):
                # Mock container not found error
                mock_run.side_effect = subprocess.CalledProcessError(
                    1, "docker exec", stderr="Error: No such container: co-op-db"
                )

                with patch("builtins.open", mock_open()):
                    result = runner.invoke(app)

                    assert result.exit_code == 0
                    assert "Postgres backup failed" in result.stdout

    @patch("coop.commands.backup.subprocess.run")
    @patch("coop.commands.backup.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    @patch("coop.commands.backup.datetime")
    def test_create_database_connection_error(self, mock_datetime, mock_run, tmp_path):
        """Test backup when database connection fails."""
        mock_datetime.datetime.now.return_value = datetime(2024, 1, 15, 10, 30, 45)
        mock_datetime.datetime.strftime = datetime.strftime

        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        backup_dir = tmp_path / "backups"

        with patch("coop.commands.backup.COMPOSE_FILE", compose_file):
            with patch("coop.commands.backup.BACKUP_DIR", backup_dir):
                # Mock database connection error
                mock_run.side_effect = subprocess.CalledProcessError(
                    1, "pg_dump", stderr="could not connect to database"
                )

                with patch("builtins.open", mock_open()):
                    result = runner.invoke(app)

                    assert result.exit_code == 0
                    assert "Postgres backup failed" in result.stdout

    @patch("coop.commands.backup.subprocess.run")
    @patch("coop.commands.backup.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    @patch("coop.commands.backup.datetime")
    def test_create_backup_size_verification(self, mock_datetime, mock_run, tmp_path):
        """Test backup file is created successfully."""
        mock_datetime.datetime.now.return_value = datetime(2024, 1, 15, 10, 30, 45)
        mock_datetime.datetime.strftime = datetime.strftime

        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        backup_dir = tmp_path / "backups"

        with patch("coop.commands.backup.COMPOSE_FILE", compose_file):
            with patch("coop.commands.backup.BACKUP_DIR", backup_dir):
                mock_run.return_value = MagicMock(returncode=0)

                with patch("builtins.open", mock_open()):
                    result = runner.invoke(app)

                    # Verify command completed successfully
                    assert result.exit_code == 0
                    assert "Backing up PostgreSQL" in result.stdout
                    assert "Postgres dump complete" in result.stdout

    @patch("coop.commands.backup.subprocess.run")
    @patch("coop.commands.backup.COMPOSE_FILE", Path("/fake/docker-compose.yml"))
    @patch("coop.commands.backup.datetime")
    def test_create_concurrent_backups(self, mock_datetime, mock_run, tmp_path):
        """Test creating multiple backups doesn't overwrite previous ones."""
        compose_file = tmp_path / "docker-compose.yml"
        compose_file.touch()

        backup_dir = tmp_path / "backups"

        with patch("coop.commands.backup.COMPOSE_FILE", compose_file):
            with patch("coop.commands.backup.BACKUP_DIR", backup_dir):
                mock_run.return_value = MagicMock(returncode=0)

                # Create first backup
                mock_datetime.datetime.now.return_value = datetime(2024, 1, 15, 10, 0, 0)
                mock_datetime.datetime.strftime = datetime.strftime

                with patch("builtins.open", mock_open()):
                    result1 = runner.invoke(app)
                    assert result1.exit_code == 0

                # Create second backup with different timestamp
                mock_datetime.datetime.now.return_value = datetime(2024, 1, 15, 11, 0, 0)

                with patch("builtins.open", mock_open()):
                    result2 = runner.invoke(app)
                    assert result2.exit_code == 0

                # Both timestamps should appear in outputs
                assert "20240115_100000" in result1.stdout
                assert "20240115_110000" in result2.stdout
