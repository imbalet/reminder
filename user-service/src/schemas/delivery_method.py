from enum import Enum
from uuid import UUID

from pydantic import BaseModel

from .base import BaseValidationModel


class DeliveryMethodEnum(str, Enum):
    TELEGRAM = "telegram"
    EMAIL = "email"


class DeliveryMethod(BaseModel):
    delivery_method: DeliveryMethodEnum
    contact_value: str


class DeliveryMethodResponse(DeliveryMethod):
    id: UUID
    user_id: UUID


class DeliveryMethodEdit(BaseValidationModel):
    delivery_method: DeliveryMethodEnum | None = None
    contact_value: str | None = None


class DeliveryMethodConfirm(BaseModel):
    id: UUID
    user_id: UUID
    is_confirmed: bool
