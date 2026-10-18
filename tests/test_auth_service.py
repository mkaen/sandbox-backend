import unittest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from src.config import settings
from src.features.auth.schemas import RegisterRequestSchema
from src.features.auth import service as auth_service


class AuthServiceTests(unittest.TestCase):
    @patch("src.features.auth.service.create_user")
    @patch("src.features.auth.service.get_user_by_email")
    def test_register_rejects_duplicate_email(self, get_by_email, create_user):
        get_by_email.return_value = object()
        db = MagicMock()
        response = MagicMock()
        registration = RegisterRequestSchema.model_validate(
            {
                "firstName": "Ada",
                "lastName": "Lovelace",
                "phone": "1234567",
                "email": "ada@example.com",
                "password": "long-enough",
            }
        )

        with self.assertRaises(HTTPException) as ctx:
            auth_service.register_user(registration, response, db)

        self.assertEqual(ctx.exception.status_code, 400)
        create_user.assert_not_called()

    @patch("src.features.auth.service.clear_auth_cookies")
    @patch("src.features.auth.service.revoke_refresh_token")
    def test_logout_revokes_refresh_token_and_clears_cookies(self, revoke, clear_cookies):
        db = MagicMock()
        request = MagicMock()
        request.cookies = {settings.REFRESH_TOKEN_COOKIE_NAME: "refresh-token"}
        response = MagicMock()

        auth_service.logout_user(request, response, db, 1)

        revoke.assert_called_once_with(db, "refresh-token")
        clear_cookies.assert_called_once_with(response)

    @patch("src.features.auth.service.clear_auth_cookies")
    @patch("src.features.auth.service.revoke_refresh_token")
    def test_logout_without_refresh_cookie_still_clears_cookies(self, revoke, clear_cookies):
        request = MagicMock()
        request.cookies = {}
        response = MagicMock()

        auth_service.logout_user(request, response, MagicMock(), 1)

        revoke.assert_not_called()
        clear_cookies.assert_called_once_with(response)


if __name__ == "__main__":
    unittest.main()
