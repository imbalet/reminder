from fastapi import FastAPI

from src.api import router as reminders_router
from src.logger import setup_logger
from src.startup_init import startup_event
from src.exception_handler import use_case_exception_handler
from src.use_cases import UseCaseException

setup_logger()


app = FastAPI(
    lifespan=startup_event,
    swagger_ui_parameters={
        "tryItOutEnabled": True,
        "withCredentials": True,
    },
)
app.include_router(reminders_router)

app.add_exception_handler(UseCaseException, use_case_exception_handler)
