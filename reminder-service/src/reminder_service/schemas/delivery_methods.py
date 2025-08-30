from enum import Enum
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .base import BaseValidationModel


class DeliveryMethodEnum(str, Enum):
    TELEGRAM = "telegram"
    EMAIL = "email"


class DeliveryMethodBase(BaseModel):
    delivery_method: DeliveryMethodEnum
    contact_value: str


class DeliveryMethod(DeliveryMethodBase):
    id: UUID


class RmqReminder(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    content: str
    remind_date: datetime
    delivery_requests: list[DeliveryMethodBase] = Field(min_length=1)


class DeliveryMethodEdit(BaseValidationModel):
    delivery_method: DeliveryMethodEnum | None = None
    contact_value: str | None = None
