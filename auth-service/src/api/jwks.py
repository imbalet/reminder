from typing import Annotated

from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from src.dependencies import get_security_service
from src.services import SecurityService


router = APIRouter(tags=["jwks"])


@router.get("/.well-known/jwks.json", response_class=JSONResponse)
async def get_jwks(
    security_servise: Annotated[SecurityService, Depends(get_security_service)],
) -> dict:
    return security_servise.get_jwks()
