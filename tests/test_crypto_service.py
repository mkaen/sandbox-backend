import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException
from redis.exceptions import ConnectionError as RedisConnectionError

from src.constants import CACHE_TIME, POPULAR_CRYPTO_ASSETS
from src.features.crypto import repository, service

COOLDOWN_SECONDS = CACHE_TIME["CG_popular_asset_refresh"] * 60


class RefreshAssetInfoManuallyTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db = MagicMock()
        self.ck_client = MagicMock()
        self.redis = AsyncMock()

    @patch("src.features.crypto.service.fetch_and_save_assets", new_callable=AsyncMock)
    async def test_refresh_runs_and_keeps_cooldown_when_allowed(self, fetch):
        self.redis.set.return_value = True

        await service.refresh_asset_info_manually(self.ck_client, self.db, self.redis)

        self.redis.set.assert_awaited_once_with(repository.REFRESH_COOLDOWN_KEY, "1", nx=True, ex=COOLDOWN_SECONDS)
        fetch.assert_awaited_once_with(self.ck_client, self.db, POPULAR_CRYPTO_ASSETS)
        self.redis.delete.assert_not_awaited()

    @patch("src.features.crypto.service.fetch_and_save_assets", new_callable=AsyncMock)
    async def test_refresh_returns_429_with_retry_after_during_cooldown(self, fetch):
        self.redis.set.return_value = None
        self.redis.ttl.return_value = 420

        with self.assertRaises(HTTPException) as ctx:
            await service.refresh_asset_info_manually(self.ck_client, self.db, self.redis)

        self.assertEqual(ctx.exception.status_code, 429)
        self.assertEqual(ctx.exception.headers, {"Retry-After": "420"})
        fetch.assert_not_awaited()
        self.redis.delete.assert_not_awaited()

    @patch("src.features.crypto.service.fetch_and_save_assets", new_callable=AsyncMock)
    async def test_refresh_retry_after_is_at_least_one_second(self, fetch):
        self.redis.set.return_value = None
        self.redis.ttl.return_value = -2

        with self.assertRaises(HTTPException) as ctx:
            await service.refresh_asset_info_manually(self.ck_client, self.db, self.redis)

        self.assertEqual(ctx.exception.headers, {"Retry-After": "1"})

    @patch("src.features.crypto.service.fetch_and_save_assets", new_callable=AsyncMock)
    async def test_failed_refresh_releases_cooldown_and_reraises(self, fetch):
        self.redis.set.return_value = True
        fetch.side_effect = HTTPException(status_code=502, detail="Unable to fetch crypto prices")

        with self.assertRaises(HTTPException) as ctx:
            await service.refresh_asset_info_manually(self.ck_client, self.db, self.redis)

        self.assertEqual(ctx.exception.status_code, 502)
        self.redis.delete.assert_awaited_once_with(repository.REFRESH_COOLDOWN_KEY)

    @patch("src.features.crypto.service.fetch_and_save_assets", new_callable=AsyncMock)
    async def test_failed_release_does_not_mask_original_error(self, fetch):
        self.redis.set.return_value = True
        self.redis.delete.side_effect = RedisConnectionError("down")
        fetch.side_effect = HTTPException(status_code=502, detail="Unable to fetch crypto prices")

        with self.assertRaises(HTTPException) as ctx:
            await service.refresh_asset_info_manually(self.ck_client, self.db, self.redis)

        self.assertEqual(ctx.exception.status_code, 502)

    @patch("src.features.crypto.service.fetch_and_save_assets", new_callable=AsyncMock)
    async def test_redis_outage_returns_503_without_calling_coingecko(self, fetch):
        self.redis.set.side_effect = RedisConnectionError("down")

        with self.assertRaises(HTTPException) as ctx:
            await service.refresh_asset_info_manually(self.ck_client, self.db, self.redis)

        self.assertEqual(ctx.exception.status_code, 503)
        fetch.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
