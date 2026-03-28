"""
Bug condition exploration tests for MinIO health check URL.

These tests are expected to FAIL on unfixed code, confirming the bug exists.
"""
import pytest
import httpx
from unittest.mock import patch
from app.crons.system_monitor import _get_services


class MockSettings:
    """Mock settings with typical Docker service URLs."""
    MINIO_URL = "minio:9000"
    QDRANT_URL = "http://qdrant:6333"
    OLLAMA_URL = "http://ollama:11434"
    LITELLM_URL = "http://litellm:4000"


def test_minio_health_url_must_have_protocol():
    """
    Test that MinIO health URL is constructed with http:// prefix.
    
    This test is expected to FAIL on unfixed code (bug exists).
    When the bug is present, the URL will be "minio:9000/minio/health/live"
    instead of "http://minio:9000/minio/health/live".
    """
    with patch("app.config.get_settings", return_value=MockSettings()):
        services = _get_services()
        minio_url = services["minio"]["url"]
        
        assert minio_url.startswith("http://") or minio_url.startswith("https://"), \
            f"MinIO health URL should have HTTP protocol, got {minio_url}"


def test_minio_http_request_fails_without_protocol():
    """
    Test that httpx raises protocol error when using malformed URL.
    
    This test verifies that the malformed URL (without protocol) causes
    httpx to raise an InvalidURL exception.
    """
    with patch("app.config.get_settings", return_value=MockSettings()):
        services = _get_services()
        minio_url = services["minio"]["url"]
        
        # Only run this if the URL is missing protocol (which is the buggy case)
        if not (minio_url.startswith("http://") or minio_url.startswith("https://")):
            with pytest.raises(httpx.InvalidURL):
                # httpx will raise InvalidURL if the URL scheme is missing
                httpx.get(minio_url)
