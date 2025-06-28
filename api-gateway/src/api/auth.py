from typing import Annotated

from fastapi import Depends, HTTPException, APIRouter, Response
from fastapi.security import OAuth2PasswordRequestForm
import httpx

from src.schemas import (
    TokenResponse,
    UserRegisterRequset,
    UserResponse,
)
from src.config import config
from src.dependencies import get_refresh_token_from_cookies


router = APIRouter(prefix="/api/auth", tags=["auth"])


def set_token_to_cookie(response: Response, new_refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        # max_age=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/api/auth/refresh",
    )


@router.post("/register")
async def register(
    reg_data: UserRegisterRequset,
) -> UserResponse:
    try:
        async with httpx.AsyncClient(base_url=config.AUTH_URL, timeout=10.0) as client:
            response = await client.post(
                "/api/auth/register", json=reg_data.model_dump()
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"External API error: {e.response.text}",
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


@router.post("/login")
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenResponse:
    try:
        payload = {
            "username": form_data.username,
            "password": form_data.password,
            "grant_type": form_data.grant_type or "password",
        }
        if form_data.scopes:
            payload["scope"] = form_data.scopes
        if form_data.client_id:
            payload["client_id"] = form_data.client_id
        if form_data.client_secret:
            payload["client_secret"] = form_data.client_secret
        async with httpx.AsyncClient(base_url=config.AUTH_URL, timeout=10.0) as client:
            res = await client.post("/api/auth/login", data=payload)
            res.raise_for_status()
            for cookie_header in res.headers.get_list("Set-Cookie"):
                response.headers.append("Set-Cookie", cookie_header)
            return res.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"External API error: {e.response.text}",
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


@router.post("/refresh")
async def refresh_token(
    response: Response,
    token: Annotated[str, Depends(get_refresh_token_from_cookies)],
):
    try:
        async with httpx.AsyncClient(base_url=config.AUTH_URL, timeout=10.0) as client:
            cookies = {"refresh_token": token}
            res = await client.post("/api/auth/refresh", cookies=cookies)
            res.raise_for_status()
            for cookie_header in res.headers.get_list("Set-Cookie"):
                response.headers.append("Set-Cookie", cookie_header)
            return res.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"External API error: {e.response.text}",
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


@router.post("/logout")
async def logout(
    response: Response,
    token: Annotated[str, Depends(get_refresh_token_from_cookies)],
):
    try:
        async with httpx.AsyncClient(base_url=config.AUTH_URL, timeout=10.0) as client:
            cookies = {"refresh_token": token}
            res = await client.post("/api/auth/logout", cookies=cookies)
            res.raise_for_status()
            for cookie_header in res.headers.get_list("Set-Cookie"):
                response.headers.append("Set-Cookie", cookie_header)
            return res.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"External API error: {e.response.text}",
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
