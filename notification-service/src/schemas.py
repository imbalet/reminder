from enum import Enum
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DeliveryMethod(str, Enum):
    TELEGRAM = "telegram"


class DeliveryRequest(BaseModel):
    method: DeliveryMethod
    recipient: str  # chat-id, email, etc


class Reminder(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    content: str
    remind_date: datetime
    delivery_requests: list[DeliveryRequest]


class Message(BaseModel):
    title: str
    content: str
