import unittest
from types import SimpleNamespace
from uuid import uuid4

from src.constants import UserRoles
from src.features.users.schemas import UserResponseSchema


def _user(**overrides):
    data = dict(
        id=1,
        first_name="Ada",
        last_name="Lovelace",
        phone="1234567",
        email="ada@example.com",
        role=UserRoles.USER,
        image_reference=None,
    )
    data.update(overrides)
    return SimpleNamespace(**data)


class UserResponseSchemaTests(unittest.TestCase):
    def test_does_not_expose_image_reference_when_user_has_image(self):
        payload = UserResponseSchema.model_validate(_user(image_reference=uuid4())).model_dump(by_alias=True)

        self.assertEqual(
            payload,
            {
                "id": 1,
                "firstName": "Ada",
                "lastName": "Lovelace",
                "phone": "1234567",
                "email": "ada@example.com",
                "role": UserRoles.USER,
            },
        )

    def test_open_api_schema_omits_image_fields(self):
        properties = UserResponseSchema.model_json_schema()["properties"]

        self.assertNotIn("hasImage", properties)
        self.assertNotIn("imageReference", properties)
        self.assertNotIn("image_reference", properties)


if __name__ == "__main__":
    unittest.main()
