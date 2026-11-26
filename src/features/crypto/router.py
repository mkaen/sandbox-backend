from typing import Annotated

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from src.core.redis import get_redis
from src.features.crypto import service as s
from src.db.database import get_db
from src.db.models import User
from src.features.auth.dependencies import get_current_user
from src.features.users.dependencies import require_admin
from src.providers.coingecko.client import CoinGeckoClient
from src.providers.coingecko.dependencies import get_coingecko_client
from src.features.crypto.schemas import PopularAssetsResponseSchema, FearAndGreedIndexRespone

crypto_router_v1 = APIRouter(prefix="/v1/crypto", tags=["Crypto"])


@crypto_router_v1.get("/popular-assets", status_code=200, summary="Get popular crypto assets")
async def get_popular_asset_prices(
    db: Annotated[Session, Depends(get_db)],
) -> PopularAssetsResponseSchema:
    return s.get_popular_assets(db)


@crypto_router_v1.post("/refresh-popular-assets-manually", status_code=200, summary="Refresh and update Popular Asset Data manually")
async def refresh_asset_info_manually(
    db: Annotated[Session, Depends(get_db)],
    ck_client: Annotated[CoinGeckoClient, Depends(get_coingecko_client)],
    redis: Annotated[Redis, Depends(get_redis)],
    _: Annotated[User, Depends(require_admin)],
) -> PopularAssetsResponseSchema:
    return await s.refresh_asset_info_manually(ck_client, db, redis)


@crypto_router_v1.get("/fear-and-greed-index", status_code=200, summary="Fetch Fear and Greed index from server")
async def get_fear_and_greed_index(db: Annotated[Session, Depends(get_db)],) -> FearAndGreedIndexRespone:
    return s.get_fear_and_greed_index_data(db)


@crypto_router_v1.post("/refresh-fear-and-greed", status_code=200, summary="Refresh and update fear and greed index manually")
async def refresh_fear_and_greed_index_manually(
    db: Annotated[Session, Depends(get_db)],
    ck_client: Annotated[CoinGeckoClient, Depends(get_coingecko_client)],
    redis: Annotated[Redis, Depends(get_redis)],
    _: Annotated[User, Depends(require_admin)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FearAndGreedIndexRespone:
    return await s.refresh_fear_and_greed_index_manually(ck_client, db, redis, current_user)
