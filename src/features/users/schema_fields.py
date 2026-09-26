"""Shared field normalization and validation for user-related Pydantic schemas."""

from src.constants import MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH


def validate_person_name(value: str, label: str) -> str:
    value = value.strip().title()
    if not value:
        raise ValueError(f"{label} cannot be empty")
    if len(value) < 2:
        raise ValueError(f"{label} must be at least 2 characters long")
    if len(value) > 25:
        raise ValueError(f"{label} must be less than 25 characters long")
    return value


def validate_phone(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("Phone cannot be empty")
    if not value.isdigit():
        raise ValueError("Phone must contain only digits")
    if len(value) < 7:
        raise ValueError("Phone must be at least 7 characters long")
    if len(value) > 15:
        raise ValueError("Phone must be less than 15 characters long")
    return value


def validate_user_email(value: str) -> str:
    value = value.strip().lower()
    if not value:
        raise ValueError("Email cannot be empty")
    if len(value) < 5:
        raise ValueError("Email must be at least 5 characters long")
    if len(value) > 40:
        raise ValueError("Email must be less than 40 characters long")
    return value


def validate_registration_password(value: str) -> str:
    value = value.strip()
    if len(value) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long")
    if len(value) > MAX_PASSWORD_LENGTH:
        raise ValueError(f"Password must be less than {MAX_PASSWORD_LENGTH} characters long")
    return value


def validate_optional_new_password(value: str | None) -> str | None:
    if not value:
        return value
    value = value.strip()
    if len(value) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long")
    if len(value) > MAX_PASSWORD_LENGTH:
        raise ValueError(f"Password must be less than {MAX_PASSWORD_LENGTH} characters long")
    return value
