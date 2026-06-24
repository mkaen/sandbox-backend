from fastapi import APIRouter
from pydantic import BaseModel

router_v1 = APIRouter(prefix="/v1/users", tags=["users"])
