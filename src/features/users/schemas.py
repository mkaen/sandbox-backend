from pydantic import BaseModel, ConfigDict, EmailStr, Field

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
