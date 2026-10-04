import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from src.constants import UserRoles
from src.features.users import service
from src.features.users.schemas import UserUpdatedDataRequestSchema


def _user(**overrides):
    data = dict(
        id=1,
        first_name="Ada",
        last_name="Lovelace",
        phone="1234567",
        email="ada@example.com",
        password="hashed",
        role=UserRoles.USER,
        is_active=True,
        image_reference=None,
    )
    data.update(overrides)
    return SimpleNamespace(**data)


class UsersServiceTests(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()

    @patch("src.features.users.service.repository.get_active_user_by_id")
    def test_update_user_rejects_mismatched_path_and_body_id(self, get_active):
        current = _user(id=1, role=UserRoles.USER)
        data = UserUpdatedDataRequestSchema.model_validate(
            {
                "id": 2,
                "firstName": "Ada",
                "lastName": "Lovelace",
                "phone": "1234567",
                "email": "ada@example.com",
            }
        )

        with self.assertRaises(HTTPException) as ctx:
            service.update_user_data(1, current, self.db, data)

        self.assertEqual(ctx.exception.status_code, 400)
        get_active.assert_not_called()

    @patch("src.features.users.service.repository.get_user_by_email")
    @patch("src.features.users.service.repository.get_active_user_by_id")
    @patch("src.features.users.service.repository.save_user")
    def test_update_user_rejects_duplicate_email(self, save_user, get_active, get_by_email):
        user = _user()
        get_active.return_value = user
        get_by_email.return_value = _user(id=99, email="other@example.com")
        current = _user(id=1, role=UserRoles.ADMIN)
        data = UserUpdatedDataRequestSchema.model_validate(
            {
                "id": 1,
                "firstName": "Ada",
                "lastName": "Lovelace",
                "phone": "1234567",
                "email": "other@example.com",
            }
        )

        with self.assertRaises(HTTPException) as ctx:
            service.update_user_data(1, current, self.db, data)

        self.assertEqual(ctx.exception.status_code, 400)
        save_user.assert_not_called()

    @patch("src.features.users.service.repository.get_active_user_by_id")
    def test_self_cannot_change_role(self, get_active):
        user = _user()
        get_active.return_value = user
        current = _user(id=1, role=UserRoles.USER)
        data = UserUpdatedDataRequestSchema.model_validate(
            {
                "id": 1,
                "firstName": "Ada",
                "lastName": "Lovelace",
                "phone": "1234567",
                "email": "ada@example.com",
                "role": UserRoles.ADMIN,
            }
        )

        with self.assertRaises(HTTPException) as ctx:
            service.update_user_data(1, current, self.db, data)

        self.assertEqual(ctx.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
