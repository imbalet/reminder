import functools
from typing import Callable, Any

from fastapi import HTTPException
import httpx


def error_handler(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                original_detail = error_data.get("detail", error_data)
                detail_value = original_detail
            except Exception:
                detail_value = e.response.text
            raise HTTPException(
                status_code=e.response.status_code,
                detail=detail_value,
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503, detail=f"Service unavailable: {str(e)}"
            )

    return wrapper
