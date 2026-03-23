import pytest
from unittest.mock import AsyncMock, patch
from app.communication.telegram import cmd_start, cmd_status, cmd_budget

@pytest.mark.asyncio
async def test_cmd_start():
    update = AsyncMock()
    context = AsyncMock()
    
    await cmd_start(update, context)
    update.message.reply_text.assert_called_once()
    assert "Welcome" in update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_cmd_status():
    update = AsyncMock()
    context = AsyncMock()
    
    with patch("app.communication.telegram._get_db") as mock_get_db:
        # Mock simple session
        mock_session = AsyncMock()
        mock_get_db.return_value.__aenter__.return_value = mock_session
        
        await cmd_status(update, context)
        update.message.reply_text.assert_called_once()
        assert "System Status" in update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_cmd_budget():
    update = AsyncMock()
    context = AsyncMock()
    
    with patch("app.communication.telegram._get_db") as mock_get_db, \
         patch("app.communication.telegram.settings_router.get_credit_usage") as mock_credits:
         
        mock_get_db.return_value.__aenter__.return_value = AsyncMock()
        mock_credits.return_value = {"today_usd": 0.15, "total_usd": 1.20, "daily_budget_usd": 0.50}
        
        await cmd_budget(update, context)
        update.message.reply_text.assert_called_once()
        msg = update.message.reply_text.call_args[0][0]
        assert "Budget Status" in msg
        assert "0.15" in msg
        assert "0.50" in msg
