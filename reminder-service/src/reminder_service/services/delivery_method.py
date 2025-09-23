from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from reminder_service.models import DeliveryMethodOrm, RemindersOrm
from reminder_service.schemas import DeliveryMethod, DeliveryMethodEnum


class DeliveryMethodService:

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def create(
        self,
        id: UUID,
        delivery_method: DeliveryMethodEnum,
        contact_value: str,
        user_id: UUID,
    ) -> DeliveryMethod:
        async with self.session_factory() as session:
            new_reminder = DeliveryMethodOrm(
                id=id,
                delivery_method=delivery_method,
                contact_value=contact_value,
                user_id=user_id,
            )
            session.add(new_reminder)
            await session.commit()
            await session.refresh(new_reminder)
            return DeliveryMethod.model_validate(new_reminder, from_attributes=True)

    async def get(self, id: UUID) -> DeliveryMethod | None:
        async with self.session_factory() as session:
            result = await session.get(DeliveryMethodOrm, id)
            if result is None:
                return None
            return DeliveryMethod.model_validate(result, from_attributes=True)

    async def get_by_reminder_id(self, reminder_id: UUID) -> list[DeliveryMethod]:
        async with self.session_factory() as session:
            result = await session.get(RemindersOrm, reminder_id)
            if result is None:
                return []
            return [
                DeliveryMethod.model_validate(method, from_attributes=True)
                for method in result.delivery_methods
            ]

    async def delete(self, id: UUID) -> UUID | None:
        async with self.session_factory() as session:
            stmt = (
                delete(DeliveryMethodOrm)
                .filter_by(id=id)
                .returning(DeliveryMethodOrm.id)
            )
            res = await session.execute(stmt)
            result = res.scalar()
            if not result:
                return None
            await session.commit()
            return result
