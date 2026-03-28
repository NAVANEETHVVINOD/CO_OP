"""Enhanced tests for system monitor cron job."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.crons.system_monitor import (
    run_system_monitor,
    _check_service_http,
    _check_postgres,
    _check_redis,
    _get_services
)


@pytest.mark.asyncio
async def test_check_service_http_success():
    """Test HTTP service check with successful response"""
    with patch("app.crons.system_monitor.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await _check_service_http("test-service", "http://test:8000/health")
        
        assert result is True
        mock_client.get.assert_called_once_with("http://test:8000/health", timeout=5.0)


@pytest.mark.asyncio
async def test_check_service_http_failure():
    """Test HTTP service check with failed response"""
    with patch("app.crons.system_monitor.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await _check_service_http("test-service", "http://test:8000/health")
        
        assert result is False


@pytest.mark.asyncio
async def test_check_service_http_timeout():
    """Test HTTP service check with timeout"""
    with patch("app.crons.system_monitor.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("Timeout")
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await _check_service_http("test-service", "http://test:8000/health")
        
        assert result is False


@pytest.mark.asyncio
async def test_check_service_http_connection_error():
    """Test HTTP service check with connection error"""
    with patch("app.crons.system_monitor.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get.side_effect = ConnectionError("Connection refused")
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await _check_service_http("test-service", "http://test:8000/health")
        
        assert result is False


@pytest.mark.asyncio
async def test_check_postgres_success():
    """Test PostgreSQL check with successful connection"""
    with patch("app.crons.system_monitor.engine") as mock_engine:
        mock_conn = AsyncMock()
        mock_engine.connect.return_value.__aenter__.return_value = mock_conn
        
        result = await _check_postgres()
        
        assert result is True
        mock_conn.execute.assert_called_once()


@pytest.mark.asyncio
async def test_check_postgres_failure():
    """Test PostgreSQL check with connection failure"""
    with patch("app.crons.system_monitor.engine") as mock_engine:
        mock_engine.connect.side_effect = Exception("Connection failed")
        
        result = await _check_postgres()
        
        assert result is False


@pytest.mark.asyncio
async def test_check_redis_success():
    """Test Redis check with successful ping"""
    with patch("app.crons.system_monitor.redis_client") as mock_redis:
        mock_redis.ping.return_value = True
        
        result = await _check_redis()
        
        assert result is True
        mock_redis.ping.assert_called_once()


@pytest.mark.asyncio
async def test_check_redis_failure():
    """Test Redis check with failed ping"""
    with patch("app.crons.system_monitor.redis_client") as mock_redis:
        mock_redis.ping.side_effect = Exception("Connection refused")
        
        result = await _check_redis()
        
        assert result is False


@pytest.mark.asyncio
async def test_get_services_with_all_services():
    """Test _get_services returns all configured services"""
    with patch("app.crons.system_monitor.get_settings") as mock_settings:
        mock_config = MagicMock()
        mock_config.QDRANT_URL = "http://qdrant:6333"
        mock_config.MINIO_URL = "minio:9000"
        mock_config.OLLAMA_URL = "http://ollama:11434"
        mock_config.LITELLM_URL = "http://litellm:4000"
        mock_settings.return_value = mock_config
        
        services = _get_services()
        
        assert "postgres" in services
        assert "redis" in services
        assert "qdrant" in services
        assert "minio" in services
        assert "ollama" in services
        assert "litellm" in services


@pytest.mark.asyncio
async def test_get_services_skips_disabled():
    """Test _get_services skips disabled services"""
    with patch("app.crons.system_monitor.get_settings") as mock_settings:
        mock_config = MagicMock()
        mock_config.QDRANT_URL = None
        mock_config.MINIO_URL = "minio:9000"
        mock_config.OLLAMA_URL = "http://ollama:11434"
        mock_config.LITELLM_URL = None
        mock_settings.return_value = mock_config
        
        services = _get_services()
        
        assert services["qdrant"]["type"] == "skip"
        assert services["litellm"]["type"] == "skip"


@pytest.mark.asyncio
async def test_run_system_monitor_all_healthy():
    """Test system monitor with all services healthy"""
    with patch("app.crons.system_monitor._check_postgres", return_value=True):
        with patch("app.crons.system_monitor._check_redis", return_value=True):
            with patch("app.crons.system_monitor._check_service_http", return_value=True):
                with patch("app.crons.system_monitor._get_services") as mock_get_services:
                    mock_get_services.return_value = {
                        "postgres": {"type": "internal"},
                        "redis": {"type": "internal"},
                        "qdrant": {"url": "http://qdrant:6333/healthz"},
                        "minio": {"url": "http://minio:9000/minio/health/live"},
                        "ollama": {"url": "http://ollama:11434/api/tags"},
                        "litellm": {"type": "skip"}
                    }
                    
                    # Should not raise exception
                    await run_system_monitor()


@pytest.mark.asyncio
async def test_run_system_monitor_with_failures():
    """Test system monitor with some services unhealthy"""
    with patch("app.crons.system_monitor._check_postgres", return_value=True):
        with patch("app.crons.system_monitor._check_redis", return_value=False):
            with patch("app.crons.system_monitor._check_service_http", return_value=False):
                with patch("app.crons.system_monitor._get_services") as mock_get_services:
                    with patch("app.crons.system_monitor.send_alert") as mock_alert:
                        mock_get_services.return_value = {
                            "postgres": {"type": "internal"},
                            "redis": {"type": "internal"},
                            "qdrant": {"url": "http://qdrant:6333/healthz"}
                        }
                        
                        await run_system_monitor()
                        
                        # Should send alert for unhealthy services
                        mock_alert.assert_called_once()
                        alert_msg = mock_alert.call_args[0][0]
                        assert "Unhealthy services" in alert_msg


@pytest.mark.asyncio
async def test_run_system_monitor_alert_failure():
    """Test system monitor handles alert sending failures"""
    with patch("app.crons.system_monitor._check_postgres", return_value=False):
        with patch("app.crons.system_monitor._check_redis", return_value=True):
            with patch("app.crons.system_monitor._get_services") as mock_get_services:
                with patch("app.crons.system_monitor.send_alert") as mock_alert:
                    mock_get_services.return_value = {
                        "postgres": {"type": "internal"},
                        "redis": {"type": "internal"}
                    }
                    mock_alert.side_effect = Exception("Telegram API error")
                    
                    # Should not raise exception even if alert fails
                    await run_system_monitor()


@pytest.mark.asyncio
async def test_run_system_monitor_multiple_failures():
    """Test system monitor with multiple service failures"""
    with patch("app.crons.system_monitor._check_postgres", return_value=False):
        with patch("app.crons.system_monitor._check_redis", return_value=False):
            with patch("app.crons.system_monitor._check_service_http", return_value=False):
                with patch("app.crons.system_monitor._get_services") as mock_get_services:
                    with patch("app.crons.system_monitor.send_alert") as mock_alert:
                        mock_get_services.return_value = {
                            "postgres": {"type": "internal"},
                            "redis": {"type": "internal"},
                            "qdrant": {"url": "http://qdrant:6333/healthz"},
                            "minio": {"url": "http://minio:9000/minio/health/live"}
                        }
                        
                        await run_system_monitor()
                        
                        # Should send alert listing all unhealthy services
                        mock_alert.assert_called_once()
                        alert_msg = mock_alert.call_args[0][0]
                        assert "postgres" in alert_msg or "redis" in alert_msg


@pytest.mark.asyncio
async def test_run_system_monitor_skips_disabled_services():
    """Test system monitor skips services marked as skip"""
    with patch("app.crons.system_monitor._check_postgres", return_value=True):
        with patch("app.crons.system_monitor._check_redis", return_value=True):
            with patch("app.crons.system_monitor._check_service_http") as mock_http_check:
                with patch("app.crons.system_monitor._get_services") as mock_get_services:
                    mock_get_services.return_value = {
                        "postgres": {"type": "internal"},
                        "redis": {"type": "internal"},
                        "qdrant": {"type": "skip"},
                        "litellm": {"type": "skip"}
                    }
                    
                    await run_system_monitor()
                    
                    # Should not check HTTP services marked as skip
                    mock_http_check.assert_not_called()
