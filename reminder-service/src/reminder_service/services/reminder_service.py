from datetime import datetime, timezone
from uuid import UUID

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from reminder_service.models import DeliveryMethodOrm, RemindersOrm, Status
from reminder_service.schemas import (
    ReminderEdit,
    ReminderResponse,
)


class ReminderService:

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def create_reminder(
        self,
        title: str,
        content: str,
        user_id: UUID,
        remind_date: datetime,
        delivery_method_ids: list[UUID],
    ) -> ReminderResponse:
        async with self.session_factory() as session:
            result = await session.execute(
                select(DeliveryMethodOrm).where(
                    DeliveryMethodOrm.id.in_(delivery_method_ids)
                )
            )
            delivery_methods = result.scalars().all()

            reminder = RemindersOrm(
                title=title,
                content=content,
                user_id=user_id,
                remind_date=remind_date,
                delivery_methods=delivery_methods,  # type: ignore
            )

            session.add(reminder)
            await session.commit()
            await session.refresh(reminder)
            return ReminderResponse.model_validate(reminder, from_attributes=True)

    async def get_reminder(self, reminder_id: UUID) -> ReminderResponse | None:
        async with self.session_factory() as session:
            result = await session.get(RemindersOrm, reminder_id)
            if result is None:
                return None
            return ReminderResponse.model_validate(result, from_attributes=True)

    async def get_reminders_by_user_id(
        self, user_id: UUID, page: int, page_size: int
    ) -> Page[ReminderResponse]:
        async with self.session_factory() as session:
            stmt = (
                select(RemindersOrm)
                .filter_by(user_id=user_id)
                .order_by(RemindersOrm.created_at.desc())
            )
            pages: Page = await apaginate(
                session, stmt, Params(page=page, size=page_size)
            )

            pages.items = [
                ReminderResponse.model_validate(method, from_attributes=True)
                for method in pages.items
            ]
            return pages

    async def delete_reminder(
        self, reminder_id: UUID, user_id: UUID
    ) -> ReminderResponse | None:
        async with self.session_factory() as session:
            stmt = (
                delete(RemindersOrm)
                .filter_by(id=reminder_id, user_id=user_id)
                .returning(RemindersOrm)
            )
            res = await session.execute(stmt)
            result = res.scalar()
            if not result:
                return None
            await session.commit()
            return ReminderResponse.model_validate(result, from_attributes=True)

    async def edit_reminder(
        self,
        reminder_id: UUID,
        data: ReminderEdit,
        user_id: UUID,
    ) -> ReminderResponse | None:
        async with self.session_factory() as session:
            reminder = await session.get(RemindersOrm, reminder_id)
            if not reminder or reminder.user_id != user_id:
                return None
            update_data = data.model_dump(
                exclude_unset=True, exclude={"delivery_methods"}
            )
            for field, value in update_data.items():
                setattr(reminder, field, value)

            if data.delivery_methods_ids:
                delivery_method_ids = update_data["delivery_methods"]
                if delivery_method_ids is not None:
                    result = await session.execute(
                        select(DeliveryMethodOrm).where(
                            DeliveryMethodOrm.id.in_(delivery_method_ids)
                        )
                    )
                    reminder.delivery_methods = list(result.scalars().all())
            reminder.edited_at = datetime.now(timezone.utc)

            await session.commit()
            await session.refresh(reminder)
            return ReminderResponse.model_validate(reminder, from_attributes=True)

    async def get_upcoming_reminders(self) -> list[ReminderResponse]:
        async with self.session_factory() as session:
            stmt = (
                update(RemindersOrm)
                .filter(
                    RemindersOrm.status == Status.PENDING,
                    RemindersOrm.remind_date <= datetime.now(timezone.utc),
                )
                .values(status=Status.SENT)
                .returning(RemindersOrm)
            )
            result = await session.execute(stmt)
            res = result.scalars().all()
            await session.commit()
            return [
                ReminderResponse.model_validate(rem, from_attributes=True)
                for rem in res
            ]

    async def set_status(
        self, reminder_id: UUID, status: Status
    ) -> ReminderResponse | None:
        async with self.session_factory() as session:
            stmt = (
                update(RemindersOrm)
                .filter_by(id=reminder_id)
                .values(status=status)
                .returning(RemindersOrm)
            )
            result = await session.execute(stmt)
            res = result.scalar()
            await session.commit()
            if res is None:
                return None
            return ReminderResponse.model_validate(res, from_attributes=True)
