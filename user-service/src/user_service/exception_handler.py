import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse

from user_service.exceptions import AlreadyExistsError, NotFoundError
from user_service.use_cases import ForbiddenException, BadRequestException

logger = logging.getLogger(__name__)


def infrastructure_exception_handler(request: Request, exc: Exception):
    match exc:
        case AlreadyExistsError():
            return JSONResponse(
                content={"detail": str(exc)},
                status_code=status.HTTP_409_CONFLICT,
            )
        case NotFoundError():
            return JSONResponse(
                content={"detail": str(exc)},
                status_code=status.HTTP_404_NOT_FOUND,
            )
        case _:
            logger.error("Unexpected api error:", exc_info=exc)
            return JSONResponse(
                content={"detail": "Unexpected error"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def use_case_exception_handler(request: Request, exc: Exception):
    match exc:
        case ForbiddenException():
            return JSONResponse(
                content={"detail": str(exc)},
                status_code=exc.http_code,
            )
        case BadRequestException():
            return JSONResponse(
                content={"detail": str(exc)},
                status_code=exc.http_code,
            )
        case _:
            logger.error("Unexpected use case error:", exc_info=exc)
            return JSONResponse(
                content={"detail": "Unexpected error"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
