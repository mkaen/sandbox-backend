from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.features.crypto import service as s
from src.db.database import get_db
from src.providers.coingecko.client import CoinGeckoClient
from src.providers.coingecko.dependencies import get_coingecko_client
from src.features.crypto.schemas import PopularAssetsResponseSchema

crypto_router_v1 = APIRouter(prefix="/v1/crypto", tags=["Crypto"])


@crypto_router_v1.get("/popular-assets", status_code=200)
async def get_popular_asset_prices(
    db: Annotated[Session, Depends(get_db)],
) -> PopularAssetsResponseSchema:
    return s.get_popular_assets(db)


@crypto_router_v1.post("/refresh-popular-assets-manually", status_code=200)
async def refresh_asset_info_manually(
    db: Annotated[Session, Depends(get_db)],
    ck_client: Annotated[CoinGeckoClient, Depends(get_coingecko_client)],
):
    await s.refresh_asset_info_manually(ck_client, db)
