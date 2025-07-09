import logging

from src.schemas import User, DeliveryMethodConfirm
from src.services import UserService, DeliveryMethodsService

logger = logging.getLogger(__name__)


async def add_user_callback(data: str, session_factory):
    user = User.model_validate_json(data)
    service = UserService(session_factory)
    await service.add(user_id=user.id, name=user.name, email=user.email)


async def confirm_method_callback(data: str, session_factory):
    method = DeliveryMethodConfirm.model_validate_json(data)
    service = DeliveryMethodsService(session_factory)
    await service.set_confirm(method_id=method.id)
