class UseCaseException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

    pass


class ForbiddenException(UseCaseException):
    http_code = 403
    pass
