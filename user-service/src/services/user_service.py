from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.exc import IntegrityError

from src.schemas import UserResponse, UserInDB
from src.models import UserOrm
from src.exceptions import AlreadyExistsError, Entity


class UserService:

    def __init__(self, session_factory: async_sessionmaker) -> None:
        self.session_factory: async_sessionmaker = session_factory

    async def create_user(
        self, name: str, email: str, hashed_password: str
    ) -> UserResponse:
        try:
            async with self.session_factory() as session:
                session = cast(AsyncSession, session)
                new_user = UserOrm(
                    name=name, email=email, hashed_password=hashed_password
                )
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
                return UserResponse.model_validate(new_user, from_attributes=True)
        except IntegrityError as e:
            raise AlreadyExistsError(Entity.USER, "User already exists") from e

    async def get_user(self, user_id: UUID) -> UserInDB | None:
        async with self.session_factory() as session:
            session = cast(AsyncSession, session)
            result = await session.get(UserOrm, user_id)
            if result is None:
                return None
            return UserInDB.model_validate(result, from_attributes=True)

    async def get_user_by_email(self, email: str) -> UserInDB | None:
        async with self.session_factory() as session:
            session = cast(AsyncSession, session)
            stmt = select(UserOrm).where(UserOrm.email == email)
            result = await session.execute(stmt)
            res = result.scalar()
            if res is None:
                return None
            return UserInDB.model_validate(res, from_attributes=True)
