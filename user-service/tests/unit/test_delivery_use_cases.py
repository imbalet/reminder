import pytest

from user_service.use_cases import AddDeliveryUseCase, BadRequestException


@pytest.mark.asyncio
async def test_valid_add_tg(
    mock_delivery_service,
    mock_confirm_service,
    mock_produce_service,
    sample_delivery_method_tg_add,
    sample_user_data,
):
    uc = AddDeliveryUseCase(
        delivery_service=mock_delivery_service,
        confirm_service=mock_confirm_service,
        produce_service=mock_produce_service,
    )
    res = await uc.execute(
        user_id=sample_user_data.id, delivery_method=sample_delivery_method_tg_add
    )

    assert res.user_id == sample_user_data.id
    mock_confirm_service.confirm.assert_awaited_once()
    mock_delivery_service.add.assert_awaited_once()


@pytest.mark.asyncio
async def test_invalid_code_add_tg(
    mock_delivery_service,
    mock_confirm_service,
    mock_produce_service,
    sample_delivery_method_tg_add,
    sample_user_data,
):
    mock_confirm_service.confirm.return_value = None

    uc = AddDeliveryUseCase(
        delivery_service=mock_delivery_service,
        confirm_service=mock_confirm_service,
        produce_service=mock_produce_service,
    )
    with pytest.raises(BadRequestException):
        await uc.execute(
            user_id=sample_user_data.id, delivery_method=sample_delivery_method_tg_add
        )

    mock_confirm_service.confirm.assert_awaited_once()
