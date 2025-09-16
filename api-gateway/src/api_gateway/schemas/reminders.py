from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .base import BaseValidationModel
from .delivery_methods import DeliveryMethodResponse


class Status(Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class ReminderCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=3, max_length=100)
    content: str = Field(min_length=3, max_length=2048)
    remind_date: datetime


class ReminderResponse(ReminderCreate):
    id: UUID
    user_id: UUID
    created_at: datetime
    status: Status
    edited_at: datetime | None
    delivery_methods: list[DeliveryMethodResponse]


class ReminerEdit(BaseValidationModel):
    title: str | None = Field(default=None, min_length=3, max_length=100)
    content: str | None = Field(default=None, min_length=3, max_length=2048)
    remind_date: datetime | None = Field(default=None)
