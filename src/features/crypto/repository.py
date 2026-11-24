from redis.asyncio import Redis
from sqlalchemy.orm import Session

from src.db.models import CryptoAsset, FearAndGreedIndex
from src.core.logger import logger

REFRESH_COOLDOWN_KEY = "crypto:popular-assets:refresh-cooldown"


async def acquire_refresh_cooldown(redis: Redis, seconds: int) -> bool:
    """Atomically start the cooldown. Returns False if a refresh is already running or cooling down."""
    return bool(await redis.set(REFRESH_COOLDOWN_KEY, "1", nx=True, ex=seconds))


async def get_refresh_cooldown_ttl(redis: Redis) -> int:
    """Remaining cooldown in seconds (0 if the key is gone)."""
    return max(await redis.ttl(REFRESH_COOLDOWN_KEY), 0)


async def release_refresh_cooldown(redis: Redis) -> None:
    await redis.delete(REFRESH_COOLDOWN_KEY)


def get_crypto_assets(db: Session, assets: list[str]) -> list[CryptoAsset]:
    return (db.query(CryptoAsset)
        .filter(CryptoAsset.currency
        .in_(assets))
        .order_by(CryptoAsset.market_cap.desc())
        .all()
        )


def save_asset_info(db: Session, coin: CryptoAsset) -> CryptoAsset:
    """Add new coin into database."""
    existing_asset = get_asset_by_symbol(db, coin.symbol)
    if existing_asset:
        return update_asset_values(db, existing_asset, coin)
    db.add(coin)
    db.commit()
    db.refresh(coin)
    logger.info(f"New asset {coin} added into database")
    return coin


def get_asset_by_symbol(db: Session, symbol: str) -> CryptoAsset | None:
    return db.query(CryptoAsset).filter(CryptoAsset.symbol == symbol).first()


def update_asset_values(db: Session, existing_asset: CryptoAsset, to_update: CryptoAsset) -> CryptoAsset:
    """Update existing asset data in database."""
    existing_asset.price_usd = to_update.price_usd
    existing_asset.market_cap = to_update.market_cap
    existing_asset.ath_change = to_update.ath_change
    existing_asset.change_24h = to_update.change_24h
    existing_asset.market_cap_rank = to_update.market_cap_rank
    existing_asset.updated_at = to_update.updated_at
    db.commit()
    db.refresh(existing_asset)
    logger.info(f"Crypto asset {existing_asset} updated successfully.")
    return existing_asset


def save_fear_and_greed_index(db: Session, data: FearAndGreedIndex) -> FearAndGreedIndex:
    """Save Fear and Greed Index data into database."""
    db.add(data)
    db.commit()
    db.refresh(data)
    return data

