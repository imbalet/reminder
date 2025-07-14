from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .base import BaseValidationModel
from .delivery_methods import DeliveryMethod


class ReminderCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=3, max_length=100)
    content: str = Field(min_length=3, max_length=2048)
    remind_date: datetime

    @field_validator("remind_date")
    def validate_remind_date(cls, v: datetime) -> datetime:
        current_time = datetime.now(timezone.utc)
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)

        if v <= current_time:
            raise ValueError("Reminder date must be in the future")
        return v


class ReminderResponse(ReminderCreate):
    id: UUID
    user_id: UUID
    created_at: datetime
    edited_at: datetime | None
    delivery_methods: list[DeliveryMethod]


class ReminderEdit(BaseValidationModel):
    title: str | None = Field(default=None, min_length=3, max_length=100)
    content: str | None = Field(default=None, min_length=3, max_length=2048)
    remind_date: datetime | None = Field(default=None)
