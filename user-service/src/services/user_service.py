from uuid import UUID

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.exc import IntegrityError

from src.schemas import UserResponse
from src.models import UserOrm
from src.exceptions import AlreadyExistsError


class UserService:

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def add(self, user_id: UUID, name: str, email: str) -> UserResponse:
        try:
            async with self.session_factory() as session:
                new_user = UserOrm(id=user_id, name=name, email=email)
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
                return UserResponse.model_validate(new_user, from_attributes=True)
        except IntegrityError as e:
            raise AlreadyExistsError("User already exists") from e

    async def get(self, user_id: UUID) -> UserResponse | None:
        async with self.session_factory() as session:
            result = await session.get(UserOrm, user_id)
            if result is None:
                return None
            return UserResponse.model_validate(result, from_attributes=True)
