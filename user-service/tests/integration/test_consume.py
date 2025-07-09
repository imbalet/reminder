from uuid import uuid4
import pytest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from src.schemas import User, DeliveryMethodConfirm
from src.event_handler import add_user_callback, confirm_method_callback


@pytest.mark.asyncio
async def test_user_callback(
    sample_user_data: User,
    mocker: MockerFixture,
    async_session_factory: async_sessionmaker,
):
    service_mock = mocker.patch("src.event_handler.UserService", autospec=True)
    await add_user_callback(sample_user_data.model_dump_json(), async_session_factory)
    service_mock.return_value.add.assert_awaited_once()


@pytest.mark.asyncio
async def test_method_callback(
    mocker: MockerFixture,
    async_session_factory: async_sessionmaker,
):
    service_mock = mocker.patch(
        "src.event_handler.DeliveryMethodsService", autospec=True
    )
    await confirm_method_callback(
        DeliveryMethodConfirm(
            id=uuid4(), is_confirmed=True, user_id=uuid4()
        ).model_dump_json(),
        async_session_factory,
    )
    service_mock.return_value.set_confirm.assert_awaited_once()
