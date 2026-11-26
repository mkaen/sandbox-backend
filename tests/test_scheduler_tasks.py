import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from src.scheduler import tasks


class SchedulerTasksTests(unittest.IsolatedAsyncioTestCase):
    @patch("src.scheduler.tasks.job_resources")
    async def test_refresh_popular_assets_propagates_fetch_failure(self, job_resources: AsyncMock) -> None:
        client = object()
        db = object()
        job_resources.return_value.__aenter__.return_value = (db, client)
        job_resources.return_value.__aexit__.return_value = None

        with patch(
            "src.scheduler.tasks.crypto_service.fetch_and_save_assets",
            new_callable=AsyncMock,
            side_effect=HTTPException(status_code=502, detail="Unable to fetch crypto prices"),
        ):
            with self.assertRaises(HTTPException):
                await tasks.refresh_popular_assets()


if __name__ == "__main__":
    unittest.main()