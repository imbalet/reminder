from typing import Annotated

import jwt
from fastapi import HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from pydantic import ValidationError

from src.services import RefreshTokenService, UserService, SecurityService
from src.schemas import AccesTokenData, RefreshTokenData, KeyPair, UserAuth
from src.security import oauth2_scheme, decode_jwt


def get_async_session_factory(req: Request):
    return req.app.state.session_factory  # type: ignore


def get_user_service(
    session_factory: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_session_factory)
    ],
) -> UserService:
    return UserService(session_factory)


def get_token_service(
    session_factory: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_session_factory)
    ],
) -> RefreshTokenService:
    return RefreshTokenService(session_factory)


def get_security_service(req: Request) -> SecurityService:
    return req.app.state.security_service


def get_last_key_pair(
    security_servise: Annotated[SecurityService, Depends(get_security_service)],
) -> KeyPair:
    return security_servise.get_last_key_pair()


def get_refresh_token_from_cookies(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token"
        )
    return refresh_token


def get_access_token_data(
    token: Annotated[str, Depends(oauth2_scheme)],
    key_pair: Annotated[KeyPair, Depends(get_last_key_pair)],
) -> AccesTokenData:
    """Get data from JWT

    Args:
       token (Annotated[str, Depends(oauth2_scheme)]): JWT token
       key_pair (Annotated[KeyPair, Depends(get_last_key_pair)]): Key pair object, includes private and public key

    Raises:
        HTTPException: 401 - expired or invalid token
    Returns:
        AccesTokenData: DTO with user data fields
    """
    try:
        payload = decode_jwt(token, key_pair.public_key)
        id = payload.get("sub")
        if id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token structure",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = AccesTokenData(user_id=id)
        return token_data
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_refresh_token_data(
    token: Annotated[str, Depends(get_refresh_token_from_cookies)],
    key_pair: Annotated[KeyPair, Depends(get_last_key_pair)],
) -> RefreshTokenData:
    """Get data from JWT

    Args:
       token (Annotated[str, Depends(get_refresh_token_from_cookies)]): JWT token
       key_pair (Annotated[KeyPair, Depends(get_last_key_pair)]): Key pair object, includes private and public key

    Raises:
        HTTPException: 401 - expired or invalid token
    Returns:
        RefreshTokenData: DTO with user data fields
    """
    try:
        payload = decode_jwt(token, key_pair.public_key)
        user_id = payload.get("sub")
        jti = payload.get("jti")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token structure",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = RefreshTokenData(user_id=user_id, jti=jti)
        return token_data
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_auth_data(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    try:
        return UserAuth(email=form_data.username, password=form_data.password)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors()
        )
