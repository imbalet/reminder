from uuid import UUID
from pydantic import BaseModel, EmailStr
from .delivery_method import DeliveryMethod


class User(BaseModel):
    id: UUID
    email: EmailStr
    name: str


class UserResponse(User):
    list[DeliveryMethod]
