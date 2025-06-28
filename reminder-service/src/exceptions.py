class AppException(Exception):
    pass


class NotFoundError(AppException):
    pass


class AlreadyExistsError(AppException):
    pass
