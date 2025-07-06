from enum import Enum


class Entity(Enum):
    USER = "user"
    TOKEN = "token"
    DELIVERY_METHOD = "delivery_method"


class AppException(Exception):
    def __init__(self, entity: Entity, message: str) -> None:
        self.entity = entity
        super().__init__(message)


class NotFoundError(AppException):
    pass


class AlreadyExistsError(AppException):
    pass
