from typing import Annotated

import httpx
import jwt
from fastapi import HTTPException, Depends, status, Request
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from api_gateway.schemas import AccesTokenData, RefreshTokenData
from api_gateway.security import oauth2_scheme, decode_jwt
from api_gateway.config import config


async def get_jwks_pyjwt(token: Annotated[str, Depends(oauth2_scheme)]):
    jwks_client = jwt.PyJWKClient(
        config.JWKS_URL,
        cache_keys=True,
        max_cached_keys=5,
        cache_jwk_set=True,
        lifespan=3600,
    )
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    pem_key = signing_key.key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    public_key = serialization.load_pem_public_key(pem_key)

    if not isinstance(public_key, rsa.RSAPublicKey):
        raise TypeError("Полученный ключ не является RSA ключом")
    return public_key


def get_access_token_data(
    token: Annotated[str, Depends(oauth2_scheme)],
    public_key: Annotated[rsa.RSAPublicKey, Depends(get_jwks_pyjwt)],
) -> AccesTokenData:
    try:
        payload = decode_jwt(token, public_key)
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


def get_refresh_token_from_cookies(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token"
        )
    return refresh_token


def get_refresh_token_data(
    token: Annotated[str, Depends(get_refresh_token_from_cookies)],
    public_key: Annotated[rsa.RSAPublicKey, Depends(get_jwks_pyjwt)],
) -> RefreshTokenData:
    try:
        payload = decode_jwt(token, public_key)
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


async def get_jwks():
    try:
        async with httpx.AsyncClient(
            base_url="http://127.0.0.1:8000", timeout=10.0
        ) as client:
            response = await client.get("/.well-known/jwks.json")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"External API error: {e.response.text}",
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
