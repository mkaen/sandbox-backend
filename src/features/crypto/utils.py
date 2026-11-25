from datetime import datetime, timezone

from src.db.models import CryptoAsset
from src.features.crypto.schemas import PopularAssetSchema, PopularAssetsResponseSchema


def to_utc_naive(dt: datetime | None) -> datetime:
    """Persist instants as UTC-naive, matching Fear & Greed and other crypto timestamps."""
    if dt is None:
        return datetime.now(timezone.utc).replace(tzinfo=None)
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(timezone.utc).replace(tzinfo=None)

def serialize_popular_assets_response(assets: list[CryptoAsset]) -> PopularAssetsResponseSchema:
    """Serialize and return ORM assets into PopularAssetsResponseSchema."""
    serialized_assets = [PopularAssetSchema.model_validate(asset) for asset in assets]
    return PopularAssetsResponseSchema(assets=serialized_assets)
