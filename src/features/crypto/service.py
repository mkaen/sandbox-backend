from datetime import datetime, timezone

from fastapi import HTTPException
from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy.orm import Session

from src.core.exceptions import WithNotificationCodeHTTPException as WNCHTTPException
from src.constants import CACHE_TIME, POPULAR_CRYPTO_ASSETS
from src.providers.coingecko.client import CoinGeckoClient
from src.providers.coingecko.exceptions import CoinGeckoError
from src.features.crypto import repository as r
from src.db.models import CryptoAsset, FearAndGreedIndex
from src.features.crypto import schemas as sch
from src.core.logger import logger



async def fetch_and_save_fear_and_greed_index(coingecko: CoinGeckoClient, db: Session):
    """
    Fetch Fear and Greed Index data from Coingecko and update database.
    
    Later this function is used with cron job to update assets prices etc regulary.
    """
    try:
        global_data = await coingecko.get_fear_and_greed_index()
        index = global_data.fear_and_greed_index
        created_at = datetime.fromtimestamp(global_data.updated_at, tz=timezone.utc).replace(tzinfo=None)
        fetched_data = FearAndGreedIndex(
            created_at=created_at,
            value=index.value,
            sentiment=index.sentiment,
        )
        saved = r.save_fear_and_greed_index(db, fetched_data)
        logger.info("SUCCESS: Fetched Fear and Greed Index from CoinGecko")
        return saved
    except CoinGeckoError as e:
        raise HTTPException(status_code=502, detail="Unable to fetch Fear and Greed index from CoinGecko") from e


async def fetch_and_save_assets(coingecko: CoinGeckoClient, db: Session, assets: list[str]) -> list[CryptoAsset]:
    """
    Fetch coins data from Coingecko and saves particular response into database.
    
    Later this function is used with cron job to update assets prices etc regulary.
    """
    if not assets:
        return []

    try:
        fetched_assets = []
        for coin in assets:
            asset = await coingecko.get_coin_data(id=coin)
            fetched_coin = CryptoAsset(
                symbol=asset.symbol,
                currency=asset.id,
                price_usd=float(asset.market_data.current_price.usd),
                market_cap=int(asset.market_data.market_cap.usd),
                ath_change=float(asset.market_data.ath_change_percentage.usd),
                change_24h=float(asset.market_data.price_change_percentage_24h),
                image_thumb=asset.image.thumb,
                image_small=asset.image.small,
                market_cap_rank=int(asset.market_cap_rank) or 0,
                updated_at=asset.last_updated
            )
            fetched_coin = r.save_asset_info(db, fetched_coin)
            fetched_assets.append(fetched_coin)
        logger.info(f"Fetched total {len(fetched_assets)} assets from CoinGecko.")
        return fetched_assets
    except CoinGeckoError as e:
        raise HTTPException(status_code=502, detail="Unable to fetch crypto prices") from e


def get_popular_assets(db: Session) -> sch.PopularAssetsResponseSchema:
    """Fetch popular crypto assets from database."""
    raw_assets = r.get_crypto_assets(db, POPULAR_CRYPTO_ASSETS)
    serialized_assets = [sch.PopularAssetSchema.model_validate(asset) for asset in raw_assets]
    return sch.PopularAssetsResponseSchema(assets=serialized_assets)


def get_fear_and_greed_index_data(db: Session) -> sch.FearAndGreedIndexRespone:
    return sch.FearAndGreedIndexRespone.model_validate(r.get_latest_fear_and_greed_data(db))


async def refresh_fear_and_greed_index_manually(
    ck_client: CoinGeckoClient, db: Session, redis: Redis,
) -> sch.FearAndGreedIndexRespone:
    """Refresh Fear and Greed Index from CoinGecko, at most once per cooldown period."""

    cooldown_minutes = CACHE_TIME["CG_fear_and_greed_index_refresh"]
    try:
        acquired = await r.acquire_refresh_cooldown(redis, cooldown_minutes * 60)
        if not acquired:
            retry_after = await r.get_refresh_cooldown_ttl(redis)
            raise WNCHTTPException(
                status_code=429,
                detail=f"Fear and Greed Index can be refreshed once every {cooldown_minutes} minutes",
                notification_code="FEAR_AND_GREED_INDEX_REFRESH_TIMEOUT",
                headers={"Retry-After": str(max(retry_after, 1))},
            )
    except RedisError as e:
        logger.error(f"Redis unavailable while checking refresh cooldown: {e}")
        raise HTTPException(status_code=503, detail="Refresh is temporarily unavailable") from e

    refreshed = False
    try:
        response = await fetch_and_save_fear_and_greed_index(ck_client, db)
        refreshed = True
        return sch.FearAndGreedIndexRespone.model_validate(response)
    finally:
        if not refreshed:
            await _release_refresh_cooldown_safely(redis)



async def refresh_asset_info_manually(ck_client: CoinGeckoClient, db: Session, redis: Redis):
    """Refresh popular assets from CoinGecko, at most once per cooldown period."""
    cooldown_minutes = CACHE_TIME["CG_popular_asset_refresh"]
    try:
        acquired = await r.acquire_refresh_cooldown(redis, cooldown_minutes * 60)
        if not acquired:
            retry_after = await r.get_refresh_cooldown_ttl(redis)
            raise WNCHTTPException(
                status_code=429,
                detail=f"Popular assets can be refreshed once every {cooldown_minutes} minutes",
                notification_code="ASSET_MANUAL_REFRESH_TIMEOUT",
                headers={"Retry-After": str(max(retry_after, 1))},
            )
    except RedisError as e:
        logger.error(f"Redis unavailable while checking refresh cooldown: {e}")
        raise HTTPException(status_code=503, detail="Refresh is temporarily unavailable") from e

    refreshed = False
    try:
        await fetch_and_save_assets(ck_client, db, POPULAR_CRYPTO_ASSETS)
        refreshed = True
    finally:
        if not refreshed:
            await _release_refresh_cooldown_safely(redis)


async def _release_refresh_cooldown_safely(redis: Redis) -> None:
    """Allow a retry after a failed refresh; never mask the original error."""
    try:
        await r.release_refresh_cooldown(redis)
    except RedisError as e:
        logger.error(f"Could not release refresh cooldown: {e}")
