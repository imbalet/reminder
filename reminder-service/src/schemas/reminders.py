from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_core import PydanticCustomError


class BaseValidationModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def validate_at_least_one_not_none(self) -> "BaseValidationModel":
        if all(value is None for value in self.model_dump().values()):
            raise PydanticCustomError(
                "at_least_one_required",
                "At least one of the fields {fields} must be set",
                {
                    "fields": ", ".join(self.model_dump().keys()),
                    "model": self.__class__.__name__,
                },
            )
        return self


class ReminderCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=3, max_length=100)
    content: str = Field(min_length=3, max_length=2048)
    user_id: UUID
    remind_date: datetime


class ReminderResponse(ReminderCreate):
    id: UUID
    created_at: datetime
    edited_at: datetime | None


class ReminerEdit(BaseValidationModel):
    title: str | None = Field(default=None, min_length=3, max_length=100)
    content: str | None = Field(default=None, min_length=3, max_length=2048)
    remind_date: datetime | None = Field(default=None)
