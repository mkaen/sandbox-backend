from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.features.crypto import service as s
from src.db.database import get_db
from src.features.crypto.schemas import PopularAssetsResponseSchema

crypto_router_v1 = APIRouter(prefix="/v1/crypto", tags=["Crypto"])


@crypto_router_v1.get("/popular-assets")
async def get_popular_asset_prices(
    db: Annotated[Session, Depends(get_db)],
) -> PopularAssetsResponseSchema:
    return s.get_popular_assets(db)
