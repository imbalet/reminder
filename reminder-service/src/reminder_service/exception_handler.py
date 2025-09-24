import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse

from reminder_service.use_cases import BadRequestException, ForbiddenException

logger = logging.getLogger(__name__)


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
                content="Unexpected error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
