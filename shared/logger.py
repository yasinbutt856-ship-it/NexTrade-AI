import structlog
from structlog.dev import ConsoleRenderer
from structlog.processors import JSONRenderer
import logging
import logging.handlers
from pathlib import Path


def setup_logging(
    level: str = "INFO",
    log_format: str = "json",
    log_file: str = "logs/trading.log",
    max_bytes: int = 10485760,
    backup_count: int = 5,
    error_file: str = "logs/error.log",
) -> None:
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    Path(error_file).parent.mkdir(parents=True, exist_ok=True)

    renderer: structlog.types.Processor
    if log_format == "json":
        renderer = JSONRenderer()
    else:
        renderer = ConsoleRenderer()

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            renderer,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(level.upper())

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level.upper())
    root_logger.addHandler(stream_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count
    )
    file_handler.setLevel(level.upper())
    root_logger.addHandler(file_handler)

    error_handler = logging.handlers.RotatingFileHandler(
        error_file, maxBytes=max_bytes, backupCount=backup_count
    )
    error_handler.setLevel(logging.WARNING)
    root_logger.addHandler(error_handler)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name or __name__)
