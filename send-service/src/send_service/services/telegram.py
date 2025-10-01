import httpx

from send_service.schemas import Message, Result, ResultStatusEnum
from send_service.services import SenderInterface


class TelegramSender(SenderInterface):

    def __init__(self, token: str) -> None:
        self.token = token
        self.url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    async def send(self, contact_value: str, message: Message) -> Result:
        text = f"{message.title}\n{message.content}"

        payload = {"chat_id": contact_value, "text": text}
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url=self.url, json=payload)
            if response.status_code != 200:
                return Result(status=ResultStatusEnum.ERROR, data=response.json())
            return Result(status=ResultStatusEnum.SUCCESS, data=response.json())
