from src.constants import UserRoles
from features.auth.utils import generate_image_reference
from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator

class LoginRequestSchema(BaseModel):
    email: str
    password: str

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

    @field_validator("password")
    def validate_password(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Password cannot be empty")
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return value


class RegisterRequestSchema(BaseModel):
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    phone: str 
    email: EmailStr
    password: str
    has_image: bool = Field(
        alias="hasImage",
        description="If user has an image, generate reference (uuid) and return it to frontend"
        )
    
    
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


    @field_validator("password")
    def validate_password(cls, value):
        value = value.strip()
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(value) > 30:
            raise ValueError("Password must be less than 30 characters long")
        return value

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

    @field_validator("has_image")
    def validate_has_image(cls, value: bool):
        if value:
            print(f"Generating image reference: {value}")
            return generate_image_reference()
        else:
            return ""


class AuthorizedUserResponseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    phone: str 
    email: EmailStr
    image_reference: str = Field(alias="imageReference", default=None)
    role: UserRoles = Field(alias="role")
