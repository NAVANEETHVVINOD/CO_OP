"""
Telegram Bot — In-process bot for system control and notifications.
Uses python-telegram-bot with long polling (no webhook needed).
Started as an asyncio background task in the FastAPI lifespan.
"""
import logging
import asyncio
from typing import Optional

from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app.config import get_settings

logger = logging.getLogger(__name__)

# Module-level bot instance (set during start_telegram_bot)
_bot_app: Optional[Application] = None
_admin_chat_id: Optional[str] = None


# ─── Utilities ──────────────────────────────────────────────────────

async def send_alert(message: str) -> None:
    """Send an alert message to the admin Telegram chat."""
    if not _bot_app or not _admin_chat_id:
        logger.warning(f"Telegram alert skipped (not configured): {message}")
        return
    try:
        await _bot_app.bot.send_message(
            chat_id=_admin_chat_id,
            text=f"🚨 *ALERT*\n{message}",
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")


async def send_progress(chat_id: str, step: int, total: int, message: str) -> None:
    """Send a numbered progress update (e.g., [1/6] Searching Upwork...)."""
    if not _bot_app:
        logger.warning(f"Telegram progress skipped (not configured): [{step}/{total}] {message}")
        return
    try:
        await _bot_app.bot.send_message(
            chat_id=chat_id,
            text=f"⏳ [{step}/{total}] {message}",
        )
    except Exception as e:
        logger.error(f"Failed to send Telegram progress: {e}")


async def send_message(message: str, chat_id: Optional[str] = None) -> None:
    """Send a message to a specific chat or the admin chat."""
    target = chat_id or _admin_chat_id
    if not _bot_app or not target:
        logger.warning(f"Telegram message skipped (not configured): {message}")
        return
    try:
        await _bot_app.bot.send_message(chat_id=target, text=message)
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")


# ─── Command Handlers ──────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        "🤖 *Co-Op OS Bot*\n\n"
        "I'm your AI company operating system.\n"
        "Send /help to see available commands.\n\n"
        f"Your chat ID: `{chat_id}`\n"
        "_Set this as TELEGRAM_ADMIN_CHAT_ID in .env for alerts._",
        parse_mode="Markdown",
    )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status — show system health."""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:8000/health", timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                lines = ["📊 *System Status*\n"]
                for svc, status in data.items():
                    if svc == "status":
                        continue
                    icon = "✅" if status == "ok" else "❌"
                    lines.append(f"  {icon} {svc}: {status}")
                await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
            else:
                await update.message.reply_text("⚠️ Health check returned non-200")
    except Exception as e:
        await update.message.reply_text(f"❌ Health check failed: {e}")


async def cmd_pause(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /pause — pause all background agents."""
    # TODO: Implement actual pause logic in Stage 3
    await update.message.reply_text(
        "⏸️ *Agents Paused*\n"
        "All background tasks will skip their next run.\n"
        "Use /resume to continue.",
        parse_mode="Markdown",
    )


async def cmd_resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /resume — resume background agents."""
    await update.message.reply_text(
        "▶️ *Agents Resumed*\n"
        "Background tasks are running again.",
        parse_mode="Markdown",
    )


async def cmd_panic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /panic — emergency stop all agents."""
    await update.message.reply_text(
        "🛑 *PANIC MODE*\n"
        "All agents stopped immediately.\n"
        "All pending tasks cancelled.\n"
        "Use /resume to restart.",
        parse_mode="Markdown",
    )


async def cmd_approve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /approve — approve pending HITL actions."""
    await update.message.reply_text(
        "✅ No pending approvals.\n"
        "_HITL approval system will be active in Stage 3._",
        parse_mode="Markdown",
    )


async def cmd_budget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /budget — show token budget status."""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:8000/v1/costs", timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                today = data.get("today", {})
                await update.message.reply_text(
                    "💰 *Token Budget*\n\n"
                    f"Today's tokens: {today.get('total_tokens', 0):,}\n"
                    f"Today's cost: ${today.get('total_cost', 0):.4f}\n"
                    f"Daily limit: {data.get('daily_limit', 100000):,} tokens\n"
                    f"Usage: {today.get('usage_pct', 0):.1f}%",
                    parse_mode="Markdown",
                )
            else:
                await update.message.reply_text("⚠️ Could not fetch budget info.")
    except Exception as e:
        await update.message.reply_text(f"❌ Budget check failed: {e}")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help — list available commands."""
    await update.message.reply_text(
        "🤖 *Co-Op Bot Commands*\n\n"
        "/start — Welcome message\n"
        "/status — System health check\n"
        "/pause — Pause all agents\n"
        "/resume — Resume agents\n"
        "/panic — Emergency stop\n"
        "/approve — Review pending approvals\n"
        "/budget — Token usage & limits\n"
        "/help — This message",
        parse_mode="Markdown",
    )


# ─── Bot Lifecycle ──────────────────────────────────────────────────

async def start_telegram_bot() -> None:
    """
    Start the Telegram bot with long polling.
    Called as a background task from the FastAPI lifespan.
    """
    global _bot_app, _admin_chat_id

    settings = get_settings()
    token = settings.TELEGRAM_BOT_TOKEN

    if not token:
        logger.info("TELEGRAM_BOT_TOKEN not set — Telegram bot disabled.")
        return

    _admin_chat_id = settings.TELEGRAM_ADMIN_CHAT_ID
    if not _admin_chat_id:
        logger.warning("TELEGRAM_ADMIN_CHAT_ID not set — alerts will be skipped.")

    logger.info("Starting Telegram bot...")

    _bot_app = Application.builder().token(token).build()

    # Register handlers
    _bot_app.add_handler(CommandHandler("start", cmd_start))
    _bot_app.add_handler(CommandHandler("status", cmd_status))
    _bot_app.add_handler(CommandHandler("pause", cmd_pause))
    _bot_app.add_handler(CommandHandler("resume", cmd_resume))
    _bot_app.add_handler(CommandHandler("panic", cmd_panic))
    _bot_app.add_handler(CommandHandler("approve", cmd_approve))
    _bot_app.add_handler(CommandHandler("budget", cmd_budget))
    _bot_app.add_handler(CommandHandler("help", cmd_help))

    # Initialize and start polling
    await _bot_app.initialize()
    await _bot_app.start()
    await _bot_app.updater.start_polling(drop_pending_updates=True)

    logger.info("Telegram bot started successfully.")


async def stop_telegram_bot() -> None:
    """Stop the Telegram bot gracefully."""
    global _bot_app
    if _bot_app:
        logger.info("Stopping Telegram bot...")
        await _bot_app.updater.stop()
        await _bot_app.stop()
        await _bot_app.shutdown()
        _bot_app = None
        logger.info("Telegram bot stopped.")
