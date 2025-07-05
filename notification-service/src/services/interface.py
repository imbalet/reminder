from abc import ABC, abstractmethod

from src.schemas import Message


class SenderInterface(ABC):
    @abstractmethod
    async def send(self, recipient: str, message: Message): ...
