from enum import Enum
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DeliveryMethodEnum(str, Enum):
    TELEGRAM = "telegram"
    EMAIL = "email"


class DeliveryMethod(BaseModel):
    delivery_method: DeliveryMethodEnum
    contact_value: str


class Reminder(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    content: str
    remind_date: datetime
    delivery_methods: list[DeliveryMethod]


class Message(BaseModel):
    title: str
    content: str


class ResultStatusEnum(str, Enum):
    ERROR = "error"
    SUCCESS = "success"


class Result(BaseModel):
    status: ResultStatusEnum
    data: dict
