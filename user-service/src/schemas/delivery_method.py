from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class DeliveryMethodEnum(str, Enum):
    TELEGRAM = "telegram"
    EMAIL = "email"


class DeliveryMethod(BaseModel):
    delivery_method: DeliveryMethodEnum
    contact_value: str


class DeliveryMethodResponse(DeliveryMethod):
    id: UUID
