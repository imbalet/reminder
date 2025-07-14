from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

from .base import BaseValidationModel


class DeliveryMethodEnum(str, Enum):
    TELEGRAM = "telegram"
    EMAIL = "email"


class DeliveryMethod(BaseModel):
    delivery_method: DeliveryMethodEnum
    contact_value: str | None = Field(default=None)
    confirm_code: str | None = Field(default=None)


class DeliveryMethodResponse(DeliveryMethod):
    id: UUID
    user_id: UUID


class DeliveryMethodEdit(BaseValidationModel):
    delivery_method: DeliveryMethodEnum | None = None
    contact_value: str | None = None
