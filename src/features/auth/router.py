from fastapi import APIRouter, Response
from src.features.auth.schemas import LoginRequestSchema, RegisterRequestSchema
from fastapi.responses import JSONResponse
from src.features.auth.utils import create_access_token, set_access_token_cookie

auth_router_v1 = APIRouter(prefix="/v1/auth", tags=["auth"])

without_db = True


@auth_router_v1.post("/login", tags=["auth"])
async def login(login_request: LoginRequestSchema):
    print(f"Login request received: {login_request.email} {login_request.password}")
    return JSONResponse(content={"message": "Login successful!"}, status_code=200)


@auth_router_v1.post("/register", tags=["auth"], status_code=201)
async def register(registration_data: RegisterRequestSchema, response: Response):
    print(f"Register request received: {registration_data}")
    if without_db:
        access_token = create_access_token({"sub": registration_data.email})
        set_access_token_cookie(response, access_token)
        return {"message": "Registreerimine õnnestus"}
    return JSONResponse(content={"message": "Register failed!"}, status_code=400)
