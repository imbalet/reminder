from uuid import UUID

from pydantic import BaseModel


class DeliveryMethodConfirm(BaseModel):
    id: UUID
    user_id: UUID
    is_confirmed: bool
