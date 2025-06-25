from typing import cast
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from src.schemas.user import UserResponse, UserInDB
from src.models import UserOrm


class UserService:

    def __init__(self, session_factory: async_sessionmaker) -> None:
        self.session_factory: async_sessionmaker = session_factory

    async def create_user(
        self, name: str, email: str, hashed_password: str
    ) -> UserResponse:
        async with self.session_factory() as session:
            session = cast(AsyncSession, session)
            new_user = UserOrm(name=name, email=email, hashed_password=hashed_password)
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            return UserResponse.model_validate(new_user, from_attributes=True)

    async def get_user(self, user_id: str) -> UserInDB:
        async with self.session_factory() as session:
            session = cast(AsyncSession, session)
            result = await session.get(UserOrm, user_id)
            return UserInDB.model_validate(result, from_attributes=True)

    async def get_user_by_email(self, email: str) -> UserInDB:
        async with self.session_factory() as session:
            session = cast(AsyncSession, session)
            stmt = select(UserOrm).where(UserOrm.email == email)
            result = await session.execute(stmt)
            return UserInDB.model_validate(result.scalar(), from_attributes=True)
