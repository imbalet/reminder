from typing import Annotated

from fastapi import Depends, HTTPException, status, APIRouter, Request, Response
from fastapi.security import OAuth2PasswordRequestForm

from src.services.token_service import RefreshTokenService
from src.services.user_service import UserService
from src.use_cases.user import AuthUseCase, RegisterUserUseCase
from src.use_cases.token import CreateTokenPairUseCase, RefreshTokenPairUseCase
from src.schemas.token import TokenResponse, AccesTokenData
from src.schemas.user import UserRegisterRequset, UserResponse, UserAuth

from src.config import config
from src.dependencies import get_access_token_data

router = APIRouter(prefix="/api/test", tags=["test"])


@router.post("/")
async def create(
    user_data: Annotated[AccesTokenData, Depends(get_access_token_data)],
):
    return "ok"
