from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserRegisterRequset(UserBase):
    password: str


class UserResponse(UserBase):
    id: UUID
    registered_at: datetime


class UserInDB(UserBase):
    id: UUID
    hashed_password: str
    registered_at: datetime
