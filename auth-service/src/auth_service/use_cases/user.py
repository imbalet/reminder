from auth_service.services import UserService
from auth_service.schemas.user import (
    UserRegisterRequset,
    UserAuth,
    UserResponse,
    UserRmqData,
)
from auth_service.security import get_hash, verify_password

from rmq_service import ProduceService, Message


class RegisterUserUseCase:
    def __init__(
        self, user_service: UserService, event_service: ProduceService
    ) -> None:
        self.user_service = user_service
        self.event_service = event_service

    async def execute(self, data: UserRegisterRequset) -> UserResponse:
        """Register a new user

        Args:
            data (UserRegisterRequset): User's data

        Returns:
            UserResponse: Registered user object
        """
        hashed_password = get_hash(data.password)
        res = await self.user_service.create_user(
            email=data.email, hashed_password=hashed_password
        )
        await self.event_service.produce(
            Message.from_json(
                UserRmqData(id=res.id, email=res.email, name=data.name).model_dump(
                    mode="json"
                )
            )
        )
        return res


class AuthUseCase:
    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    async def execute(self, data: UserAuth) -> UserResponse | None:
        """Authenticates a user using email and password.

        Args:
            data (AuthUserRequest): User's credentials

        Returns:
            UserResponse | None: Authenticated user object if successful, None otherwise
        """
        user = await self.user_service.get_user_by_email(data.email)
        if not user:
            return None
        if not verify_password(data.password, user.hashed_password):
            return None

        return UserResponse.model_validate(user, from_attributes=True)
