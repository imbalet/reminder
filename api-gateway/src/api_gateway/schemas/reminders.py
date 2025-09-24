from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .delivery_methods import DeliveryMethodEnum


class DeliveryMethod(BaseModel):
    id: UUID
    user_id: UUID
    delivery_method: DeliveryMethodEnum
    contact_value: str


class Status(Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    INACTIVE = "inactive"


class ReminderBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str
    content: str
    remind_date: datetime


class ReminderCreate(ReminderBase):
    delivery_methods_ids: list[UUID]


class ReminderResponse(ReminderBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    status: Status
    edited_at: datetime | None
    delivery_methods: list[DeliveryMethod]


class ReminderEdit(BaseModel):
    title: str | None
    content: str | None
    remind_date: datetime | None
    delivery_methods_ids: list[UUID] | None
