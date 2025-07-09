from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship

from src.schemas import DeliveryMethodEnum as DeliveryMethod


class Base(DeclarativeBase):
    pass


class UserOrm(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]

    delivery_methods: Mapped[list["DeliveryMethodsOrm"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __init__(self, id: UUID, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email


class DeliveryMethodsOrm(Base):
    __tablename__ = "delivery_methods"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(UserOrm.id, ondelete="CASCADE"), index=True
    )
    delivery_method: Mapped[DeliveryMethod]
    contact_value: Mapped[str]
    is_confirmed: Mapped[bool] = mapped_column(server_default="FALSE")

    user: Mapped["UserOrm"] = relationship(back_populates="delivery_methods")

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
