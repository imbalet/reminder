from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.schemas import ReminderEdit, ReminderResponse, DeliveryMethod
from src.models import RemindersOrm, DeliveryMethodOrm, Status


class ReminderService:

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def create_reminder(
        self,
        title: str,
        content: str,
        user_id: UUID,
        remind_date: datetime,
        delivery_methods: list[DeliveryMethod],
    ) -> ReminderResponse:
        async with self.session_factory() as session:
            new_reminder = RemindersOrm(
                title=title,
                content=content,
                user_id=user_id,
                remind_date=remind_date,
                delivery_methods=[
                    DeliveryMethodOrm(
                        delivery_method=method.delivery_method,
                        contact_value=method.contact_value,
                    )
                    for method in delivery_methods
                ],
            )
            session.add(new_reminder)
            await session.commit()
            await session.refresh(new_reminder)
            return ReminderResponse.model_validate(new_reminder, from_attributes=True)

    async def get_reminder(self, reminder_id: UUID) -> ReminderResponse | None:
        async with self.session_factory() as session:
            result = await session.get(RemindersOrm, reminder_id)
            if result is None:
                return None
            return ReminderResponse.model_validate(result, from_attributes=True)

    async def get_reminders_by_user_id(self, user_id: UUID) -> list[ReminderResponse]:
        async with self.session_factory() as session:
            stmt = select(RemindersOrm).where(RemindersOrm.user_id == user_id)
            result = await session.execute(stmt)
            res = result.scalars().all()
            return [
                ReminderResponse.model_validate(reminder, from_attributes=True)
                for reminder in res
            ]

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
        self, reminder_id: UUID, data: ReminderEdit, user_id: UUID
    ) -> ReminderResponse | None:
        async with self.session_factory() as session:
            reminder = await session.get(RemindersOrm, reminder_id)
            if not reminder or reminder.user_id != user_id:
                return None
            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(reminder, field, value)
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
