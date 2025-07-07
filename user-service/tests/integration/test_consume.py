import pytest
from pytest_mock import MockerFixture

from src.schemas import User
from src.event_handler import consume


@pytest.mark.asyncio
async def test_recieving(
    sample_user_data: User,
    mocker: MockerFixture,
):
    aio_pika_mock = mocker.patch("src.event_handler.aio_pika", mocker.MagicMock())
    conn_mock = mocker.AsyncMock()
    channel_mock = mocker.AsyncMock()
    queue_mock = mocker.MagicMock()
    message_mock = mocker.MagicMock()
    test_data = sample_user_data.model_dump_json()
    message_mock.body.decode.return_value = test_data

    context_manager = mocker.MagicMock()

    async def async_iter():
        yield message_mock

    context_manager.__aenter__.return_value = async_iter()
    context_manager.__aexit__.return_value = None

    queue_mock.iterator.return_value = context_manager

    channel_mock.declare_queue.return_value = queue_mock
    conn_mock.channel.return_value = channel_mock
    aio_pika_mock.connect_robust = mocker.AsyncMock(return_value=conn_mock)

    mock_user_service = mocker.AsyncMock()
    mock_session_factory = mocker.MagicMock()

    mock_service = mocker.patch(
        "src.event_handler.UserService", return_value=mock_user_service
    )
    await consume(
        url="amqp://test",
        queue_name="test_queue",
        session_factory=mock_session_factory,
    )

    conn_mock.channel.assert_called_once()
    channel_mock.set_qos.assert_called_once_with(prefetch_count=10)
    channel_mock.declare_queue.assert_called_once_with("test_queue", durable=False)

    message_mock.body.decode.assert_called_once_with()
    message_mock.process.assert_called_once()

    mock_service.assert_called_once_with(mock_session_factory)
    mock_user_service.add.assert_awaited_once_with(
        user_id=sample_user_data.id,
        name=sample_user_data.name,
        email=sample_user_data.email,
    )
