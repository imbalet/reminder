from fastapi import FastAPI
from src.api.auth import router

app = FastAPI(
    swagger_ui_parameters={
        "tryItOutEnabled": True,
        "withCredentials": True,
    },
)
app.include_router(router)
