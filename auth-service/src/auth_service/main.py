from fastapi import FastAPI

from auth_service.exceptions import AppException
from auth_service.exception_handler import exception_handler
from auth_service.api import auth_router, jwks_router
from auth_service.logger import setup_logger
from auth_service.startup_init import startup_event

setup_logger()


app = FastAPI(
    lifespan=startup_event,
    swagger_ui_parameters={
        "tryItOutEnabled": True,
        "withCredentials": True,
    },
)
app.include_router(auth_router)
app.include_router(jwks_router)

app.add_exception_handler(AppException, exception_handler)
