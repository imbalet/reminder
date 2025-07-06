from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.exc import IntegrityError

from src.schemas import DeliveryMethodEnum, DeliveryMethodResponse, DeliveryMethodEdit
from src.models import DeliveryMethodsOrm
from src.exceptions import AlreadyExistsError, Entity


class DeliveryMethodsService:

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def add(
        self, user_id: UUID, method: DeliveryMethodEnum, contact_value: str
    ) -> DeliveryMethodResponse:
        try:
            async with self.session_factory() as session:
                new_method = DeliveryMethodsOrm(
                    user_id=user_id, delivery_method=method, contact_value=contact_value
                )
                session.add(new_method)
                await session.commit()
                await session.refresh(new_method)
                return DeliveryMethodResponse.model_validate(
                    new_method, from_attributes=True
                )
        except IntegrityError as e:
            raise AlreadyExistsError(
                Entity.DELIVERY_METHOD, "Delivery method already exists"
            ) from e

    async def remove(self, user_id: UUID, id: UUID) -> DeliveryMethodResponse | None:
        async with self.session_factory() as session:
            query = (
                delete(DeliveryMethodsOrm)
                .filter_by(id=id, user_id=user_id)
                .returning(DeliveryMethodsOrm)
            )
            res = await session.execute(query)
            await session.commit()
            result = res.scalar()
            if not result:
                return None
            return DeliveryMethodResponse.model_validate(result, from_attributes=True)

    async def get(self, method_id: UUID) -> DeliveryMethodResponse | None:
        async with self.session_factory() as session:
            result = await session.get(DeliveryMethodsOrm, method_id)
            if not result:
                return None
            return DeliveryMethodResponse.model_validate(result, from_attributes=True)

    async def get_all(self, user_id: UUID) -> list[DeliveryMethodResponse]:
        async with self.session_factory() as session:
            stmt = select(DeliveryMethodsOrm).filter_by(user_id=user_id)
            res = await session.execute(stmt)
            result = res.scalars().all()
            return [
                DeliveryMethodResponse.model_validate(method, from_attributes=True)
                for method in result
            ]

    async def edit(
        self, method_id: UUID, user_id: UUID, data: DeliveryMethodEdit
    ) -> DeliveryMethodResponse | None:
        async with self.session_factory() as session:
            method = await session.get(DeliveryMethodsOrm, method_id)
            if not method or method.user_id != user_id:
                return None

            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(method, field, value)

            await session.commit()
            await session.refresh(method)
            return DeliveryMethodResponse.model_validate(method, from_attributes=True)
