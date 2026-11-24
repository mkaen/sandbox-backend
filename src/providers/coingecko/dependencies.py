from fastapi import Request

from src.providers.coingecko.client import CoinGeckoClient


def get_coingecko_client(request: Request) -> CoinGeckoClient:
    return request.app.state.coingecko_client
