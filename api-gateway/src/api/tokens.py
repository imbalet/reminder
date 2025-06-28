from typing import Annotated

from fastapi import Depends, HTTPException, status, APIRouter
from src.schemas import AccesTokenData
from src.dependencies import get_access_token_data

router = APIRouter(prefix="/api/tokens", tags=["tokens"])


@router.post("/")
async def create(
    user_data: Annotated[AccesTokenData, Depends(get_access_token_data)],
):
    return "ok"
