import pytest
from unittest.mock import AsyncMock, patch
from app.communication.telegram import cmd_start, cmd_status, cmd_budget, cmd_pause, cmd_resume, cmd_panic, cmd_approve, cmd_help

@pytest.fixture
def mock_update_context():
    update = AsyncMock()
    context = AsyncMock()
    return update, context

@pytest.mark.asyncio
async def test_cmd_start(mock_update_context):
    update, context = mock_update_context
    await cmd_start(update, context)
    update.message.reply_text.assert_called_once()
    assert "Co-Op OS Bot" in update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_cmd_help(mock_update_context):
    update, context = mock_update_context
    await cmd_help(update, context)
    update.message.reply_text.assert_called_once()
    assert "Co-Op Bot Commands" in update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_cmd_status(mock_update_context):
    update, context = mock_update_context
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = lambda: {"postgres": "ok", "redis": "ok"}
        mock_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_instance
        
        await cmd_status(update, context)
        update.message.reply_text.assert_called_once()
        assert "System Status" in update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_cmd_budget(mock_update_context):
    update, context = mock_update_context
    with patch("httpx.AsyncClient") as mock_client:
         
        mock_instance = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = lambda: {"today": {"total_cost": 0.15, "total_tokens": 1200, "usage_pct": 30.0}, "daily_limit": 100000}
        mock_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_instance
        
        await cmd_budget(update, context)
        update.message.reply_text.assert_called_once()
        msg = update.message.reply_text.call_args[0][0]
        assert "Token Budget" in msg
        assert "0.15" in msg

@pytest.mark.asyncio
async def test_cmd_pause(mock_update_context):
    update, context = mock_update_context
    await cmd_pause(update, context)
    update.message.reply_text.assert_called_once()
    assert "paused" in update.message.reply_text.call_args[0][0].lower()

@pytest.mark.asyncio
async def test_cmd_resume(mock_update_context):
    update, context = mock_update_context
    await cmd_resume(update, context)
    update.message.reply_text.assert_called_once()
    assert "resumed" in update.message.reply_text.call_args[0][0].lower()

@pytest.mark.asyncio
async def test_cmd_panic(mock_update_context):
    update, context = mock_update_context
    await cmd_panic(update, context)
    update.message.reply_text.assert_called_once()
    assert "panic" in update.message.reply_text.call_args[0][0].lower()

@pytest.mark.asyncio
async def test_cmd_approve(mock_update_context):
    update, context = mock_update_context
    context.bot = AsyncMock()
    context.bot.get_me.return_value = AsyncMock(username="TestBot")
    # Without args
    context.args = []
    await cmd_approve(update, context)
    update.message.reply_text.assert_called()
    text = update.message.reply_text.call_args[0][0].lower()
    assert ("no pending approvals" in text) or ("pending approval" in text)
    
    # With args
    update.message.reply_text.reset_mock()
    context.args = ["uuid-123"]
    await cmd_approve(update, context)
    update.message.reply_text.assert_called()
