import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import DateTime, Enum, ForeignKey, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from user_service.schemas import DeliveryMethodEnum as DeliveryMethod
from user_service.schemas import MetaData


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
    delivery_method: Mapped[DeliveryMethod] = mapped_column(
        Enum(DeliveryMethod, name="deliverymethod", native_enum=True), nullable=False
    )
    contact_value: Mapped[str]
    is_confirmed: Mapped[bool] = mapped_column(server_default="FALSE")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', now())"),
    )
    meta_data: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))

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
        is_confirmed: bool,
        meta_data: dict | MetaData | None,
    ):
        self.user_id = user_id
        self.delivery_method = delivery_method
        self.contact_value = contact_value
        self.is_confirmed = is_confirmed
        self.meta_data = (
            meta_data.model_dump(exclude_none=True)
            if isinstance(meta_data, BaseModel)
            else meta_data or {}
        )


class NotificationOrm(Base):
    __tablename__ = "notification"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(UserOrm.id, ondelete="CASCADE"), index=True
    )
    title: Mapped[str]
    content: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', now())"),
    )
    is_read: Mapped[bool] = mapped_column(server_default=text("FALSE"))

    def __init__(
        self,
        user_id: UUID,
        title: str,
        content: str,
    ):
        self.user_id = user_id
        self.title = title
        self.content = content
