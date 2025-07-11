from fastapi import FastAPI

from src.api import auth_router, reminder_router, delivery_methods_router
from src.logger import setup_logger

setup_logger()

app = FastAPI(
    swagger_ui_parameters={
        "tryItOutEnabled": True,
        "withCredentials": True,
    },
)
app.include_router(auth_router)
app.include_router(reminder_router)
app.include_router(delivery_methods_router)
