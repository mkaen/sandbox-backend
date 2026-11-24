from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


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
