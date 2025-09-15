from uuid import UUID
from pydantic import BaseModel, EmailStr
from .delivery_method import DeliveryMethodResponse


class User(BaseModel):
    id: UUID
    email: EmailStr
    name: str


class UserResponse(User):
    list[DeliveryMethodResponse]
