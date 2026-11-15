from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_serializer

from src.features.crypto import schema_fields as sf


class PopularAssetSchema(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        serialize_by_alias=True,

    )
    currency: str
    price_usd: float = Field(alias="priceUsd")
    ath_change: float = Field(alias="athChange")
    change_24h: float = Field(alias="change24h")
    market_cap: int = Field(alias="marketCapUsd")
    market_cap_rank: int = Field(alias="marketCapRank")
    image_thumb: str = Field(alias="imageThumb")
    updated_at: datetime = Field(alias="updatedAt")

    @field_serializer("currency", mode="plain")
    @classmethod
    def validate_currency(cls, value):
        return value.title()

    @field_serializer("price_usd", mode="plain")
    @classmethod
    def validate_price(cls, value):
        return sf.format_price(value)
    
    @field_serializer("ath_change", mode="plain")
    @classmethod
    def validate_ath_change(cls, value):
        return sf.validate_percent_value(value)

    @field_serializer("change_24h", mode="plain")
    @classmethod
    def validate_change_24h(cls, value):
        return sf.validate_percent_value(value)

    @field_serializer("market_cap", mode="plain")
    @classmethod
    def validate_market_cap(cls, value):
        return f"{value:,}"

    @field_serializer("updated_at", mode="plain")
    @classmethod
    def validate_updated_at(cls, value):
        return value.strftime("%H:%M %d.%m.%Y")


class PopularAssetsResponseSchema(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias=True
    )
    assets: list[PopularAssetSchema]
