from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship

from reminder_service.schemas import DeliveryMethodEnum
from reminder_service.schemas.reminders import Status


class Base(DeclarativeBase):
    pass


class RemindersOrm(Base):
    __tablename__ = "reminders"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str]
    content: Mapped[str]
    user_id: Mapped[UUID] = mapped_column(index=True)
    remind_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[Status] = mapped_column(server_default="PENDING", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', now())"),
    )
    edited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    delivery_methods: Mapped[list["DeliveryMethodOrm"]] = relationship(
        back_populates="reminder",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __init__(
        self,
        title: str,
        content: str,
        user_id: UUID,
        remind_date: datetime,
        delivery_methods: list["DeliveryMethodOrm"],
    ):
        self.title = title
        self.content = content
        self.user_id = user_id
        self.remind_date = remind_date
        self.delivery_methods = delivery_methods


class DeliveryMethodOrm(Base):
    __tablename__ = "delivery_methods"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    reminder_id: Mapped[UUID] = mapped_column(
        ForeignKey(RemindersOrm.id, ondelete="CASCADE"), index=True
    )
    delivery_method: Mapped[DeliveryMethodEnum]
    contact_value: Mapped[str]
    reminder: Mapped["RemindersOrm"] = relationship(back_populates="delivery_methods")

    __table_args__ = (
        UniqueConstraint(
            "reminder_id",
            "delivery_method",
            "contact_value",
            name="uq_user_method_contact",
        ),
    )

    def __init__(
        self,
        delivery_method: DeliveryMethodEnum,
        contact_value: str,
    ):
        self.delivery_method = delivery_method
        self.contact_value = contact_value
