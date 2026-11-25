import math
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from src.config import settings

def format_price(value: float) -> str:
    if not value:
        raise ValueError("Missing price value to validate")
    if value < 10:
        return f"{value:.4g}"
    if value >= 10:
        return f"{value:,.2f}"

def validate_percent_value(value: float) -> str:
    if not value:
        raise ValueError("Missing value to validate")
    if value < -100:
        raise ValueError(f"Percent value {value}. Price cannot drop more than 100%.")
    return value.__round__(2)


def format_display_datetime(value: datetime) -> str:
    """Format a UTC-naive (or aware) instant for API output in settings.TIMEZONE."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    local = value.astimezone(ZoneInfo(settings.TIMEZONE))
    return local.strftime("%H:%M %d.%m.%Y")
