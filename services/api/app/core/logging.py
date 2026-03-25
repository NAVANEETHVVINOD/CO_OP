import logging
import sys
import structlog
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging():
    log_dir = Path.home() / ".co-op" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "coop.log"

    # Standard logging handlers
    stdout_handler = logging.StreamHandler(sys.stdout)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB per file, 5 backups
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[stdout_handler, file_handler]
    )
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.contextvars.merge_contextvars,
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                }
            ),
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

logger = structlog.get_logger()
