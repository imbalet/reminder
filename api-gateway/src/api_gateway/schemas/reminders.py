from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .base import BaseValidationModel
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


class ReminderBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=3, max_length=100)
    content: str = Field(min_length=3, max_length=2048)
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


class ReminderEdit(BaseValidationModel):
    title: str | None = Field(default=None, min_length=3, max_length=100)
    content: str | None = Field(default=None, min_length=3, max_length=2048)
    remind_date: datetime | None = Field(default=None)
    delivery_methods_ids: list[UUID] | None = Field(default=None)
