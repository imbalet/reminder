from enum import Enum
from uuid import UUID

from pydantic import BaseModel, model_validator
from pydantic_core import PydanticCustomError

from .base import BaseValidationModel


class DeliveryMethodEnum(str, Enum):
    TELEGRAM = "telegram"
    EMAIL = "email"


class DeliveryMethod(BaseModel):
    delivery_method: DeliveryMethodEnum
    contact_value: str | None = None
    confirm_code: str | None = None


class DeliveryMethodAdd(DeliveryMethod):
    @model_validator(mode="after")
    def validate_at_least_one_not_none(self) -> "DeliveryMethodAdd":
        if self.delivery_method == DeliveryMethodEnum.TELEGRAM and (
            self.confirm_code is None or self.contact_value is not None
        ):
            raise PydanticCustomError(
                "confirm_code_required",
                "Confirm code required for telegram delivery method",
                {
                    "fields": ", ".join(
                        self.model_dump(
                            include={str(self.confirm_code), str(self.contact_value)}
                        ).keys()
                    ),
                },
            )
        if self.delivery_method == DeliveryMethodEnum.EMAIL and (
            self.confirm_code is not None or self.contact_value is None
        ):
            raise PydanticCustomError(
                "contact_value_required",
                "Contact value required for email delivery method",
                {
                    "fields": ", ".join(
                        self.model_dump(
                            include={str(self.confirm_code), str(self.contact_value)}
                        ).keys()
                    ),
                },
            )
        return self


class DeliveryMethodResponse(DeliveryMethod):
    id: UUID
    user_id: UUID


class DeliveryMethodEdit(BaseValidationModel):
    delivery_method: DeliveryMethodEnum | None = None
    contact_value: str | None = None
