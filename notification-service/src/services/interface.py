from abc import ABC, abstractmethod

from src.schemas import Message, Result


class SenderInterface(ABC):
    @abstractmethod
    async def send(self, contact_value: str, message: Message) -> Result: ...
