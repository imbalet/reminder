import httpx

from src.schemas import Message
from src.services import SenderInterface


class TelegramSender(SenderInterface):

    def __init__(self, token: str) -> None:
        self.token = token
        self.url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    async def send(self, contact_value: str, message: Message):
        text = f"{message.title}\n{message.content}"

        payload = {"chat_id": contact_value, "text": text}
        async with httpx.AsyncClient(base_url=self.url, timeout=10.0) as client:
            response = await client.post(url="", json=payload)
            response.raise_for_status()
            return response.json()
