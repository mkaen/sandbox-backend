from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from src.constants import UserRoles
from src.features.users import schema_fields


class CreateUserData(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: EmailStr
    password: str


class UserResponseSchema(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        serialize_by_alias=True,
    )

    id: int
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    phone: str
    email: EmailStr
    role: UserRoles


class UserUpdatedDataRequestSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    phone: str
    email: EmailStr
    old_password: str | None = Field(alias="oldPassword", default=None)
    new_password: str | None = Field(alias="newPassword", default=None)
    role: UserRoles | None = None

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

    @field_validator("old_password")
    @classmethod
    def validate_old_password(cls, value):
        if not value:
            return value
        return value.strip()

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value):
        return schema_fields.validate_optional_new_password(value)

    @model_validator(mode="after")
    def validate_password_pair(self):
        if bool(self.old_password) != bool(self.new_password):
            raise ValueError("Both oldPassword and newPassword must be provided together")
        return self

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        return schema_fields.validate_user_email(value)
