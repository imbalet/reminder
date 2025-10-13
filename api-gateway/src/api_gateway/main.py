import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_gateway.api import (
    auth_router,
    delivery_methods_router,
    notification_router,
    reminder_router,
)
from api_gateway.config import config
from api_gateway.logger import setup_logger

setup_logger()

logger = logging.getLogger(__name__)

app = FastAPI(
    swagger_ui_parameters={
        "tryItOutEnabled": True,
        "withCredentials": True,
    },
)

origins = [str(i) for i in config.ALLOWED_ORIGINS]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.info("set allowed origins %s", origins)

app.include_router(auth_router)
app.include_router(reminder_router)
app.include_router(delivery_methods_router)
app.include_router(notification_router)
