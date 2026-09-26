import unittest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

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


if __name__ == "__main__":
    unittest.main()
