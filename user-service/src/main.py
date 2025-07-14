from fastapi import FastAPI

from src.exceptions import AppException
from src.exception_handler import (
    infrastructure_exception_handler,
    use_case_exception_handler,
)
from src.api import delivery_methods_router, notification_router
from src.use_cases import UseCaseException
from src.startup_init import startup_event
from src.logger import setup_logger

setup_logger()

app = FastAPI(
    lifespan=startup_event,
    swagger_ui_parameters={
        "tryItOutEnabled": True,
        "withCredentials": True,
    },
)
app.include_router(delivery_methods_router)
app.include_router(notification_router)

app.add_exception_handler(AppException, infrastructure_exception_handler)
app.add_exception_handler(UseCaseException, use_case_exception_handler)
