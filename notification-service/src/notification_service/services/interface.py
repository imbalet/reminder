from abc import ABC, abstractmethod

from notification_service.schemas import Message, Result


class SenderInterface(ABC):
    @abstractmethod
    async def send(self, contact_value: str, message: Message) -> Result: ...
