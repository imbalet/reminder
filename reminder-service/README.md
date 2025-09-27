# Reminder service <!-- omit from toc -->

Микросервис для управления напоминаниями и отправки их в очередь публикации.

- [Функционал](#функционал)
- [Стек](#стек)
- [Схема взаимодействия](#схема-взаимодействия)
- [Конфигурация](#конфигурация)
  - [Приложение](#приложение)
  - [Тесты](#тесты)
- [Установка и запуск](#установка-и-запуск)
  - [Установка зависимостей](#установка-зависимостей)
  - [Применение миграций БД](#применение-миграций-бд)
  - [Запуск](#запуск)
  - [Тесты](#тесты-1)
- [API](#api)
- [Работа с RabbitMQ](#работа-с-rabbitmq)
  - [Отправка напоминаний](#отправка-напоминаний)
- [TODO](#todo)


## Функционал

- Управление напоминаниями (CRUD)
- Планирование и отправка напоминаний в очередь RabbitMQ
- Обработка ошибок отправки (DLX / DLQ)
- Деактивация напоминаний при отсутствии методов доставки


## Стек

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- RabbitMQ (aio-pika)


## Схема взаимодействия

![Схема](https://gist.githubusercontent.com/imbalet/39006a5be11887095d5af0d4139cc240/raw/90a0bb67f51faf185f27df895913787ea179195d/schema_reminder_service.svg)


## Конфигурация

### Приложение

В `.env` файле в корне проекта нужно указать следующие переменные окружения:

`LOG_LEVEL="INFO"` - Уровень логирования приложения DEBUG/INFO/WARNING/ERROR/CRITICAL.  
`DB_USER="postgres"` - Имя пользователя PostgreSQL.  
`DB_PASS="your_password"` - Пароль пользователя PostgreSQL.  
`DB_NAME="your_db_name"` - Название базы данных PostgreSQL.  
`DB_HOST="localhost"` - Хост PostgreSQL.  
`DB_PORT="5432"` - Порт PostgreSQL.  

Настройки RabbitMQ:

`RMQ_DLQ_FAILED_REMINDERS_NAME="<your_dlq_name>"` - Название dead letter queue для сообщений о неуспешной отправке напоминаний.  
`RMQ_DLX_FAILED_REMINDERS_NAME="<your_dlx_name>"` - Название dead letter exchange (DLX) для пересылки ошибок.  
`RMQ_DELIVERY_METHOD_ADD_QUEUE="<your_queue_name>"` - Очередь для событий добавления метода доставки.  
`RMQ_DELIVERY_METHOD_REMOVE_QUEUE="<your_queue_name>"` - Очередь для событий удаления метода доставки.  
`RMQ_REMINDER_DEACTIVATE_QUEUE="<your_queue_name>"` - Очередь для уведомления о деактивированных напоминаниях.  
`RMQ_REMINDERS_QUEUE="<your_queue_name>"` - Очередь для отправки напоминаний (основная очередь).

`RMQ_USER="guest"` - Имя пользователя RabbitMQ.  
`RMQ_PASS="<your_password>"` - Пароль RabbitMQ.  
`RMQ_HOST="localhost"` - Хост RabbitMQ.  
`RMQ_PORT="5672"` - Порт RabbitMQ.  


### Тесты

В `tests/.env.test` файле нужно указать следующие переменные окружения:

`TEST_DB_USER="postgres"` - Имя пользователя PostgreSQL.  
`TEST_DB_PASS="<your_password>"` - Пароль пользователя PostgreSQL.  
`TEST_DB_NAME="<your_db_name>"` - Название тестовой базы данных PostgreSQL.  
`TEST_DB_HOST="localhost"` - Хост PostgreSQL.  
`TEST_DB_PORT="5432"` - Порт PostgreSQL.  

> Важно: используйте отдельную чистую базу только для тестов. Все данные из неё будут удалены при запуске тестов. Название тестовой базы не должно совпадать с основной.


## Установка и запуск

### Установка зависимостей

#### UV (рекомендуется) <!-- omit from toc -->

```bash
uv sync
```

#### Poetry <!-- omit from toc -->

```bash
poetry install
```

#### pip <!-- omit from toc -->

```bash
# Создать виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate

pip3 install -e .
```


### Применение миграций БД

Для миграций БД используется Alembic.  
Для применения миграций необходимо выполнить:

```bash
alembic upgrade head
```


### Запуск

```bash
uvicorn reminder_service.main:app --port 8001
```

Или через UV

```bash
uv run -m uvicorn reminder_service.main:app --port 8001
```


### Тесты

Для запуска тестов необходимо установить дополнительные пакеты.

Через UV

```bash
uv sync --all-groups
```

Или установить вручную:

```bash
pip install httpx pytest pytest-asyncio pytest-cov pytest-mock
```

Запуск тестов:

```bash
python -m pytest ./tests
```


## API

Сервис доверяет заголовку `app-user-id`, который должен установить api-gateway при валидации запросов пользователей при помощи JWT или другого метода аутентификации. Не допускается использование сервиса без api-gateway в целях безопасности. Значение заголовка - ID пользователя, который совершает запрос. Он необходим для всех API методов.

Описание API методов: [api.md](./api.md)


## Работа с RabbitMQ

### Напоминания, при отправке которых произошла ошибка <!-- omit from toc -->

При ошибке отправки напоминания автоматически помещаются в DLX (dead letter exchange) обменник типа `fanout` и доставляются в сервис напоминаний и в user service для создания системного уведомления об ошибке отправки.

Структура сообщения включает в себя все данные о напоминании и методы доставки:

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

# Основная схема напоминания
class Reminder(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    content: str
    remind_date: datetime
    created_at: datetime
    edited_at: datetime | None
    delivery_methods: list[DeliveryMethod]
```

Пример сообщения:

```json
{
  "id": "c5f1d8f2-3f74-4b8c-9a1f-5bde5a7f2a1c",
  "user_id": "2a7c7a9e-7f74-41e1-9a42-3c9a5b7d4e3f",
  "title": "Напоминание о встрече",
  "content": "Zoom созвон",
  "remind_date": "2026-09-30T10:00:00Z",
  "created_at": "2026-09-25T15:32:00Z",
  "edited_at": null,
  "delivery_methods": [
    {
      "id": "c5f1d8f2-3f74-4b8c-9a1f-5bde5a7f2a1c",
      "delivery_method": "telegram",
      "contact_value": "12345"
    }
  ]
}
```

### Добавление метода доставки <!-- omit from toc -->

При добавлении метода доставки user service публикует сообщение с данными метода доставки. Reminder service использует эти события для локального хранения копии данных о методах доставки. 

Структура сообщения:

```python
class DeliveryMethodEnum(str, Enum):
    TELEGRAM = "telegram"
    EMAIL = "email"

class DeliveryMethodRMQ(BaseModel):
    id: UUID
    user_id: UUID
    delivery_method: DeliveryMethodEnum
    contact_value: str
```

Пример сообщения:

```json
{
  "id": "91f23b16-3f6a-4f20-9d34-6d3a2a48fbb1",
  "user_id": "a3f7d8b2-8f21-4b91-9c72-1b9f5a7c2e4d",
  "delivery_method": "telegram",
  "contact_value": "1234"
}
```

### Удаление метода доставки <!-- omit from toc -->

При удалении метода доставки публикуется текстовое сообщение с UUID удалённого метода. При этом метод доставки удаляется из базы данных и из всех связанных с ним напоминаниях.

Пример сообщения:

```
91f23b16-3f6a-4f20-9d34-6d3a2a48fbb1
```

### Деактивация напоминания <!-- omit from toc -->

При удалении всех методов доставки у напоминания, оно будет деактивировано, reminder service при этом отправляет сообщение в очередь для уведомления пользователя о том, что некоторые его напоминания стали неактивны.

Структура сообщения:

```json
{
  "user_id": "uuid",
  "reminders": [
    {
      "id": "uuid",
      "title": "string",
      "content": "string",
      "remind_date": "datetime"
    }
  ]
}
```

Пример сообщения:  

```json
{
  "user_id": "2a7c7a9e-7f74-41e1-9a42-3c9a5b7d4e3f",
  "reminders": [
    {
      "id": "c5f1d8f2-3f74-4b8c-9a1f-5bde5a7f2a1c",
      "title": "Напоминание о встрече",
      "content": "Zoom созвон с командой",
      "remind_date": "2025-09-30T10:00:00Z"
    },
    {
      "id": "e6a8b0f4-5d12-45b3-9d62-9fbdc7a9e0c1",
      "title": "Сдать отчёт",
      "content": "До конца дня",
      "remind_date": "2025-09-28T18:00:00Z"
    }
  ]
}
```

### Отправка напоминаний

Reminder service каждую минуту получает из БД напоминания, которые должны быть отправлены. Далее все напоминания отправляются в очередь для дальнейшей обработки и отправки пользователю.

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


## TODO
- [ ] Реализовать более точную отправку уведомлений с TTL
- [ ]  ...