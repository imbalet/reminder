from __future__ import annotations

from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class DeliveryMethodEnum(str, Enum):
    TELEGRAM = "telegram"
    EMAIL = "email"


class DeliveryMethod(BaseModel):
    id: UUID
    user_id: UUID
    delivery_method: DeliveryMethodEnum
    contact_value: str
