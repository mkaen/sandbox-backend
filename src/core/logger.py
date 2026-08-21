import logging
import sys
from contextvars import ContextVar

from pythonjsonlogger.json import JsonFormatter

from src.config import settings

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

logger = logging.getLogger(settings.LOGGER_NAME)


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not getattr(record, "request_id", None):
            record.request_id = request_id_var.get()
        record.environment = getattr(record, "environment", None) or settings.ENVIRONMENT
        for field in ("method", "path", "status_code", "duration_ms"):
            if not hasattr(record, field):
                setattr(record, field, None)
        return True


def configure_logging() -> None:
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(settings.LOG_LEVEL.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestContextFilter())

    if settings.LOG_JSON:
        formatter = JsonFormatter(
            fmt=(
                "%(asctime)s %(levelname)s %(name)s %(message)s "
                "%(environment)s %(request_id)s %(method)s %(path)s "
                "%(status_code)s %(duration_ms)s"
            ),
            rename_fields={"asctime": "timestamp", "levelname": "level", "name": "logger"},
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s [rid=%(request_id)s]"
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
