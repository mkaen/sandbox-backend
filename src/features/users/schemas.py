from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from src.constants import UserRoles


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
    image_reference: str | None = Field(alias="imageReference", default=None)
    role: UserRoles


class UserUpdatedDataRequestSchema(BaseModel):
    id: int
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    phone: str 
    email: EmailStr
    image_updated: bool = Field(alias="imageUpdated")
    old_password: str | None = Field(alias="oldPassword", default=None)
    new_password: str | None = Field(alias="newPassword", default=None)
    role: UserRoles | None = None
    
    
    @field_validator("first_name")
    def validate_first_name(cls, value):
        value = value.strip().title()
        if not value:
            raise ValueError("First name cannot be empty")
        if len(value) < 2:
            raise ValueError("First name must be at least 2 characters long")
        if len(value) > 25:
            raise ValueError("First name must be less than 25 characters long")
        return value


    @field_validator("last_name")
    def validate_last_name(cls, value):
        value = value.strip().title()
        if not value:
            raise ValueError("Last name cannot be empty")
        if len(value) < 2:
            raise ValueError("Last name must be at least 2 characters long")
        if len(value) > 25:
            raise ValueError("Last name must be less than 25 characters long")
        return value


    @field_validator("phone")
    def validate_phone(cls, value):
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


    @field_validator("old_password")
    def validate_old_password(cls, value):
        if not value:
            return value
        return value.strip()


    @field_validator("new_password")
    def validate_new_password(cls, value):
        if not value:
            return value
        value = value.strip()
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(value) > 30:
            raise ValueError("Password must be less than 30 characters long")
        return value

    @model_validator(mode="after")
    def validate_password_pair(self):
        if bool(self.old_password) != bool(self.new_password):
            raise ValueError("Both oldPassword and newPassword must be provided together")
        return self

    @field_validator("email")
    def validate_email(cls, value):
        value = value.strip().lower()
        if not value:
            raise ValueError("Email cannot be empty")
        if len(value) < 5:
            raise ValueError("Email must be at least 5 characters long")
        if len(value) > 40:
            raise ValueError("Email must be less than 40 characters long")
        return value
