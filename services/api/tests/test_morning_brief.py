import pytest
from unittest.mock import patch, MagicMock

from app.crons.morning_brief import run_morning_brief
from app.db.models import Lead

@pytest.mark.asyncio
@pytest.mark.xfail(reason="Not supported in sqlite/host env")
async def test_run_morning_brief(db_session):
    # Create a mock session factory that returns our db_session
    mock_session_factory = MagicMock()
    mock_session_factory.return_value.__aenter__.return_value = db_session

    with patch("app.communication.telegram.send_message") as mock_send_message, \
         patch("httpx.AsyncClient") as mock_client, \
         patch("app.db.session.AsyncSessionLocal", mock_session_factory):
        
        # Add a lead to the DB to test DB queries
        import uuid
        tenant_uuid = uuid.uuid4()
        lead = Lead(tenant_id=tenant_uuid, source="test", title="Test Lead", url="http", description="", score=10)
        db_session.add(lead)
        # Mock token usage query
        from app.db.models import CostEvent
        cost = CostEvent(tenant_id=tenant_uuid, model_name="test", cost=1.50, prompt_tokens=50, completion_tokens=50)
        db_session.add(cost)
        await db_session.commit()
        
        # Mock healthy system components
        client_instance = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = client_instance
        
        await run_morning_brief()
        
        # Alert should be sent with the brief
        mock_send_message.assert_called_once()
        args, kwargs = mock_send_message.call_args
        message = args[0]
        assert "Morning Brief" in message
        assert "1 found in last 24h" in message
        assert "100 tokens" in message # Check that mock token usage was grabbed

class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)
