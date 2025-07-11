from typing import Annotated

from fastapi import Depends, HTTPException, Request, status, APIRouter, Response

from src.services import RefreshTokenService, UserService, EventService
from src.use_cases import (
    AuthUseCase,
    CreateTokenPairUseCase,
    RegisterUserUseCase,
    RefreshTokenPairUseCase,
)
from src.schemas import (
    TokenResponse,
    UserRegisterRequset,
    UserResponse,
    UserAuth,
    RefreshTokenData,
    KeyPair,
)
from src.config import config
from src.dependencies import (
    get_user_service,
    get_token_service,
    get_refresh_token_data,
    get_last_key_pair,
    get_auth_data,
    get_event_service,
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
        path="/api/auth",
    )


@router.post("/register")
async def register(
    request: Request,
    reg_data: UserRegisterRequset,
    user_service: Annotated[UserService, Depends(get_user_service)],
    event_service: Annotated[EventService, Depends(get_event_service)],
) -> UserResponse:
    if "refresh_token" in request.cookies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are already authenticated",
        )
    register_uc = RegisterUserUseCase(user_service, event_service)
    res = await register_uc.execute(reg_data)
    return res


@router.post("/login")
async def login(
    response: Response,
    auth_data: Annotated[UserAuth, Depends(get_auth_data)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    token_service: Annotated[RefreshTokenService, Depends(get_token_service)],
    key_pair: Annotated[KeyPair, Depends(get_last_key_pair)],
) -> TokenResponse:
    auth_uc = AuthUseCase(user_service)
    token_uc = CreateTokenPairUseCase(token_service, user_service)
    user = await auth_uc.execute(auth_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_pair = await token_uc.execute(user_id=user.id, key_pair=key_pair)
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
    refresh_token_data: Annotated[RefreshTokenData, Depends(get_refresh_token_data)],
    key_pair: Annotated[KeyPair, Depends(get_last_key_pair)],
):
    token_uc = RefreshTokenPairUseCase(
        token_service=token_service, user_service=user_service
    )

    token_pair = await token_uc.execute(
        token_data=refresh_token_data, key_pair=key_pair
    )
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
    token_service: Annotated[RefreshTokenService, Depends(get_token_service)],
    refresh_token_data: Annotated[RefreshTokenData, Depends(get_refresh_token_data)],
):
    if refresh_token_data:
        await token_service.revoke_token(refresh_token_data.jti)

    response.delete_cookie(key="refresh_token", path="/api/auth")

    return {"message": "Successfully logged out"}
