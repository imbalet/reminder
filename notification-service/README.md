# Notification service <!-- omit from toc -->

Микросервис для отправки напоминаний пользователям по указанным каналам связи.

- [Функционал](#функционал)
- [Стек](#стек)
- [Установка и запуск](#установка-и-запуск)
  - [Конфигурация](#конфигурация)
  - [Локальный запуск](#локальный-запуск)
    - [Установка зависимостей](#установка-зависимостей)
    - [Запуск](#запуск)
  - [Запуск из Docker](#запуск-из-docker)
- [Отправка напоминаний](#отправка-напоминаний)
- [Работа с RabbitMQ](#работа-с-rabbitmq)




## Функционал

- Получение напоминаний из очереди RabbitMQ 
- Отправка напоминаний по указанным каналам доставки


## Стек

- Python 3.12
- aiogram
- RabbitMQ (aio-pika)


## Установка и запуск

### Конфигурация

#### Приложение <!-- omit from toc -->

В `.env` файле в корне проекта укажите следующие переменные окружения:


| Переменная                      | Пример                        | Описание                                                          |
| ------------------------------- | ----------------------------- | ----------------------------------------------------------------- |
| `LOG_LEVEL`                     | `INFO`                        | Уровень логирования приложения: DEBUG/INFO/WARNING/ERROR/CRITICAL |
| `TG_BOT_TOKEN`                  | `<your_telegram_bot_token>`   | Токен Telegram-бота, используемый для отправки уведомлений        |
| `RMQ_DLX_FAILED_REMINDERS_NAME` | `<your_dlx_name>`             | Название обменника (DLX) для DLQ                                  |
| `RMQ_REMINDERS_QUEUE`           | `<your_reminders_queue_name>` | Основная очередь для сообщений о напоминаниях                     |
| `RMQ_USER`                      | `guest`                       | Имя пользователя RabbitMQ                                         |
| `RMQ_PASS`                      | `<your_password>`             | Пароль пользователя RabbitMQ                                      |
| `RMQ_HOST`                      | `localhost`                   | Хост RabbitMQ                                                     |
| `RMQ_PORT`                      | `5672`                        | Порт RabbitMQ                                                     |


### Локальный запуск

#### Установка зависимостей

##### UV <!-- omit from toc -->

```bash
uv sync
```

##### Poetry <!-- omit from toc -->

```bash
poetry install
```

##### pip <!-- omit from toc -->

```bash
# Создать виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate

pip3 install -e .
```


#### Запуск

```bash
python src/notification_service/main.py
```

Или

```bash
python -m notification_service.main
```


### Запуск из Docker

При использовании этого метода, запускается два контейнера: с приложением и с базой данных.
Прочие зависимости (RabbitMQ, Redis) должны запускаться отдельно.

Сборка:

```bash
docker build . -t "notification-service"
```

Запуск:

```bash
docker run -d --env-file .env --name app-notification-service notification-service:latest
```

> Важно, перед запуском необходимо верно указать все переменные окружения в файле `.env`.  
> При использовании локальных Redis, RabbitMQ необходимо указать ip адрес интерфейса хоста.
> Узнать его можно командой `ip addr show docker0`  
> Или же использовать `host.docker.internal` в поддерживаемых системах.

Остановка:

```bash
docker stop app-notification-service
```


## Отправка напоминаний

Для каждого метода доставки напоминаний необходимо реализовать сервис отправки. На данный момент для демонстрации работы реализован только сервис отправки для Telegram.

Архитектура выстроена таким образом, что интегрировать новый сервис отправки просто.

Все доступные методы доставки описаны в `schemas.py` в Enum `DeliveryMethodEnum`:

```python
class DeliveryMethodEnum(str, Enum):
    TELEGRAM = "telegram"
    EMAIL = "email"
```

Для корректной работы нового метода доставки необходима согласованность значения Enum с остальными микросервисами, работающими с методами доставки.

В `main.py` есть маппинг для метода доставки и сервиса отправки:

```python
senders: dict[DeliveryMethodEnum, SenderInterface] = {
    DeliveryMethodEnum.TELEGRAM: TelegramSender(config.TG_BOT_TOKEN),
}
```

Ключом словаря является метод доставки из Enum, а значением - объект сервиса отправки.

Определен интерфейс в виде абстрактного класса которому должны соответствовать сервисы отправки:

```python
class SenderInterface(ABC):
    @abstractmethod
    async def send(self, contact_value: str, message: Message) -> Result: ...
```

Таким образом, сервис отправки обязательно должен иметь асинхронный метод send, который принимает строку `contact_value` обозначающую "адрес" доставки - ID чата в случае с Telegram или же email адрес для электронной почты. Также метод должен принимать и работать с объектом схемы `Message`:
```python
class Message(BaseModel):
    title: str
    content: str
```

В процессе работы сервис должен сам обрабатывать возникающие исключения и ошибки. Возвращаемое значение - структура `Result` с результатом отправки:

```python
class ResultStatusEnum(str, Enum):
    ERROR = "error"
    SUCCESS = "success"


class Result(BaseModel):
    status: ResultStatusEnum
    data: dict
```

После реализации сервиса и регистрации его в маппинге данный микросервис будет корректно работать с новым методом доставки.



## Работа с RabbitMQ

### Отправка напоминаний <!-- omit from toc -->

Reminder service отправляют в очередь `RMQ_REMINDERS_QUEUE` все напоминания для дальнейшей обработки и отправки пользователю.

Структура сообщения:

```python
# Дополнительные схемы
class DeliveryMethodEnum(str, Enum):
    TELEGRAM = "telegram"
    EMAIL = "email"

class DeliveryMethod(BaseModel):
    id: UUID
    user_id: UUID
    delivery_method: DeliveryMethodEnum
    contact_value: str

class Status(Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    INACTIVE = "inactive"

# Схема данных напоминания
class ReminderResponse(ReminderBase):
    id: UUID
    title: str
    content: str
    remind_date: datetime
    user_id: UUID
    created_at: datetime
    status: Status
    edited_at: datetime | None
    delivery_methods: list[DeliveryMethod]
```

Пример сообщения:

```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "user_id": "9a1b2c3d-4e5f-6789-0abc-def123456789",
  "created_at": "2025-09-27T12:34:56.789Z",
  "edited_at": "2025-09-27T13:00:00.000Z",
  "status": "pending",
  "delivery_methods": [
    {
      "id": "1e3d5c7a-8b9f-4d12-9abc-1234567890ab",
      "user_id": "9a1b2c3d-4e5f-6789-0abc-def123456789",
      "delivery_method": "telegram",
      "contact_value": "1234"
    },
    {
      "id": "2a4b6c8d-9e0f-1a23-4bcd-9876543210fe",
      "user_id": "9a1b2c3d-4e5f-6789-0abc-def123456789",
      "delivery_method": "email",
      "contact_value": "user@example.com"
    }
  ]
}

```