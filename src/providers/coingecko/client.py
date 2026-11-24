import httpx
from pydantic import ValidationError

from src.config import settings
from .exceptions import CoinGeckoError
from .schemas import CoinDataResponse, CoinGeckoGlobalResponse, GlobalMarketData

DEFAULT_CG_BASE_URL = "https://api.coingecko.com/api/v3"


def create_http_client() -> httpx.AsyncClient:
    base_url = settings.CG_BASE_URL or DEFAULT_CG_BASE_URL
    return httpx.AsyncClient(base_url=base_url.rstrip("/"), timeout=settings.CG_TIMEOUT)


class CoinGeckoClient:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http
        self._api_key_headers: dict[str, str] = {}
        if settings.CG_API_KEY:
            self._api_key_headers = {"x-cg-demo-api-key": settings.CG_API_KEY}

    async def get_coin_data(
        self,
        id: str,
        include_localization: bool = False,
        include_tickers: bool = False,
    ) -> CoinDataResponse:
        try:
            r = await self._http.get(
                f"/coins/{id}",
                headers=self._api_key_headers or None,
                params={
                    "localization": str(include_localization),
                    "tickers": str(include_tickers),
                },
            )

            r.raise_for_status()
            return CoinDataResponse.model_validate(r.json())

        except httpx.HTTPError as e:
            raise CoinGeckoError(str(e)) from e

    async def get_fear_and_greed_index(self) -> GlobalMarketData:
        try:
            r = await self._http.get("/global", headers=self._api_key_headers or None)
            r.raise_for_status()
            
            return CoinGeckoGlobalResponse.model_validate(r.json()).data

        except (httpx.HTTPError, ValidationError) as e:
            raise CoinGeckoError(str(e)) from e

