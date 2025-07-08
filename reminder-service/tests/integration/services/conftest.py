from uuid import uuid4

import pytest
from src.schemas import (
    DeliveryMethod,
    DeliveryMethodEnum,
)


@pytest.fixture
async def sample_methods() -> list[DeliveryMethod]:
    return [
        DeliveryMethod(
            delivery_method=DeliveryMethodEnum.TELEGRAM,
            contact_value="telegram",
            id=uuid4(),
        )
    ]
