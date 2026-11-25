from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from sqlalchemy.orm import Session

from src.db.database import SessionLocal
from src.providers.coingecko.client import CoinGeckoClient, create_http_client


@asynccontextmanager
async def job_resources() -> AsyncIterator[tuple[Session, CoinGeckoClient]]:
    """DB session and CoinGecko client for scheduled jobs (no Redis)."""
    http: httpx.AsyncClient = create_http_client()
    client = CoinGeckoClient(http)
    db = SessionLocal()
    try:
        yield db, client
    finally:
        db.close()
        await http.aclose()