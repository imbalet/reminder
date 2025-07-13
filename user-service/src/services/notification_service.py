from uuid import UUID

from sqlalchemy import delete, update, select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.models import NotificationOrm
from src.schemas import NotificationResponse


class NotificationService:

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def create(
        self, user_id: UUID, title: str, content: str
    ) -> NotificationResponse:
        async with self.session_factory() as session:
            new_notification = NotificationOrm(
                user_id=user_id, title=title, content=content
            )
            session.add(new_notification)
            await session.commit()
            await session.refresh(new_notification)
            return NotificationResponse.model_validate(
                new_notification, from_attributes=True
            )

    async def delete(
        self, notification_id: UUID, user_id: UUID
    ) -> NotificationResponse | None:
        async with self.session_factory() as session:
            stmt = (
                delete(NotificationOrm)
                .filter_by(id=notification_id, user_id=user_id)
                .returning(NotificationOrm)
            )
            res = await session.execute(stmt)
            result = res.scalar()
            await session.commit()
            if not result:
                return None
            return NotificationResponse.model_validate(result, from_attributes=True)

    async def read(
        self, notification_id: UUID, user_id: UUID
    ) -> NotificationResponse | None:
        async with self.session_factory() as session:
            stmt = (
                update(NotificationOrm)
                .filter_by(id=notification_id, user_id=user_id, is_read=False)
                .values(is_read=True)
                .returning(NotificationOrm)
            )
            res = await session.execute(stmt)
            result = res.scalar()
            await session.commit()
            if not result:
                return None
            return NotificationResponse.model_validate(result, from_attributes=True)

    async def get(self, notification_id: UUID) -> NotificationResponse | None:
        async with self.session_factory() as session:
            res = await session.get(NotificationOrm, notification_id)
            if not res:
                return None
            return NotificationResponse.model_validate(res, from_attributes=True)

    async def get_all(self, user_id: UUID) -> list[NotificationResponse]:
        async with self.session_factory() as session:
            stmt = select(NotificationOrm).filter_by(user_id=user_id)
            res = await session.execute(stmt)
            result = res.scalars()
            return [
                NotificationResponse.model_validate(i, from_attributes=True)
                for i in result
            ]
