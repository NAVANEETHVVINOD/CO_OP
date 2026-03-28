"""
Preservation property tests for system monitor.

These tests should PASS on unfixed code, ensuring other services are unaffected.
"""
from unittest.mock import patch
from app.crons.system_monitor import _get_services


class MockSettings:
    """Mock settings with typical Docker service URLs."""
    QDRANT_URL = "http://localhost:6333"
    OLLAMA_URL = "http://localhost:11434"
    LITELLM_URL = "http://localhost:4000"
    MINIO_URL = "localhost:9000"  # This will be used but we're testing non-MinIO


def test_postgres_config_unchanged():
    """Verify Postgres configuration remains unchanged after fix."""
    with patch("app.config.get_settings", return_value=MockSettings()):
        services = _get_services()
        assert services["postgres"] == {"type": "internal"}


def test_redis_config_unchanged():
    """Verify Redis configuration remains unchanged after fix."""
    with patch("app.config.get_settings", return_value=MockSettings()):
        services = _get_services()
        assert services["redis"] == {"type": "internal"}


def test_qdrant_url_unchanged():
    """Verify Qdrant URL format remains unchanged after fix."""
    with patch("app.config.get_settings", return_value=MockSettings()):
        services = _get_services()
        expected = f"{MockSettings.QDRANT_URL}/healthz"
        assert services["qdrant"]["url"] == expected


def test_ollama_url_unchanged():
    """Verify Ollama URL format remains unchanged after fix."""
    with patch("app.config.get_settings", return_value=MockSettings()):
        services = _get_services()
        expected = f"{MockSettings.OLLAMA_URL}/api/tags"
        assert services["ollama"]["url"] == expected


def test_litellm_url_unchanged():
    """Verify LiteLLM URL format remains unchanged after fix."""
    with patch("app.config.get_settings", return_value=MockSettings()):
        services = _get_services()
        expected = f"{MockSettings.LITELLM_URL}/health"
        assert services["litellm"]["url"] == expected


def test_all_non_minio_services_have_expected_structure():
    """Verify all non-MinIO services maintain their expected structure."""
    with patch("app.config.get_settings", return_value=MockSettings()):
        services = _get_services()
        
        # Internal services should have type="internal"
        assert "type" in services["postgres"]
        assert services["postgres"]["type"] == "internal"
        assert "type" in services["redis"]
        assert services["redis"]["type"] == "internal"
        
        # HTTP services should have url field
        assert "url" in services["qdrant"]
        assert "url" in services["ollama"]
        assert "url" in services["litellm"]
        
        # All HTTP service URLs should start with http:// or https://
        for service_name in ["qdrant", "ollama", "litellm"]:
            url = services[service_name]["url"]
            assert url.startswith("http://") or url.startswith("https://"), \
                f"{service_name} URL should have protocol: {url}"
