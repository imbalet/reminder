from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_gateway.api import (
    auth_router,
    delivery_methods_router,
    notification_router,
    reminder_router,
)
from api_gateway.logger import setup_logger

setup_logger()

app = FastAPI(
    swagger_ui_parameters={
        "tryItOutEnabled": True,
        "withCredentials": True,
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(reminder_router)
app.include_router(delivery_methods_router)
app.include_router(notification_router)
