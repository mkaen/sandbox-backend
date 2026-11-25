from src.db.models import CryptoAsset
from src.features.crypto.schemas import PopularAssetSchema, PopularAssetsResponseSchema

def serialize_popular_assets_response(assets: list[CryptoAsset]) -> PopularAssetsResponseSchema:
    serialized_assets = [PopularAssetSchema.model_validate(asset) for asset in assets]
    return PopularAssetsResponseSchema(assets=serialized_assets)
