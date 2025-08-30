from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserAuth(BaseModel):
    email: EmailStr
    password: str


class UserBase(BaseModel):
    email: EmailStr


class UserRegisterRequset(UserBase):
    name: str
    password: str


class UserResponse(UserBase):
    id: UUID
    registered_at: datetime
