"""
Structured Logging Configuration

Provides JSON-formatted logging for production with rotation support.
"""

import logging
import logging.handlers
import json
import sys
from datetime import datetime
from typing import Any, Dict
from app.config import get_settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        # Filter sensitive information
        message = log_data["message"]
        if any(keyword in message.lower() for keyword in ["password", "secret", "token", "api_key"]):
            log_data["message"] = "[REDACTED - Contains sensitive information]"
        
        return json.dumps(log_data)


class SimpleFormatter(logging.Formatter):
    """Simple formatter for development"""
    
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        level = record.levelname
        logger_name = record.name
        message = record.getMessage()
        
        # Filter sensitive information
        if any(keyword in message.lower() for keyword in ["password", "secret", "token", "api_key"]):
            message = "[REDACTED - Contains sensitive information]"
        
        return f"{timestamp} [{level}] {logger_name}: {message}"


def setup_logging():
    """Configure logging for the application"""
    settings = get_settings()
    
    # Get log level from settings
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Use JSON formatter for production, simple formatter for development
    if settings.ENVIRONMENT == "production":
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(SimpleFormatter())
    
    root_logger.addHandler(console_handler)
    
    # Rotating file handler (10MB max, keep 5 files)
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            filename="logs/app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)
    except Exception as e:
        # If logs directory doesn't exist or can't write, log to console only
        root_logger.warning(f"Could not create file handler: {e}")
    
    # Suppress noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    root_logger.info(f"Logging configured: level={settings.LOG_LEVEL}, environment={settings.ENVIRONMENT}")
