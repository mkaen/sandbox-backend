import logging
import sys

from pythonjsonlogger.json import JsonFormatter

from src.config import settings

logger = logging.getLogger(settings.LOGGER_NAME)


class AppContextFilter(logging.Filter):
    """Add default field values for structured logging."""

    _DEFAULTS = {
        "environment": lambda: settings.ENVIRONMENT,
        "request_id": lambda: None,
        "correlation_id": lambda: None,
        "method": lambda: None,
        "path": lambda: None,
        "status_code": lambda: None,
        "duration_ms": lambda: None,
    }

    def filter(self, record: logging.LogRecord) -> bool:
        for field, default in self._DEFAULTS.items():
            if not hasattr(record, field):
                setattr(record, field, default())
        return True


def configure_logging() -> None:
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(settings.LOG_LEVEL.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(AppContextFilter())

    if settings.LOG_JSON:
        formatter = JsonFormatter(
            fmt=(
                "%(asctime)s %(levelname)s %(name)s %(message)s "
                "%(environment)s %(request_id)s %(correlation_id)s "
                "%(method)s %(path)s %(status_code)s %(duration_ms)s"
            ),
            rename_fields={
                "asctime": "timestamp",
                "levelname": "level",
                "name": "logger",
            },
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s "
            "[rid=%(request_id)s cid=%(correlation_id)s]"
        )

    handler.setFormatter(formatter)
    root.addHandler(handler)

    for name in ("uvicorn", "uvicorn.error"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers = []
        uvicorn_logger.propagate = True

    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.handlers = []
    uvicorn_access.propagate = False

    logger.setLevel(settings.LOG_LEVEL.upper())
