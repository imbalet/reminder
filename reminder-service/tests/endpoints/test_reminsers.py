from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from fastapi_pagination import Page, Params
from httpx import AsyncClient

from reminder_service.schemas import ReminderCreate, ReminderEdit, ReminderResponse
from reminder_service.use_cases import BadRequestException, ForbiddenException


@pytest.mark.asyncio
@patch("reminder_service.api.reminders.AddReminderUseCase")
async def test_create_reminder(
    mock_uc_cls,
    async_client: AsyncClient,
    user_header: dict[str, str],
    reminder_create: ReminderCreate,
    reminder: ReminderResponse,
):
    mock_uc = AsyncMock()
    mock_uc.execute.return_value = reminder
    mock_uc_cls.return_value = mock_uc

    response = await async_client.post(
        "/api/reminders/",
        headers=user_header,
        json=reminder_create.model_dump(mode="json"),
    )
    res = ReminderResponse.model_validate(response.json())
    assert response.status_code == 201
    assert res == reminder


@pytest.mark.asyncio
@patch("reminder_service.api.reminders.AddReminderUseCase")
async def test_create_invalid_delivery_methods(
    mock_uc_cls,
    async_client: AsyncClient,
    user_header: dict[str, str],
    reminder_create: ReminderCreate,
):
    mock_uc = AsyncMock()
    mock_uc.execute.side_effect = BadRequestException("")
    mock_uc_cls.return_value = mock_uc

    response = await async_client.post(
        "/api/reminders/",
        headers=user_header,
        json=reminder_create.model_dump(mode="json"),
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_all(
    async_client: AsyncClient,
    user_header: dict[str, str],
    mock_reminder_service: AsyncMock,
    reminder: ReminderResponse,
):
    def __get_page_args_delivery_methods(page: int, page_size: int, *args, **kwargs):
        return Page.create(
            [reminder],
            Params(page=page, size=page_size),
            total=100,
        )

    mock_reminder_service.get_all.side_effect = __get_page_args_delivery_methods
    response = await async_client.get(
        "/api/reminders/my?page=1&limit=1",
        headers=user_header,
    )
    res = [ReminderResponse.model_validate(i) for i in response.json()["items"]]
    assert response.status_code == 200
    assert res == [reminder]
    mock_reminder_service.get_all.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_empty(
    async_client: AsyncClient,
    user_header: dict[str, str],
    mock_reminder_service: AsyncMock,
    reminder: ReminderResponse,
):
    def __get_page_args_delivery_methods(page: int, page_size: int, *args, **kwargs):
        return Page.create(
            [],
            Params(page=page, size=page_size),
            total=0,
        )

    mock_reminder_service.get_all.side_effect = __get_page_args_delivery_methods
    response = await async_client.get(
        "/api/reminders/my?page=1&limit=1",
        headers=user_header,
    )
    res = [ReminderResponse.model_validate(i) for i in response.json()["items"]]
    assert response.status_code == 200
    assert res == []
    mock_reminder_service.get_all.assert_awaited_once()


@pytest.mark.asyncio
@patch("reminder_service.api.reminders.GetReminderUseCase")
async def test_get(
    mock_uc_cls,
    async_client: AsyncClient,
    user_header: dict[str, str],
    reminder: ReminderResponse,
):
    mock_uc = AsyncMock()
    mock_uc.execute.return_value = reminder
    mock_uc_cls.return_value = mock_uc

    response = await async_client.get(
        f"/api/reminders/{reminder.id}", headers=user_header
    )
    res = ReminderResponse.model_validate(response.json())
    assert response.status_code == 200
    assert res == reminder


@pytest.mark.asyncio
@patch("reminder_service.api.reminders.GetReminderUseCase")
async def test_get_forbidden(
    mock_uc_cls,
    async_client: AsyncClient,
    user_header: dict[str, str],
    reminder: ReminderResponse,
):
    mock_uc = AsyncMock()
    mock_uc.execute.side_effect = ForbiddenException("")
    mock_uc_cls.return_value = mock_uc

    response = await async_client.get(
        f"/api/reminders/{reminder.id}", headers=user_header
    )
    assert response.status_code == 403


@pytest.mark.asyncio
@patch("reminder_service.api.reminders.EditReminderUseCase")
async def test_edit(
    mock_uc_cls,
    async_client: AsyncClient,
    user_header: dict[str, str],
    reminder: ReminderResponse,
):
    new_data = ReminderEdit(
        title="new_title",
        content="new content",
        remind_date=datetime.now(UTC) + timedelta(days=1),
    )

    mock_uc = AsyncMock()
    mock_uc.execute.return_value = reminder
    mock_uc_cls.return_value = mock_uc

    response = await async_client.patch(
        f"/api/reminders/{reminder.id}",
        headers=user_header,
        json=new_data.model_dump(mode="json"),
    )
    res = ReminderResponse.model_validate(response.json())
    assert response.status_code == 200
    assert res == reminder


@pytest.mark.asyncio
@patch("reminder_service.api.reminders.EditReminderUseCase")
async def test_edit_forbidden(
    mock_uc_cls,
    async_client: AsyncClient,
    user_header: dict[str, str],
    reminder: ReminderResponse,
):
    new_data = ReminderEdit(
        title="new_title",
        content="new content",
        remind_date=datetime.now(UTC) + timedelta(days=1),
    )

    mock_uc = AsyncMock()
    mock_uc.execute.side_effect = ForbiddenException("")
    mock_uc_cls.return_value = mock_uc

    response = await async_client.patch(
        f"/api/reminders/{reminder.id}",
        headers=user_header,
        json=new_data.model_dump(mode="json"),
    )
    assert response.status_code == 403


@pytest.mark.asyncio
@patch("reminder_service.api.reminders.EditReminderUseCase")
async def test_edit_bad_request(
    mock_uc_cls,
    async_client: AsyncClient,
    user_header: dict[str, str],
    reminder: ReminderResponse,
):
    new_data = ReminderEdit(
        title="new_title",
        content="new content",
        remind_date=datetime.now(UTC) + timedelta(days=1),
    )

    mock_uc = AsyncMock()
    mock_uc.execute.side_effect = BadRequestException("")
    mock_uc_cls.return_value = mock_uc

    response = await async_client.patch(
        f"/api/reminders/{reminder.id}",
        headers=user_header,
        json=new_data.model_dump(mode="json"),
    )
    assert response.status_code == 400


@pytest.mark.asyncio
@patch("reminder_service.api.reminders.DeleteReminderUseCase")
async def test_delete(
    mock_uc_cls,
    async_client: AsyncClient,
    user_header: dict[str, str],
    reminder: ReminderResponse,
):
    mock_uc = AsyncMock()
    mock_uc.execute.return_value = None
    mock_uc_cls.return_value = mock_uc

    response = await async_client.delete(
        f"/api/reminders/{reminder.id}", headers=user_header
    )
    assert response.status_code == 204


@pytest.mark.asyncio
@patch("reminder_service.api.reminders.DeleteReminderUseCase")
async def test_delete_forbidden(
    mock_uc_cls,
    async_client: AsyncClient,
    user_header: dict[str, str],
    reminder: ReminderResponse,
):
    mock_uc = AsyncMock()
    mock_uc.execute.side_effect = ForbiddenException("")
    mock_uc_cls.return_value = mock_uc

    response = await async_client.delete(
        f"/api/reminders/{reminder.id}", headers=user_header
    )
    assert response.status_code == 403
