from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PopularAssetSchema(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias=True
    )

    currency: str
    price: float
    volume_24h_usd: int = Field(alias="volume24hUsd")
    change_24h: float = Field(alias="change24h")
    market_cap: int = Field(alias="marketCap")
    image_thumb: str = Field(alias="imageThumb")
    updated_at: datetime


class PopularAssetsResponseSchema(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias=True
    )

    assets: list(PopularAssetSchema)
