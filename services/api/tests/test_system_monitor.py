import pytest
from unittest.mock import patch, MagicMock

from app.crons.system_monitor import run_system_monitor

@pytest.mark.asyncio
async def test_run_system_monitor_all_healthy(db_session):
    with patch("httpx.AsyncClient") as mock_client, \
         patch("app.core.redis_client.redis_client.ping") as mock_redis_ping, \
         patch("app.crons.system_monitor._check_postgres") as mock_postgres, \
         patch("app.communication.telegram.send_alert") as mock_send_alert:
        
        # Setup mocks to return success
        mock_postgres.return_value = True
        client_instance = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = client_instance
        
        mock_redis_ping.return_value = True
        
        # Run system monitor
        await run_system_monitor()
        
        # Ensure send_alert was NOT called since everything is healthy
        mock_send_alert.assert_not_called()

@pytest.mark.asyncio
async def test_run_system_monitor_failure(db_session):
    with patch("httpx.AsyncClient") as mock_client, \
         patch("app.core.redis_client.redis_client.ping") as mock_redis_ping, \
         patch("app.crons.system_monitor._check_postgres") as mock_postgres, \
         patch("app.communication.telegram.send_alert") as mock_send_alert:
        
        # Force a failure in Redis
        mock_postgres.return_value = True
        mock_redis_ping.side_effect = Exception("Connection refused")
        
        # Mock others as successful just in case
        client_instance = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = client_instance
        
        # Run system monitor
        await run_system_monitor()
        
        # Assert send_alert was called because of the Redis failure
        mock_send_alert.assert_called_once()
        args, _ = mock_send_alert.call_args
        assert "Unhealthy services" in args[0]
        assert "redis" in args[0].lower()

class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)
