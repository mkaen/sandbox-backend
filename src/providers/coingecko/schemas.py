from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime

from src.constants import CryptoSentiment


class FiatUsd(BaseModel):
    usd: float


class CoinMarketData(BaseModel):
    current_price: FiatUsd
    market_cap: FiatUsd
    ath_change_percentage: FiatUsd
    price_change_percentage_24h: float | None = None


class CoinImage(BaseModel):
    thumb: str
    small: str


class CoinDataResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    symbol: str
    name: str
    market_cap_rank: int | None = None
    last_updated: datetime | None = None
    market_data: CoinMarketData
    image: CoinImage


class FearAndGreedIndexPayload(BaseModel):
    value: int = Field(ge=0, le=100)
    sentiment: CryptoSentiment

    @field_validator("sentiment", mode="before")
    @classmethod
    def normalize_sentiment(cls, value):
        """CoinGecko sends lowercase sentiment (e.g. "extreme_fear"); our enum values are uppercase."""
        return value.upper() if isinstance(value, str) else value


class GlobalMarketData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    fear_and_greed_index: FearAndGreedIndexPayload
    updated_at: int


class CoinGeckoGlobalResponse(BaseModel):
    data: GlobalMarketData
