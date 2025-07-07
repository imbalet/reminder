from uuid import uuid4

from httpx import AsyncClient
import pytest
from pytest_mock import MockerFixture


from src.main import app
from src.dependencies import get_delivery_methods_service
from src.exceptions import AlreadyExistsError, Entity
from src.services import DeliveryMethodsService
from src.schemas import (
    DeliveryMethodResponse,
    DeliveryMethodEdit,
    DeliveryMethod,
    DeliveryMethodEnum,
    User,
)


@pytest.fixture
def sample_delivery_method(sample_user: User):
    return DeliveryMethodResponse(
        id=uuid4(),
        user_id=sample_user.id,
        delivery_method=DeliveryMethodEnum.TELEGRAM,
        contact_value="telegram",
    )


@pytest.mark.asyncio
async def test_valid_create(
    async_client: AsyncClient,
    sample_delivery_method: DeliveryMethodResponse,
    user_header: dict[str, str],
    mocker: MockerFixture,
):
    mock_service = mocker.create_autospec(DeliveryMethodsService)
    mock_service.add.return_value = sample_delivery_method
    app.dependency_overrides[get_delivery_methods_service] = lambda: mock_service

    data = DeliveryMethod(
        delivery_method=DeliveryMethodEnum.TELEGRAM, contact_value="telegram"
    )

    response = await async_client.post(
        "/api/delivery/",
        json=data.model_dump(),
        headers=user_header,
    )
    res = DeliveryMethodResponse.model_validate(response.json())
    assert response.status_code == 201
    assert res.contact_value == data.contact_value
    mock_service.add.assert_awaited_once


@pytest.mark.asyncio
async def test_already_exists_create(
    async_client: AsyncClient,
    user_header: dict[str, str],
    mocker: MockerFixture,
):
    mock_service = mocker.create_autospec(DeliveryMethodsService)
    mock_service.add.side_effect = AlreadyExistsError(Entity.DELIVERY_METHOD, "")
    app.dependency_overrides[get_delivery_methods_service] = lambda: mock_service

    data = DeliveryMethod(
        delivery_method=DeliveryMethodEnum.TELEGRAM, contact_value="telegram"
    )

    response = await async_client.post(
        "/api/delivery/",
        json=data.model_dump(),
        headers=user_header,
    )
    assert response.status_code == 409
    mock_service.add.assert_awaited_once


@pytest.mark.asyncio
async def test_valid_get(
    async_client: AsyncClient,
    sample_delivery_method: DeliveryMethodResponse,
    user_header: dict[str, str],
    mocker: MockerFixture,
):
    mock_service = mocker.create_autospec(DeliveryMethodsService)
    mock_service.get.return_value = sample_delivery_method
    app.dependency_overrides[get_delivery_methods_service] = lambda: mock_service

    response = await async_client.get(
        f"/api/delivery/{sample_delivery_method.id}",
        headers=user_header,
    )
    res = DeliveryMethodResponse.model_validate(response.json())
    assert response.status_code == 200
    assert res == sample_delivery_method
    mock_service.get.assert_awaited_once_with(sample_delivery_method.id)


@pytest.mark.asyncio
async def test_forbidden_not_found_get(
    async_client: AsyncClient,
    sample_delivery_method: DeliveryMethodResponse,
    user_header: dict[str, str],
    mocker: MockerFixture,
):
    mock_service = mocker.create_autospec(DeliveryMethodsService)
    mock_service.get.return_value = None
    app.dependency_overrides[get_delivery_methods_service] = lambda: mock_service

    response = await async_client.get(
        f"/api/delivery/{sample_delivery_method.id}",
        headers=user_header,
    )
    assert response.status_code == 403
    mock_service.get.assert_awaited_once_with(sample_delivery_method.id)


@pytest.mark.asyncio
async def test_forbidden_no_permissions_get(
    async_client: AsyncClient,
    sample_delivery_method: DeliveryMethodResponse,
    user_header: dict[str, str],
    mocker: MockerFixture,
):
    sample_delivery_method.user_id = uuid4()
    mock_service = mocker.create_autospec(DeliveryMethodsService)
    mock_service.get.return_value = sample_delivery_method
    app.dependency_overrides[get_delivery_methods_service] = lambda: mock_service

    response = await async_client.get(
        f"/api/delivery/{sample_delivery_method.id}",
        headers=user_header,
    )
    assert response.status_code == 403
    mock_service.get.assert_awaited_once_with(sample_delivery_method.id)


@pytest.mark.asyncio
async def test_valid_get_all(
    async_client: AsyncClient,
    sample_delivery_method: DeliveryMethodResponse,
    user_header: dict[str, str],
    mocker: MockerFixture,
):
    mock_service = mocker.create_autospec(DeliveryMethodsService)
    mock_service.get_all.return_value = [sample_delivery_method]
    app.dependency_overrides[get_delivery_methods_service] = lambda: mock_service

    response = await async_client.get(
        f"/api/delivery/users/{sample_delivery_method.user_id}",
        headers=user_header,
    )
    res = [DeliveryMethodResponse.model_validate(i) for i in response.json()]
    assert response.status_code == 200
    assert res == [sample_delivery_method]
    mock_service.get_all.assert_awaited_once_with(sample_delivery_method.user_id)


@pytest.mark.asyncio
async def test_empty_get_all(
    async_client: AsyncClient,
    sample_delivery_method: DeliveryMethodResponse,
    user_header: dict[str, str],
    mocker: MockerFixture,
):
    mock_service = mocker.create_autospec(DeliveryMethodsService)
    mock_service.get_all.return_value = []
    app.dependency_overrides[get_delivery_methods_service] = lambda: mock_service

    response = await async_client.get(
        f"/api/delivery/users/{sample_delivery_method.user_id}",
        headers=user_header,
    )
    res = [DeliveryMethodResponse.model_validate(i) for i in response.json()]
    assert response.status_code == 200
    assert res == []
    mock_service.get_all.assert_awaited_once_with(sample_delivery_method.user_id)


@pytest.mark.asyncio
async def test_forbidden_get_all(
    async_client: AsyncClient,
    sample_delivery_method: DeliveryMethodResponse,
    user_header: dict[str, str],
    mocker: MockerFixture,
):
    mock_service = mocker.create_autospec(DeliveryMethodsService)
    mock_service.get_all.return_value = [sample_delivery_method]
    app.dependency_overrides[get_delivery_methods_service] = lambda: mock_service

    response = await async_client.get(
        f"/api/delivery/users/{uuid4()}",
        headers=user_header,
    )
    assert response.status_code == 403
    mock_service.get_all.assert_not_called


@pytest.mark.asyncio
async def test_valid_edit(
    async_client: AsyncClient,
    sample_delivery_method: DeliveryMethodResponse,
    user_header: dict[str, str],
    mocker: MockerFixture,
):
    edited = sample_delivery_method.model_copy()
    edited.contact_value = "edited"

    mock_service = mocker.create_autospec(DeliveryMethodsService)
    mock_service.edit.return_value = edited
    app.dependency_overrides[get_delivery_methods_service] = lambda: mock_service

    edit_request = DeliveryMethodEdit(contact_value="edited")

    response = await async_client.patch(
        f"/api/delivery/{sample_delivery_method.id}",
        json=edit_request.model_dump(),
        headers=user_header,
    )
    res = DeliveryMethodResponse.model_validate(response.json())
    assert response.status_code == 200
    assert res == edited
    mock_service.edit.assert_awaited_once_with(
        sample_delivery_method.id, sample_delivery_method.user_id, edit_request
    )


@pytest.mark.asyncio
async def test_forbidden_edit(
    async_client: AsyncClient,
    sample_delivery_method: DeliveryMethodResponse,
    user_header: dict[str, str],
    mocker: MockerFixture,
):
    mock_service = mocker.create_autospec(DeliveryMethodsService)
    mock_service.edit.return_value = None
    app.dependency_overrides[get_delivery_methods_service] = lambda: mock_service

    edit_request = DeliveryMethodEdit(contact_value="edited")

    response = await async_client.patch(
        f"/api/delivery/{sample_delivery_method.id}",
        json=edit_request.model_dump(),
        headers=user_header,
    )
    assert response.status_code == 403
    mock_service.edit.assert_awaited_once_with(
        sample_delivery_method.id, sample_delivery_method.user_id, edit_request
    )


@pytest.mark.asyncio
async def test_valid_delete(
    async_client: AsyncClient,
    sample_delivery_method: DeliveryMethodResponse,
    user_header: dict[str, str],
    mocker: MockerFixture,
):
    mock_service = mocker.create_autospec(DeliveryMethodsService)
    mock_service.remove.return_value = sample_delivery_method
    app.dependency_overrides[get_delivery_methods_service] = lambda: mock_service

    response = await async_client.delete(
        f"/api/delivery/{sample_delivery_method.id}",
        headers=user_header,
    )
    assert response.status_code == 204
    mock_service.remove.assert_awaited_once_with(
        sample_delivery_method.user_id, sample_delivery_method.id
    )


@pytest.mark.asyncio
async def test_forbidden_delete(
    async_client: AsyncClient,
    sample_delivery_method: DeliveryMethodResponse,
    user_header: dict[str, str],
    mocker: MockerFixture,
):
    mock_service = mocker.create_autospec(DeliveryMethodsService)
    mock_service.remove.return_value = None
    app.dependency_overrides[get_delivery_methods_service] = lambda: mock_service

    response = await async_client.delete(
        f"/api/delivery/{sample_delivery_method.id}",
        headers=user_header,
    )
    assert response.status_code == 403
    mock_service.remove.assert_awaited_once_with(
        sample_delivery_method.user_id, sample_delivery_method.id
    )
