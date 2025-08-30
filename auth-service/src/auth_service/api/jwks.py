from typing import Annotated

from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from auth_service.dependencies import get_security_service
from auth_service.services import SecurityService


router = APIRouter(tags=["jwks"])


@router.get("/.well-known/jwks.json", response_class=JSONResponse)
async def get_jwks(
    security_servise: Annotated[SecurityService, Depends(get_security_service)],
) -> dict:
    return security_servise.get_jwks()
