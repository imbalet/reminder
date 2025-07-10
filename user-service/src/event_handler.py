import logging

from src.schemas import User
from src.services import UserService

logger = logging.getLogger(__name__)


async def add_user_callback(data: str, session_factory):
    user = User.model_validate_json(data)
    service = UserService(session_factory)
    await service.add(user_id=user.id, name=user.name, email=user.email)
