from uuid import uuid4

import pytest
from fastapi_pagination import Page, Params
from httpx import AsyncClient

from user_service.schemas import NotificationResponse


@pytest.mark.asyncio
async def test_valid_get(
    async_client: AsyncClient,
    sample_notification: NotificationResponse,
    user_header: dict[str, str],
    mock_notification_service,
):
    response = await async_client.get(
        f"/api/notification/{sample_notification.id}",
        headers=user_header,
    )
    res = NotificationResponse.model_validate(response.json())
    assert response.status_code == 200
    assert res == sample_notification
    mock_notification_service.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_forbidden_not_found_get(
    async_client: AsyncClient,
    sample_notification: NotificationResponse,
    user_header: dict[str, str],
    mock_notification_service,
):
    mock_notification_service.get.return_value = None

    response = await async_client.get(
        f"/api/notification/{sample_notification.id}",
        headers=user_header,
    )
    assert response.status_code == 403
    mock_notification_service.get.assert_awaited_once_with(sample_notification.id)


@pytest.mark.asyncio
async def test_forbidden_no_permissions_get(
    async_client: AsyncClient,
    sample_notification: NotificationResponse,
    user_header: dict[str, str],
    mock_notification_service,
):
    mock_notification_service.get.return_value.user_id = uuid4()

    response = await async_client.get(
        f"/api/notification/{sample_notification.id}",
        headers=user_header,
    )
    assert response.status_code == 403
    mock_notification_service.get.assert_awaited_once_with(sample_notification.id)


@pytest.mark.asyncio
async def test_valid_get_all(
    async_client: AsyncClient,
    sample_notification: NotificationResponse,
    user_header: dict[str, str],
    mock_notification_service,
):
    response = await async_client.get(
        "/api/notification/my?page=1&size=1",
        headers=user_header,
    )
    res = [NotificationResponse.model_validate(i) for i in response.json()["items"]]
    assert response.status_code == 200
    assert res == [sample_notification]
    mock_notification_service.get_all.assert_awaited_once()


@pytest.mark.asyncio
async def test_empty_get_all(
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
