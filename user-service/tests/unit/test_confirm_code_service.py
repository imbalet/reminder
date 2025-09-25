from unittest.mock import AsyncMock

from user_service.services import ConfirmCodesService


async def test_confirm(
    mock_redis: AsyncMock, mock_confirm_service_with_redis: ConfirmCodesService
):
    mock_redis.getdel = AsyncMock(return_value=b"123:user")
    res = await mock_confirm_service_with_redis.confirm("123")

    assert res and res[0] == "123" and res[1] == "user"


async def test_confirm_empty(
    mock_redis: AsyncMock, mock_confirm_service_with_redis: ConfirmCodesService
):
    mock_redis.getdel = AsyncMock(return_value=None)
    res = await mock_confirm_service_with_redis.confirm("123")

    assert res is None
