from collections.abc import Mapping
from typing import Any

from fastapi import HTTPException


class WithNotificationCodeHTTPException(HTTPException):
    """HTTP error with optional fields for the API JSON body (see exception_handlers)."""

    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        *,
        notification_code: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.notification_code = notification_code
