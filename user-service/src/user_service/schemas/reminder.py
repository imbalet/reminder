from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from .delivery_method import DeliveryMethodEnum


class DeliveryMethod(BaseModel):
    id: UUID
    delivery_method: DeliveryMethodEnum
    contact_value: str


class Reminder(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    content: str
    remind_date: datetime
    created_at: datetime
    edited_at: datetime | None
    delivery_methods: list[DeliveryMethod]


class DeactivatedReminder(BaseModel):
    id: UUID
    title: str
    content: str
    remind_date: datetime
