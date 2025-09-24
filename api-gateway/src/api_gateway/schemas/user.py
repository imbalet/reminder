from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserAuth(BaseModel):
    email: EmailStr
    password: str


class UserRegisterRequest(BaseModel):
    email: EmailStr
    name: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    registered_at: datetime
