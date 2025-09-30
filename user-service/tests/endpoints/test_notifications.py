from uuid import uuid4

import pytest
from fastapi_pagination import Page, Params
from httpx import AsyncClient

from user_service.schemas import NotificationResponse


@pytest.mark.asyncio
async def test_get(
    async_client: AsyncClient,
    user_header: dict[str, str],
    mock_notification_service,
    notification_data: NotificationResponse,
):
    response = await async_client.get(
        f"/api/notification/{notification_data.id}",
        headers=user_header,
    )
    res = NotificationResponse.model_validate(response.json())
    assert response.status_code == 200
    assert res == notification_data
    mock_notification_service.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_forbidden_not_found(
    async_client: AsyncClient,
    user_header: dict[str, str],
    mock_notification_service,
    notification_data: NotificationResponse,
):
    mock_notification_service.get.return_value = None

    response = await async_client.get(
        f"/api/notification/{notification_data.id}",
        headers=user_header,
    )
    assert response.status_code == 403
    mock_notification_service.get.assert_awaited_once_with(notification_data.id)


@pytest.mark.asyncio
async def test_get_forbidden_no_permissions(
    async_client: AsyncClient,
    user_header: dict[str, str],
    mock_notification_service,
    notification_data: NotificationResponse,
):
    mock_notification_service.get.return_value.user_id = uuid4()

    response = await async_client.get(
        f"/api/notification/{notification_data.id}",
        headers=user_header,
    )
    assert response.status_code == 403
    mock_notification_service.get.assert_awaited_once_with(notification_data.id)


@pytest.mark.asyncio
async def test_get_all(
    async_client: AsyncClient,
    user_header: dict[str, str],
    mock_notification_service,
    notification_data: NotificationResponse,
):
    response = await async_client.get(
        "/api/notification/my?page=1&size=1",
        headers=user_header,
    )
    res = [NotificationResponse.model_validate(i) for i in response.json()["items"]]
    assert response.status_code == 200
    assert res == [notification_data]
    mock_notification_service.get_all.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_empty(
    async_client: AsyncClient,
    user_header: dict[str, str],
    mock_notification_service,
):
    mock_notification_service.get_all.side_effect = lambda *_, **__: Page.create(
        [], Params(page=1, size=1), total=0
    )

    response = await async_client.get(
        "/api/notification/my?page=1&size=1",
        headers=user_header,
    )
    res = [NotificationResponse.model_validate(i) for i in response.json()["items"]]
    assert response.status_code == 200
    assert res == []


@pytest.mark.asyncio
async def test_read(
    async_client: AsyncClient,
    user_header: dict[str, str],
    mock_notification_service,
    notification_data: NotificationResponse,
):
    nt = notification_data.model_copy()
    nt.is_read = True
    mock_notification_service.read.return_value = nt

    response = await async_client.patch(
        f"/api/notification/{notification_data.id}",
        headers=user_header,
    )
    res = NotificationResponse.model_validate(response.json())
    assert response.status_code == 200
    assert res.is_read is True


@pytest.mark.asyncio
async def test_read_forbidden(
    async_client: AsyncClient,
    user_header: dict[str, str],
    mock_notification_service,
    notification_data: NotificationResponse,
):
    mock_notification_service.read.return_value = None

    response = await async_client.patch(
        f"/api/notification/{notification_data.id}",
        headers=user_header,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete(
    async_client: AsyncClient,
    user_header: dict[str, str],
    mock_notification_service,
    notification_data: NotificationResponse,
):
    mock_notification_service.delete.return_value = notification_data

    response = await async_client.delete(
        f"/api/notification/{notification_data.id}",
        headers=user_header,
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_forbidden(
    async_client: AsyncClient,
    user_header: dict[str, str],
    mock_notification_service,
    notification_data: NotificationResponse,
):
    mock_notification_service.delete.return_value = None

    response = await async_client.delete(
        f"/api/notification/{notification_data.id}",
        headers=user_header,
    )
    assert response.status_code == 403
