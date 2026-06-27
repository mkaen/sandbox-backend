from pydantic import BaseModel, Field, ConfigDict

class LoginRequestSchema(BaseModel):
    email: str
    password: str

class RegisterRequestSchema(BaseModel):
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    phone: str
    email: str = Field(alias="email")
    password: str = Field(min_length=8)
    has_image: bool = Field(alias="hasImage", default=False)


# class RegisterResponseSchema(BaseModel):
#     model_config = ConfigDict(populate_by_name=True)

#     id: int
#     first_name: str = Field(alias="firstName")
#     last_name: str = Field(alias="lastName")
#     phone: str
#     email: str
#     image_reference: str = Field(alias="imageReference", default=None)
