import pytest

from user_service.event_handler import add_user_callback
from user_service.schemas import User


@pytest.mark.asyncio
async def test_user_callback(sample_user_data: User, mock_user_service):
    await add_user_callback(
        mock_user_service, sample_user_data.model_dump_json().encode()
    )
    mock_user_service.create.assert_awaited_once()
