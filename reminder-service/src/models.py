from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import DateTime, text
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    pass


class RemindersOrm(Base):
    __tablename__ = "reminders"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str]
    content: Mapped[str]
    user_id: Mapped[UUID]
    remind_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', now())"),
    )
    edited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=datetime.now(timezone.utc),
        nullable=True,
    )

    def __init__(
        self,
        title: str,
        content: str,
        user_id: UUID,
        remind_date: datetime,
    ):
        self.title = title
        self.content = content
        self.user_id = user_id
        self.remind_date = remind_date
