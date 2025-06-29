import functools
from typing import Callable, Any, Annotated

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


def error_handeler(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=e.response.json(),
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503, detail=f"Service unavailable: {str(e)}"
            )

    return wrapper


@router.post("/register")
@error_handeler
async def register(
    reg_data: UserRegisterRequset,
) -> UserResponse:
    async with httpx.AsyncClient(base_url=config.AUTH_URL, timeout=10.0) as client:
        response = await client.post("/api/auth/register", json=reg_data.model_dump())
        response.raise_for_status()
        return response.json()


@router.post("/login")
@error_handeler
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenResponse:
    payload = {
        "username": form_data.username,
        "password": form_data.password,
        "grant_type": form_data.grant_type or "password",
    }
    if form_data.scopes:
        payload["scope"] = " ".join(form_data.scopes)
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


@router.post("/refresh")
@error_handeler
async def refresh_token(
    response: Response,
    token: Annotated[str, Depends(get_refresh_token_from_cookies)],
):
    async with httpx.AsyncClient(base_url=config.AUTH_URL, timeout=10.0) as client:
        cookies = {"refresh_token": token}
        res = await client.post("/api/auth/refresh", cookies=cookies)
        res.raise_for_status()
        for cookie_header in res.headers.get_list("Set-Cookie"):
            response.headers.append("Set-Cookie", cookie_header)
        return res.json()


@router.post("/logout")
@error_handeler
async def logout(
    response: Response,
    token: Annotated[str, Depends(get_refresh_token_from_cookies)],
):
    async with httpx.AsyncClient(base_url=config.AUTH_URL, timeout=10.0) as client:
        cookies = {"refresh_token": token}
        res = await client.post("/api/auth/logout", cookies=cookies)
        res.raise_for_status()
        for cookie_header in res.headers.get_list("Set-Cookie"):
            response.headers.append("Set-Cookie", cookie_header)
        return res.json()
