import pytest
from unittest.mock import patch

from app.crons.morning_brief import run_morning_brief
from app.db.models import Lead

@pytest.mark.asyncio
async def test_run_morning_brief(db_session):
    with patch("app.crons.morning_brief.send_alert") as mock_send_alert, \
         patch("app.crons.morning_brief.httpx.AsyncClient") as mock_client:
        
        # Add a lead to the DB
        lead = Lead(tenant_id="default", source="test", title="Test Lead", url="http", description="", score=10)
        db_session.add(lead)
        await db_session.commit()
        
        # Mock healthy system
        client_instance = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = client_instance
        
        await run_morning_brief(db_session)
        
        # Alert should be sent with the brief
        mock_send_alert.assert_called_once()
        args, kwargs = mock_send_alert.call_args
        assert "Morning Brief" in args[0]
        assert "1 leads found" in args[0]

from unittest.mock import MagicMock
class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)
