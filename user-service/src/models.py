from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, DateTime, UniqueConstraint, text
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

from src.schemas import DeliveryMethodEnum as DeliveryMethod


class Base(DeclarativeBase):
    pass


class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("TIMEZONE('utc', now())")
    )

    def __init__(
        self,
        name: str,
        email: str,
        hashed_password: str,
    ):
        self.name = name
        self.email = email
        self.hashed_password = hashed_password


class RefreshTokensOrm(Base):
    __tablename__ = "refresh_tokens"
    jti: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("TIMEZONE('utc', now())")
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    def __init__(
        self,
        jti: UUID,
        user_id: UUID,
        token_hash: str,
        expires_at: datetime,
    ):
        self.jti = jti
        self.user_id = user_id
        self.token_hash = token_hash
        self.expires_at = expires_at


class DeliveryMethodsOrm(Base):
    __tablename__ = "delivery_methods"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
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
