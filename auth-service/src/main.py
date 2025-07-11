from fastapi import FastAPI

from src.exceptions import AppException
from src.exception_handler import exception_handler
from src.api import auth_router, jwks_router
from src.logger import setup_logger
from src.startup_init import startup_event

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
