# User service <!-- omit from toc -->

Микросервис для хранения профилей пользователей, управления методами доставки и работы с системными уведомлениями.

- [Функционал](#функционал)
- [Стек](#стек)
- [Схема взаимодействия](#схема-взаимодействия)
- [Установка и запуск](#установка-и-запуск)
  - [Локальный запуск](#локальный-запуск)
    - [Конфигурация](#конфигурация)
    - [Установка зависимостей](#установка-зависимостей)
    - [Применение миграций БД](#применение-миграций-бд)
    - [Запуск](#запуск)
    - [Тесты](#тесты)
  - [Запуск из Docker compose](#запуск-из-docker-compose)
    - [Конфигурация](#конфигурация-1)
    - [Запуск](#запуск-1)
    - [Тесты](#тесты-1)
- [API](#api)
- [Работа с RabbitMQ](#работа-с-rabbitmq)
- [Работа с Redis](#работа-с-redis)
- [TODO](#todo)


## Функционал

- Управление методами доставки напоминаний (добавление, удаление)
- Хранение профилей пользователей и их связь с методами доставки
- Подтверждение методов доставки (только Telegram) по коду
- Отправка системных уведомлений


## Стек

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Redis
- RabbitMQ (aio-pika)


## Схема взаимодействия

![Схема](https://gist.githubusercontent.com/imbalet/39006a5be11887095d5af0d4139cc240/raw/4ab3716f57078d3a0a83f3f68a9d45ccc56963b9/schema_user_service.svg)

## Установка и запуск

### Локальный запуск

#### Конфигурация

##### Приложение <!-- omit from toc -->

В файле `.env` в корне проекта нужно указать следующие переменные окружения:

| Переменная                         | Пример              | Описание                                                            |
| ---------------------------------- | ------------------- | ------------------------------------------------------------------- |
| `LOG_LEVEL`                        | `INFO`              | Уровень логирования приложения (DEBUG/INFO/WARNING/ERROR/CRITICAL)  |
| `DB_USER`                          | `postgres`          | Имя пользователя PostgreSQL                                         |
| `DB_PASS`                          | `your_password`     | Пароль пользователя PostgreSQL                                      |
| `DB_NAME`                          | `your_db_name`      | Название базы данных PostgreSQL                                     |
| `DB_HOST`                          | `localhost`         | Хост PostgreSQL                                                     |
| `DB_PORT`                          | `5432`              | Порт PostgreSQL                                                     |
| `RMQ_DLQ_FAILED_REMINDERS_NAME`    | `<your_dlq_name>`   | Название dead letter queue RabbitMQ для ошибок отправки напоминаний |
| `RMQ_DLX_FAILED_REMINDERS_NAME`    | `<your_dlx_name>`   | Название обменника для DLQ RabbitMQ                                 |
| `RMQ_USER_ADD_QUEUE`               | `<your_queue_name>` | Название очереди событий регистрации пользователей                  |
| `RMQ_DELIVERY_METHOD_ADD_QUEUE`    | `<your_queue_name>` | Название очереди для публикации событий добавления метода доставки  |
| `RMQ_DELIVERY_METHOD_REMOVE_QUEUE` | `<your_queue_name>` | Название очереди для публикации событий удаления метода доставки    |
| `RMQ_REMINDER_DEACTIVATE_QUEUE`    | `<your_queue_name>` | Название очереди для обработки деактивированных напоминаний         |
| `RMQ_USER`                         | `guest`             | Имя пользователя RabbitMQ                                           |
| `RMQ_PASS`                         | `<your_password>`   | Пароль пользователя RabbitMQ                                        |
| `RMQ_HOST`                         | `localhost`         | Хост RabbitMQ                                                       |
| `RMQ_PORT`                         | `5672`              | Порт RabbitMQ                                                       |
| `REDIS_HOST`                       | `localhost`         | Хост Redis                                                          |
| `REDIS_PORT`                       | `6379`              | Порт Redis                                                          |
| `REDIS_PASSWORD`                   | `<your_password>`   | Пароль Redis                                                        |

##### Тесты <!-- omit from toc -->
 
В файле `tests/.env.test` в корне проекта нужно указать следующие переменные окружения:

| Переменная     | Пример            | Описание                                                       |
| -------------- | ----------------- | -------------------------------------------------------------- |
| `TEST_DB_USER` | `postgres`        | Имя пользователя PostgreSQL для тестов                         |
| `TEST_DB_PASS` | `<your_password>` | Пароль пользователя PostgreSQL для тестов                      |
| `TEST_DB_NAME` | `<your_db_name>`  | Название тестовой базы данных (должна быть отдельной и чистой) |
| `TEST_DB_HOST` | `localhost`       | Хост PostgreSQL для тестов                                     |
| `TEST_DB_PORT` | `5432`            | Порт PostgreSQL для тестов                                     |

> Важно: используйте отдельную чистую базу только для тестов. Все данные из неё будут удалены при запуске тестов. Название тестовой базы не должно совпадать с основной.



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


#### Применение миграций БД

Для миграций БД используется Alembic.  
Для применения миграций необходимо выполнить:

```bash
alembic upgrade head
```


#### Запуск

```bash
uvicorn user_service.main:app --port 8002
```

Или через UV

```bash
uv run -m uvicorn user_service.main:app --port 8002
```


#### Тесты

Для запуска тестов необходимо установить дополнительные пакеты.

Через UV

```bash
uv sync --all-groups
```

При работе с другим менеджером пакетов необходимо вручную установить следующие пакеты

```
"httpx>=0.28.1",
"pytest>=8.4.1",
"pytest-asyncio>=1.0.0",
"pytest-cov>=6.2.1",
"pytest-mock>=3.14.1",
```

```bash
pip install httpx pytest pytest-asyncio pytest-cov pytest-mock
```

Тесты запускаются командой 

```bash
python -m pytest ./tests
```

### Запуск из Docker compose

Используется два Docker compose конфига:
- `docker-compose.yml` для production запуска
- `docker-compose.test.yml` для запуска тестов


#### Конфигурация

##### Приложение <!-- omit from toc -->

В файле `.env` в корне проекта нужно указать следующие переменные окружения:

| Переменная                         | Пример              | Описание                                                            |
| ---------------------------------- | ------------------- | ------------------------------------------------------------------- |
| `APP_PORT`                         | `8000`              | Порт, по которому приложение будет доступно на хосте                |
| `LOG_LEVEL`                        | `INFO`              | Уровень логирования приложения (DEBUG/INFO/WARNING/ERROR/CRITICAL)  |
| `DB_USER`                          | `postgres`          | Имя пользователя PostgreSQL                                         |
| `DB_PASS`                          | `your_password`     | Пароль пользователя PostgreSQL                                      |
| `DB_NAME`                          | `your_db_name`      | Название базы данных PostgreSQL                                     |
| `RMQ_DLQ_FAILED_REMINDERS_NAME`    | `<your_dlq_name>`   | Название dead letter queue RabbitMQ для ошибок отправки напоминаний |
| `RMQ_DLX_FAILED_REMINDERS_NAME`    | `<your_dlx_name>`   | Название обменника для DLQ RabbitMQ                                 |
| `RMQ_USER_ADD_QUEUE`               | `<your_queue_name>` | Название очереди событий регистрации пользователей                  |
| `RMQ_DELIVERY_METHOD_ADD_QUEUE`    | `<your_queue_name>` | Название очереди для публикации событий добавления метода доставки  |
| `RMQ_DELIVERY_METHOD_REMOVE_QUEUE` | `<your_queue_name>` | Название очереди для публикации событий удаления метода доставки    |
| `RMQ_REMINDER_DEACTIVATE_QUEUE`    | `<your_queue_name>` | Название очереди для обработки деактивированных напоминаний         |
| `RMQ_USER`                         | `guest`             | Имя пользователя RabbitMQ                                           |
| `RMQ_PASS`                         | `<your_password>`   | Пароль пользователя RabbitMQ                                        |
| `RMQ_HOST`                         | `localhost`         | Хост RabbitMQ                                                       |
| `RMQ_PORT`                         | `5672`              | Порт RabbitMQ                                                       |
| `REDIS_HOST`                       | `localhost`         | Хост Redis                                                          |
| `REDIS_PORT`                       | `6379`              | Порт Redis                                                          |
| `REDIS_PASSWORD`                   | `<your_password>`   | Пароль Redis                                                        |


#### Запуск 

При использовании этого метода, запускается два контейнера: с приложением и с базой данных.
Прочие зависимости (RabbitMQ, Redis) должны запускаться отдельно.

Запуск:

```bash
docker compose -p app-user-service up --build -d
```

> Важно, перед запуском необходимо верно указать все переменные окружения в файле `.env`.  
> При использовании локальных Redis, RabbitMQ необходимо указать ip адрес интерфейса хоста.
> Узнать его можно командой `ip addr show docker0`  
> Или же использовать `host.docker.internal` в поддерживаемых системах.

Остановка:

```bash
docker compose -p app-user-service down
```


#### Тесты

Для запуска тестов необходимо выполнить:

```bash
docker compose -f docker-compose.test.yml -p user-test up --build --abort-on-container-exit --exit-code-from app
docker compose -f docker-compose.test.yml -p user-test down -v --rmi local
```

## API

Сервис доверяет заголовку `app-user-id`, который должен установить api-gateway при валидации запросов пользователей при помощи JWT или другого метода аутентификации. Не допускается использование сервиса без api-gateway в целях безопасности. Значение заголовка - ID пользователя, который совершает запрос. Он необходим для всех API методов.

Описание API методов: [api.md](./api.md)


## Работа с RabbitMQ

### Напоминания, при отправке которых произошла ошибка <!-- omit from toc -->

При ошибке отправки напоминания автоматически помещаются в DLX (dead letter exchange) обменник `RMQ_DLX_FAILED_REMINDERS_NAME` типа `fanout` и доставляются в сервис напоминаний и в user service для создания системного уведомления об ошибке отправки.

User service работает с очередью `RMQ_DLQ_FAILED_REMINDERS_NAME`.

Структура сообщения включает в себя все данные о напоминании и методы доставки:

```python
class DeliveryMethod(BaseModel):
    id: UUID
    delivery_method: DeliveryMethodEnum
    contact_value: str


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

### Регистрация пользователя <!-- omit from toc -->

При регистрации нового пользователя auth service отправляет сообщение в очередь `RMQ_USER_ADD_QUEUE` с данными нового пользователя.  

Структура сообщения:

```python
class User(BaseModel):
    id: UUID
    email: EmailStr
    name: str
```

Пример сообщения:
```json
{
  "id": "a3f7d8b2-8f21-4b91-9c72-1b9f5a7c2e4d",
  "email": "user@example.com",
  "name": "John Doe"
}
```

### Добавление метода доставки напоминаний <!-- omit from toc -->

При добавлении метода доставки user service публикует сообщение с данными нового метода доставки в очередь `RMQ_DELIVERY_METHOD_ADD_QUEUE`.

Структура сообщения:  

```python
class DeliveryMethodEnum(str, Enum):
    TELEGRAM = "telegram"
    EMAIL = "email"

class MetaData(BaseModel):
    username: str | None = None

class DeliveryMethodRMQ(BaseModel):
    id: UUID
    user_id: UUID
    delivery_method: DeliveryMethodEnum
    contact_value: str
    meta_data: MetaData
```

`MetaData` - объект с метаданными метода доставки. На данный момент реализует хранение имени пользователя telegram для возможности идентификации клиентом метода доставки.   

Пример сообщения:  

```json
{
  "id": "91f23b16-3f6a-4f20-9d34-6d3a2a48fbb1",
  "user_id": "a3f7d8b2-8f21-4b91-9c72-1b9f5a7c2e4d",
  "delivery_method": "telegram",
  "contact_value": "1234",
  "meta_data": {"username": "user"}
}
```

### Удаление метода доставки напоминаний <!-- omit from toc -->

При удалении метода доставки напоминаний user service публикует текстовое сообщение с UUID удаленного метода доставки в очередь `RMQ_DELIVERY_METHOD_REMOVE_QUEUE`.

Пример:  

```
91f23b16-3f6a-4f20-9d34-6d3a2a48fbb1
```

### Деактивация напоминания <!-- omit from toc -->

При удалении всех методов доставки у напоминания, оно будет деактивировано, reminder service при этом отправляет сообщение в очередь `RMQ_REMINDER_DEACTIVATE_QUEUE` для уведомления пользователя о том, что некоторые его напоминания стали неактивны.

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

## Работа с Redis

Одна база данных Redis используется вместе с confirm service для хранения кодов подтверждения для добавления телеграм как метода доставки напоминаний. Для привязки пользователь в телеграм боте получает код подтверждения, который записывается в Redis с TTL вместе с username и ID чата пользователя, далее пользователь отправляет его в теле API запроса при добавлении метода доставки, user service проверяет наличие кода в Redis и, при наличии, получает username и ID чата для отправки напоминаний.

Данные в Redis хранятся как `ключ:значение`, где ключ - это код подтверждения, а значение - username и ID чата в виде строки, разделенной символом `:` 

Пример: 
```
Ключ      -> 1234
Значение  -> username:987654321
```


## TODO
- [ ] Реализовать работу с email
- [ ]  ...
- [ ]  ...

