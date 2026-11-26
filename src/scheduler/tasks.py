from src.constants import POPULAR_CRYPTO_ASSETS
from src.core.logger import logger
from src.features.crypto import service as crypto_service
from src.scheduler.context import job_resources


async def refresh_popular_assets() -> None:
    job_id = "job_popular_assets"
    logger.info("Scheduler job started: %s", job_id)
    async with job_resources() as (db, client):
        await crypto_service.fetch_and_save_assets(client, db, POPULAR_CRYPTO_ASSETS)
    logger.info("Scheduler job finished: %s", job_id)


async def refresh_fear_and_greed() -> None:
    job_id = "job_fear_and_greed"
    logger.info("Scheduler job started: %s", job_id)
    async with job_resources() as (db, client):
        await crypto_service.update_fear_and_greed_index(client, db)
    logger.info("Scheduler job finished: %s", job_id)