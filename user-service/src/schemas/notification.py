from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Notification(BaseModel):
    user_id: UUID
    title: str
    content: str


class NotificationResponse(Notification):
    id: UUID
    created_at: datetime
    is_read: bool
