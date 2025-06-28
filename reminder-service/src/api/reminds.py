from uuid import UUID
from fastapi import APIRouter, Header

router = APIRouter(prefix="/api/reminds", tags=["reminds"])


@router.post("/")
async def create(app_user_id: UUID = Header()):
    return app_user_id
