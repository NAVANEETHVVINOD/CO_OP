import pytest
from unittest.mock import patch, MagicMock

from app.crons.system_monitor import run_system_monitor

@pytest.mark.asyncio
async def test_run_system_monitor_all_healthy(db_session):
    with patch("app.crons.system_monitor.httpx.AsyncClient") as mock_client, \
         patch("app.crons.system_monitor.redis.asyncio.from_url") as mock_redis, \
         patch("app.crons.system_monitor.QdrantClient") as mock_qdrant, \
         patch("app.crons.system_monitor.send_alert") as mock_send_alert:
        
        # Setup mocks to return success
        client_instance = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = client_instance
        
        redis_instance = AsyncMock()
        redis_instance.ping.return_value = True
        mock_redis.return_value = redis_instance
        
        # Run system monitor
        await run_system_monitor(db_session)
        
        # Ensure send_alert was NOT called since everything is healthy
        mock_send_alert.assert_not_called()

# We need an AsyncMock wrapper
class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)
