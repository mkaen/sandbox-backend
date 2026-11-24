

class CoinGeckoError(Exception):
    """Base exception for all CoinGecko errors."""

    def __init__(self, message: str, *, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class CoinGeckoRateLimitError(CoinGeckoError):
    """429 - Reached CoinGecko request limit."""

    def __init__(self, message: str = "CoinGecko rate limit exceeded", *, retry_after: int | None = None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class CoinGeckoNotFoundError(CoinGeckoError):
    """404 - Could not find coin id."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class CoinGeckoAuthError(CoinGeckoError):
    """401/403 - API key is missing or key is wrong."""

    def __init__(self, message: str = "Invalid or missing API key", *, status_code: int = 401):
        super().__init__(message, status_code=status_code)


class CoinGeckoUnavailableError(CoinGeckoError):
    """Network error, timeout või 5xx - teenus pole kättesaadav."""