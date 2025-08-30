import pytest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from user_service.schemas import User
from user_service.event_handler import add_user_callback


@pytest.mark.asyncio
async def test_user_callback(
    sample_user_data: User,
    mocker: MockerFixture,
    async_session_factory: async_sessionmaker,
):
    service_mock = mocker.patch("user_service.event_handler.UserService", autospec=True)
    await add_user_callback(sample_user_data.model_dump_json(), async_session_factory)
    service_mock.return_value.add.assert_awaited_once()
