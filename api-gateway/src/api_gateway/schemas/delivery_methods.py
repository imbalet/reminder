from datetime import datetime
from enum import Enum
from typing import Literal, Union
from uuid import UUID

from pydantic import BaseModel, EmailStr


class DeliveryMethodEnum(str, Enum):
    TELEGRAM = "telegram"
    EMAIL = "email"


class MetaData(BaseModel):
    username: str | None = None  # Only for telegram


class TelegramDelivery(BaseModel):
    delivery_method: Literal[DeliveryMethodEnum.TELEGRAM]
    confirm_code: str


class EmailDelivery(BaseModel):
    delivery_method: Literal[DeliveryMethodEnum.EMAIL]
    contact_value: EmailStr


DeliveryMethodAdd = Union[TelegramDelivery, EmailDelivery]


class DeliveryMethodResponse(BaseModel):
    id: UUID
    user_id: UUID
    created_at: datetime
    delivery_method: DeliveryMethodEnum
    contact_value: str
    meta_data: MetaData
