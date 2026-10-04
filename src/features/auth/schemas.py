
from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator

from src.features.users import schema_fields


class LoginRequestSchema(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        return schema_fields.validate_user_email(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        return schema_fields.validate_registration_password(value)


class RegisterRequestSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    phone: str
    email: EmailStr
    password: str

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, value):
        return schema_fields.validate_person_name(value, "First name")

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, value):
        return schema_fields.validate_person_name(value, "Last name")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        return schema_fields.validate_phone(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        return schema_fields.validate_registration_password(value)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        return schema_fields.validate_user_email(value)
