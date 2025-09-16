from datetime import datetime
from uuid import uuid4

import pytest

from reminder_service.schemas import (
    DeliveryMethodEnum,
    DeliveryMethodResponse,
)


@pytest.fixture
async def sample_methods_data() -> list[DeliveryMethodResponse]:
    return [
        DeliveryMethodResponse(
            delivery_method=DeliveryMethodEnum.TELEGRAM,
            contact_value="telegram",
            id=uuid4(),
            created_at=datetime.utcnow(),
            user_id=uuid4(),
        )
    ]
