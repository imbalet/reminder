from uuid import uuid4

import pytest
from fastapi_pagination import Page, Params
from httpx import AsyncClient

from user_service.exceptions import AlreadyExistsError
from user_service.schemas import (
    DeliveryMethodEnum,
    DeliveryMethodResponse,
    TelegramDelivery,
)


@pytest.mark.asyncio
async def test_valid_create(
    async_client: AsyncClient, user_header: dict[str, str], mock_delivery_service
):
    data = TelegramDelivery(
        delivery_method=DeliveryMethodEnum.TELEGRAM, confirm_code="telegram"
    )

    response = await async_client.post(
        "/api/delivery/",
        json=data.model_dump(),
        headers=user_header,
    )
    res = DeliveryMethodResponse.model_validate(response.json())
    assert res
    assert response.status_code == 201
    mock_delivery_service.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_already_exists_create(
    async_client: AsyncClient,
    user_header: dict[str, str],
    mock_delivery_service,
):
    mock_delivery_service.create.side_effect = AlreadyExistsError("")

    data = TelegramDelivery(
        delivery_method=DeliveryMethodEnum.TELEGRAM, confirm_code="telegram"
    )

    response = await async_client.post(
        "/api/delivery/",
        json=data.model_dump(),
        headers=user_header,
    )
    assert response.status_code == 409
    mock_delivery_service.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_valid_get(
    async_client: AsyncClient,
    sample_delivery_method_tg_response: DeliveryMethodResponse,
    user_header: dict[str, str],
    mock_delivery_service,
):
    response = await async_client.get(
        f"/api/delivery/{sample_delivery_method_tg_response.id}",
        headers=user_header,
    )
    res = DeliveryMethodResponse.model_validate(response.json())
    assert response.status_code == 200
    assert res == sample_delivery_method_tg_response
    mock_delivery_service.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_forbidden_not_found_get(
    async_client: AsyncClient,
    sample_delivery_method_tg_response: DeliveryMethodResponse,
    user_header: dict[str, str],
    mock_delivery_service,
):
    mock_delivery_service.get.return_value = None

    response = await async_client.get(
        f"/api/delivery/{sample_delivery_method_tg_response.id}",
        headers=user_header,
    )
    assert response.status_code == 403
    mock_delivery_service.get.assert_awaited_once_with(
        sample_delivery_method_tg_response.id
    )


@pytest.mark.asyncio
async def test_forbidden_no_permissions_get(
    async_client: AsyncClient,
    sample_delivery_method_tg_response: DeliveryMethodResponse,
    user_header: dict[str, str],
    mock_delivery_service,
):
    mock_delivery_service.get.return_value.user_id = uuid4()

    response = await async_client.get(
        f"/api/delivery/{sample_delivery_method_tg_response.id}",
        headers=user_header,
    )
    assert response.status_code == 403
    mock_delivery_service.get.assert_awaited_once_with(
        sample_delivery_method_tg_response.id
    )


@pytest.mark.asyncio
async def test_valid_get_all(
    async_client: AsyncClient,
    sample_delivery_method_tg_response: DeliveryMethodResponse,
    user_header: dict[str, str],
    mock_delivery_service,
):
    response = await async_client.get(
        "/api/delivery/my?page=1&limit=1",
        headers=user_header,
    )
    res = [DeliveryMethodResponse.model_validate(i) for i in response.json()["items"]]
    assert response.status_code == 200
    assert res == [sample_delivery_method_tg_response]
    mock_delivery_service.get_all.assert_awaited_once()


@pytest.mark.asyncio
async def test_empty_get_all(
    async_client: AsyncClient,
    sample_delivery_method_tg_response: DeliveryMethodResponse,
    user_header: dict[str, str],
    mock_delivery_service,
):
    mock_delivery_service.get_all.side_effect = lambda *_, **__: Page.create(
        [], Params(page=1, size=1), total=0
    )

    response = await async_client.get(
        "/api/delivery/my?page=1&limit=1",
        headers=user_header,
    )
    res = [DeliveryMethodResponse.model_validate(i) for i in response.json()["items"]]
    assert response.status_code == 200
    assert res == []


@pytest.mark.asyncio
async def test_valid_delete(
    async_client: AsyncClient,
    sample_delivery_method_tg_response: DeliveryMethodResponse,
    user_header: dict[str, str],
    mock_delivery_service,
):
    response = await async_client.delete(
        f"/api/delivery/{sample_delivery_method_tg_response.id}",
        headers=user_header,
    )
    assert response.status_code == 204
    mock_delivery_service.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_forbidden_delete(
    async_client: AsyncClient,
    sample_delivery_method_tg_response: DeliveryMethodResponse,
    user_header: dict[str, str],
    mock_delivery_service,
):
    mock_delivery_service.delete.return_value = None

    response = await async_client.delete(
        f"/api/delivery/{sample_delivery_method_tg_response.id}",
        headers=user_header,
    )
    assert response.status_code == 403
    mock_delivery_service.delete.assert_awaited_once_with(
        sample_delivery_method_tg_response.user_id,
        sample_delivery_method_tg_response.id,
    )
