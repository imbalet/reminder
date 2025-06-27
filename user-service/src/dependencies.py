from typing import Annotated

import jwt
from fastapi import HTTPException, Depends, status, Request
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.services import RefreshTokenService, UserService
from src.schemas import AccesTokenData, RefreshTokenData
from src.security import oauth2_scheme, decode_jwt


def get_async_session_factory(req: Request):
    return req.app.state.session_factory  # type: ignore


def get_user_service(
    session_factory: Annotated[async_sessionmaker, Depends(get_async_session_factory)],
):
    return UserService(session_factory)


def get_token_service(
    session_factory: Annotated[async_sessionmaker, Depends(get_async_session_factory)],
):
    return RefreshTokenService(session_factory)


def get_refresh_token_from_cookies(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token"
        )
    return refresh_token


def get_access_token_data(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> AccesTokenData:
    """Get data from JWT

    Args:
       token (Annotated[str, Depends(oauth2_scheme)]): JWT token

    Raises:
        HTTPException: 401 - expired or invalid token
        HTTPException: 422 - if either 'id' or 'role' is None
    Returns:
        AccesTokenData: DTO with user data fields
    """
    try:
        payload = decode_jwt(token)
        id = payload.get("sub")
        if id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token structure",
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
) -> RefreshTokenData:
    """Get data from JWT

    Args:
       token (Annotated[str, Depends(get_refresh_token_from_cookies)]): JWT token

    Raises:
        HTTPException: 401 - expired or invalid token
        HTTPException: 422 - if either 'id' or 'role' is None
    Returns:
        RefreshTokenData: DTO with user data fields
    """
    try:
        payload = decode_jwt(token)
        user_id = payload.get("sub")
        jti = payload.get("jti")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token structure",
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
