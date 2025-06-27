from datetime import datetime
from typing import cast
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.exc import IntegrityError

from src.schemas import RefreshTokenData
from src.models import RefreshTokensOrm
from src.exceptions import NotFoundError, AlreadyExistsError, Entity


class RefreshTokenService:

    def __init__(self, session_factory: async_sessionmaker) -> None:
        self.session_factory: async_sessionmaker = session_factory

    async def save(
        self, jti: UUID, token_hash: str, expiration_time: datetime, user_id: UUID
    ) -> RefreshTokenData:
        try:
            async with self.session_factory() as session:
                session = cast(AsyncSession, session)
                new_token = RefreshTokensOrm(
                    jti=jti,
                    user_id=user_id,
                    token_hash=token_hash,
                    expires_at=expiration_time,
                )
                session.add(new_token)
                await session.commit()
                await session.refresh(new_token)
                return RefreshTokenData.model_validate(new_token, from_attributes=True)
        except IntegrityError as e:
            orig_message = str(e.orig).lower()
            if "duplicate" in orig_message:
                raise AlreadyExistsError(
                    Entity.TOKEN, message=f"Token with jti {jti} already exists"
                )
            raise NotFoundError(
                entity=Entity.USER, message=f"User with id {user_id} not exists"
            ) from e

    async def find_by_jti(self, jti: UUID) -> RefreshTokenData | None:
        async with self.session_factory() as session:
            session = cast(AsyncSession, session)
            res = await session.get(RefreshTokensOrm, jti)
            if res is None:
                return None
            return RefreshTokenData.model_validate(res, from_attributes=True)

    async def revoke_token(self, jti: UUID) -> None:
        async with self.session_factory() as session:
            session = cast(AsyncSession, session)
            query = delete(RefreshTokensOrm).filter_by(jti=jti)
            await session.execute(query)
            await session.commit()

    async def revoke_for_user(self, user_id: UUID) -> None:
        async with self.session_factory() as session:
            session = cast(AsyncSession, session)
            query = delete(RefreshTokensOrm).filter_by(user_id=user_id)
            await session.execute(query)
            await session.commit()
