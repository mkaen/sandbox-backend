import unittest

from pydantic import ValidationError

from src.constants import SortOrder, SortType
from src.features.auth.schemas import RegisterRequestSchema
from src.features.users import schema_fields
from src.features.users.schemas import PaginatedFilteredUsersRequestSchema, UserUpdatedDataRequestSchema


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

    def test_filter_request_parses_sort_by_enum_values(self):
        self.assertEqual(
            PaginatedFilteredUsersRequestSchema.model_validate({"sortBy": "lastName"}).sort_by,
            SortType.LAST_NAME,
        )
        self.assertEqual(
            PaginatedFilteredUsersRequestSchema.model_validate({"sortBy": "email"}).sort_by,
            SortType.EMAIL,
        )
        self.assertEqual(
            PaginatedFilteredUsersRequestSchema.model_validate({"sortBy": SortType.EMAIL}).sort_by,
            SortType.EMAIL,
        )

    def test_filter_request_omitted_sort_by_is_none(self):
        params = PaginatedFilteredUsersRequestSchema.model_validate({})
        self.assertIsNone(params.sort_by)
        self.assertIsNone(params.sort_order)

    def test_filter_request_parses_camel_case_sort_by(self):
        params = PaginatedFilteredUsersRequestSchema.model_validate({"sortBy": "lastName", "sortOrder": "DESC"})
        self.assertEqual(params.sort_by, SortType.LAST_NAME)
        self.assertEqual(params.sort_order, SortOrder.DESC)

    def test_filter_request_rejects_unknown_sort_by(self):
        with self.assertRaises(ValidationError):
            PaginatedFilteredUsersRequestSchema.model_validate({"sortBy": "createdAt"})


if __name__ == "__main__":
    unittest.main()
