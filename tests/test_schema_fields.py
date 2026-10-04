import unittest

from pydantic import ValidationError

from src.features.auth.schemas import RegisterRequestSchema
from src.features.users import schema_fields
from src.features.users.schemas import UserUpdatedDataRequestSchema


class SchemaFieldsTests(unittest.TestCase):
    def test_registration_password_minimum_length(self):
        with self.assertRaises(ValidationError):
            RegisterRequestSchema.model_validate(
                {
                    "firstName": "Ada",
                    "lastName": "Lovelace",
                    "phone": "1234567",
                    "email": "ada@example.com",
                    "password": "short",
                }
            )

    def test_password_pair_requires_both_fields(self):
        with self.assertRaises(ValidationError):
            UserUpdatedDataRequestSchema.model_validate(
                {
                    "id": 1,
                    "firstName": "Ada",
                    "lastName": "Lovelace",
                    "phone": "1234567",
                    "email": "ada@example.com",
                    "oldPassword": "old-secret",
                }
            )

    def test_validate_person_name_normalizes(self):
        self.assertEqual(schema_fields.validate_person_name("  ada ", "First name"), "Ada")


if __name__ == "__main__":
    unittest.main()
