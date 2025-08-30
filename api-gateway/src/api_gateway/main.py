from fastapi import FastAPI

from api_gateway.api import (
    auth_router,
    reminder_router,
    delivery_methods_router,
    notification_router,
)
from api_gateway.logger import setup_logger

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
app.include_router(notification_router)
