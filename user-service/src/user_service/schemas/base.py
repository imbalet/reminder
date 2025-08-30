from pydantic import BaseModel, ConfigDict, model_validator
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
