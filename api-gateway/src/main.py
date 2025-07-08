import logging

from fastapi import FastAPI

from src.api import auth_router, reminder_router, delivery_methods_router
from src.config import config

logger = logging.getLogger(__name__)
logger.setLevel(config.LOG_LEVEL.value)

console_handler = logging.StreamHandler()
console_handler.setLevel(config.LOG_LEVEL.value)
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(config.LOG_LEVEL.value)


formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


logging.getLogger("uvicorn").handlers = logger.handlers
logging.getLogger("uvicorn.access").handlers = logger.handlers
logging.getLogger("fastapi").handlers = logger.handlers

app = FastAPI(
    swagger_ui_parameters={
        "tryItOutEnabled": True,
        "withCredentials": True,
    },
)
app.include_router(auth_router)
app.include_router(reminder_router)
app.include_router(delivery_methods_router)
