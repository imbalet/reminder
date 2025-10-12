from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from api_gateway.config import config
from api_gateway.dependencies import get_refresh_token_from_cookies
from api_gateway.schemas import (
    ErrorResponse,
    TokenResponse,
    UserRegisterRequest,
    UserResponse,
)

from .utils import error_handler

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "description": "User was registered",
            "model": UserResponse,
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "User already exists",
        },
    },
)
@error_handler
async def register(
    reg_data: UserRegisterRequest,
) -> UserResponse:
    async with httpx.AsyncClient(base_url=config.AUTH_URL, timeout=10.0) as client:
        response = await client.post("/api/auth/register", json=reg_data.model_dump())
        response.raise_for_status()
        return response.json()


@router.options("/login")
async def login_options():
    return Response(status_code=200)


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Incorrect username or password",
        },
    },
)
@error_handler
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
@error_handler
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


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
@error_handler
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
