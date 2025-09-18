from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from user_service.exceptions import AlreadyExistsError
from user_service.models import DeliveryMethodsOrm
from user_service.schemas import DeliveryMethodEnum, DeliveryMethodResponse, MetaData


class DeliveryMethodsService:

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def add(
        self,
        user_id: UUID,
        method: DeliveryMethodEnum,
        contact_value: str,
        meta_data: MetaData | None = None,
        is_confirmed: bool = False,
    ) -> DeliveryMethodResponse:
        try:
            async with self.session_factory() as session:
                new_method = DeliveryMethodsOrm(
                    user_id=user_id,
                    delivery_method=method,
                    contact_value=contact_value,
                    is_confirmed=is_confirmed,
                    meta_data=meta_data,
                )
                session.add(new_method)
                await session.commit()
                await session.refresh(new_method)
                return DeliveryMethodResponse.model_validate(
                    new_method, from_attributes=True
                )
        except IntegrityError as e:
            raise AlreadyExistsError("Delivery method already exists") from e

    async def delete(
        self, user_id: UUID, method_id: UUID
    ) -> DeliveryMethodResponse | None:
        async with self.session_factory() as session:
            query = (
                delete(DeliveryMethodsOrm)
                .filter_by(id=method_id, user_id=user_id)
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

    async def get_all(
        self, user_id: UUID, only_confirmed: bool = False
    ) -> list[DeliveryMethodResponse]:
        async with self.session_factory() as session:
            if only_confirmed:
                stmt = select(DeliveryMethodsOrm).filter_by(
                    user_id=user_id, is_confirmed=True
                )
            else:
                stmt = select(DeliveryMethodsOrm).filter_by(user_id=user_id)
            res = await session.execute(stmt)
            result = res.scalars().all()
            return [
                DeliveryMethodResponse.model_validate(method, from_attributes=True)
                for method in result
            ]

    async def set_confirm(self, method_id: UUID) -> DeliveryMethodResponse | None:
        async with self.session_factory() as session:
            method = await session.get(DeliveryMethodsOrm, method_id)
            if not method:
                return None
            method.is_confirmed = True
            await session.commit()
            await session.refresh(method)
            return DeliveryMethodResponse.model_validate(method, from_attributes=True)
