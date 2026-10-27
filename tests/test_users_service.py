import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session

from src.constants import SortOrder, SortType, UserRoles
from src.features.users.helper import USER_SORT_HELPER
from src.db.models import User
from src.features.users import repository, service
from src.features.users.schemas import PaginatedFilteredUsersRequestSchema, UserUpdatedDataRequestSchema


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

    @patch("src.features.users.service.repository.get_filtered_users")
    @patch("src.features.users.service.repository.count_filtered_users")
    def test_fetch_filtered_users_keeps_one_based_page_and_computes_total_pages(self, count, get_filtered):
        count.return_value = 25
        get_filtered.return_value = [_user(is_archived=False)]
        params = PaginatedFilteredUsersRequestSchema.model_validate({"nameFilter": None, "size": 10, "page": 1})

        result = service.fetch_filtered_users(self.db, params)

        self.assertEqual(result.page, 1)
        self.assertEqual(result.total_pages, 3)
        self.assertEqual(len(result.filtered_list), 1)

    def test_page_must_be_at_least_one(self):
        with self.assertRaises(ValidationError):
            PaginatedFilteredUsersRequestSchema.model_validate({"nameFilter": None, "page": 0})

    def test_all_sort_types_mapped(self):
        self.assertEqual(set(USER_SORT_HELPER), set(SortType))

    def test_get_filtered_users_offsets_by_zero_based_page_index(self):
        query = MagicMock()
        query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        with patch("src.features.users.repository._active_users_query", return_value=query):
            repository.get_filtered_users(self.db, None, None, 10, 3)

        query.order_by.return_value.offset.assert_called_once_with(20)

    def test_get_filtered_users_applies_sorting_to_the_paginated_query(self):
        query = MagicMock()
        ordered = query.order_by.return_value
        ordered.offset.return_value.limit.return_value.all.return_value = []

        with patch("src.features.users.repository._active_users_query", return_value=query):
            repository.get_filtered_users(self.db, None, None, 10, 1, SortType.EMAIL, SortOrder.ASC)

        query.order_by.assert_called_once()
        ordered.offset.assert_called_once_with(0)

    def test_fetch_filtered_users_passes_sort_params_to_repository(self):
        params = PaginatedFilteredUsersRequestSchema.model_validate({"sortBy": "lastName", "sortOrder": "ASC"})

        with (
            patch("src.features.users.service.repository.count_filtered_users", return_value=0),
            patch("src.features.users.service.repository.get_filtered_users", return_value=[]) as get_filtered,
        ):
            service.fetch_filtered_users(self.db, params)

        get_filtered.assert_called_once_with(self.db, None, None, 10, 1, SortType.LAST_NAME, SortOrder.ASC)


class ApplySortingTests(unittest.TestCase):
    @staticmethod
    def _order_by_sql(sort_by, sort_order):
        query = repository._apply_sorting(Session().query(User), sort_by, sort_order)
        sql = str(query.statement.compile(dialect=postgresql.dialect()))
        return sql.split("ORDER BY", 1)[1].strip()

    def test_defaults_to_newest_first(self):
        self.assertEqual(self._order_by_sql(None, None), "users.created_at DESC, users.id")

    def test_sorts_by_requested_column_and_direction(self):
        self.assertEqual(self._order_by_sql(SortType.EMAIL, SortOrder.ASC), "users.email ASC, users.id")
        self.assertEqual(self._order_by_sql(SortType.LAST_NAME, SortOrder.DESC), "users.last_name DESC, users.id")

    def test_sort_by_without_order_is_descending(self):
        self.assertEqual(self._order_by_sql(SortType.EMAIL, None), "users.email DESC, users.id")

    def test_sort_order_without_sort_by_uses_created_at(self):
        self.assertEqual(self._order_by_sql(None, SortOrder.ASC), "users.created_at ASC, users.id")

if __name__ == "__main__":
    unittest.main()
