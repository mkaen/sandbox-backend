import math

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
