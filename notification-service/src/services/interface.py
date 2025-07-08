from abc import ABC, abstractmethod

from src.schemas import Message


class SenderInterface(ABC):
    @abstractmethod
    async def send(self, contact_value: str, message: Message): ...
