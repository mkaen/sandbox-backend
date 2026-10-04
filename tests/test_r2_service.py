import unittest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from src.features.r2 import service as r2_service


class R2ServiceTests(unittest.TestCase):
    @patch("src.features.r2.service.requests.get")
    @patch("src.features.r2.service._worker_url", return_value="https://worker.example")
    @patch("src.features.r2.service._upload_key", return_value="secret")
    def test_fetch_image_maps_404_to_http_exception(self, _key, _url, mock_get):
        response = MagicMock(status_code=404, ok=False, text="missing")
        mock_get.return_value = response

        with self.assertRaises(HTTPException) as ctx:
            r2_service.fetch_image("profile_images", "abc-123")

        self.assertEqual(ctx.exception.status_code, 404)

    @patch("src.features.r2.service.requests.get")
    @patch("src.features.r2.service._worker_url", return_value="https://worker.example")
    @patch("src.features.r2.service._upload_key", return_value="secret")
    def test_fetch_image_maps_upstream_error_to_502(self, _key, _url, mock_get):
        response = MagicMock(status_code=503, ok=False, text="upstream down")
        mock_get.return_value = response

        with self.assertRaises(HTTPException) as ctx:
            r2_service.fetch_image("profile_images", "abc-123")

        self.assertEqual(ctx.exception.status_code, 502)


if __name__ == "__main__":
    unittest.main()
