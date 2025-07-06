from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

from src.schemas import DeliveryMethodEnum as DeliveryMethod


class Base(DeclarativeBase):
    pass


class DeliveryMethodsOrm(Base):
    __tablename__ = "delivery_methods"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(index=True)
    delivery_method: Mapped[DeliveryMethod]
    contact_value: Mapped[str]

    __table_args__ = (
        UniqueConstraint(
            "user_id", "delivery_method", "contact_value", name="uq_user_method_contact"
        ),
    )

    def __init__(
        self,
        user_id: UUID,
        delivery_method: DeliveryMethod,
        contact_value: str,
    ):
        self.user_id = user_id
        self.delivery_method = delivery_method
        self.contact_value = contact_value
