from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.constants import POPULAR_CRYPTO_ASSETS
from src.providers.coingecko.client import CoinGeckoClient
from src.providers.coingecko.exceptions import CoinGeckoError
from src.features.crypto import repository as r
from src.db.models import CryptoAsset
from src.features.crypto import schemas as sch
from src.core.logger import logger


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


async def refresh_asset_info_manually(ck_client: CoinGeckoClient, db: Session):
    await fetch_and_save_assets(ck_client, db, POPULAR_CRYPTO_ASSETS)
