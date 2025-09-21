from uuid import UUID

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from user_service.models import NotificationOrm
from user_service.schemas import NotificationResponse


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

    async def get_all(
        self, user_id: UUID, page: int, page_size: int
    ) -> Page[NotificationResponse]:
        async with self.session_factory() as session:
            stmt = (
                select(NotificationOrm)
                .filter_by(user_id=user_id)
                .order_by(NotificationOrm.created_at.desc())
            )
            pages: Page = await apaginate(
                session, stmt, Params(page=page, size=page_size)
            )

            pages.items = [
                NotificationResponse.model_validate(method, from_attributes=True)
                for method in pages.items
            ]
            return pages
