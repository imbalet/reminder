from typing import Annotated

from fastapi import Depends, HTTPException, status, APIRouter, Request, Response
from fastapi.security import OAuth2PasswordRequestForm

from src.services.token_service import RefreshTokenService
from src.services.user_service import UserService
from src.use_cases.user import AuthUseCase, RegisterUserUseCase
from src.use_cases.token import CreateTokenPairUseCase, RefreshTokenPairUseCase
from src.schemas.token import TokenResponse
from src.schemas.user import UserRegisterRequset, UserResponse, UserAuth

from src.config import config
from src.dependencies import (
    get_user_service,
    get_token_service,
    get_refresh_token_data,
    get_refresh_token_from_cookies,
)


router = APIRouter(prefix="/api/auth", tags=["auth"])


def set_token_to_cookie(response: Response, new_refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/api/auth/refresh",
    )


@router.post("/register")
async def register(
    reg_data: UserRegisterRequset,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    register_uc = RegisterUserUseCase(user_service)
    res = await register_uc.execute(reg_data)
    return res


@router.post("/login")
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserService, Depends(get_user_service)],
    token_service: Annotated[RefreshTokenService, Depends(get_token_service)],
) -> TokenResponse:
    auth_uc = AuthUseCase(user_service)
    token_uc = CreateTokenPairUseCase(token_service, user_service)
    user = await auth_uc.execute(
        UserAuth(email=form_data.username, password=form_data.password)
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_pair = await token_uc.execute(user_id=user.id)
    if token_pair is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    set_token_to_cookie(response, token_pair.refresh_token)
    return TokenResponse(
        access_token=token_pair.acces_token,
        token_type="bearer",
    )


@router.post("/refresh")
async def refresh_token(
    response: Response,
    user_service: Annotated[UserService, Depends(get_user_service)],
    token_service: Annotated[RefreshTokenService, Depends(get_token_service)],
    refresh_token: Annotated[str, Depends(get_refresh_token_from_cookies)],
):
    token_uc = RefreshTokenPairUseCase(
        token_service=token_service, user_service=user_service
    )
    user_data = get_refresh_token_data(refresh_token)

    token_pair = await token_uc.execute(token_data=user_data)
    if token_pair is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    set_token_to_cookie(response, token_pair.refresh_token)
    return TokenResponse(
        access_token=token_pair.acces_token,
        token_type="bearer",
    )


@router.post("/logout")
async def logout(
    response: Response,
    request: Request,
    token_service: Annotated[RefreshTokenService, Depends(get_token_service)],
):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await token_service.revoke_token(refresh_token)

    response.delete_cookie(key="refresh_token", path="/api/auth/refresh")

    return {"message": "Successfully logged out"}
