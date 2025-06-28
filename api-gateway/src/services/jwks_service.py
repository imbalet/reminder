import httpx
from fastapi import HTTPException


class JWKService:
    def __init__(self, base_url: str):
        self.client = httpx.AsyncClient(base_url=base_url, timeout=10.0)

    async def get_data(self):
        try:
            response = await self.client.get("/.well-known/jwks.json")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"External API error: {e.response.text}",
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503, detail=f"Service unavailable: {str(e)}"
            )

    async def close(self):
        await self.client.aclose()


import asyncio


async def main():
    service = JWKService("http://127.0.0.1:8000")
    res = await service.get_data()
    pass


if __name__ == "__main__":
    asyncio.run(main())
