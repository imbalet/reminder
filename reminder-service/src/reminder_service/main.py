from fastapi import FastAPI

from reminder_service.api import router as reminders_router
from reminder_service.logger import setup_logger
from reminder_service.startup_init import startup_event
from reminder_service.exception_handler import use_case_exception_handler
from reminder_service.use_cases import UseCaseException

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
