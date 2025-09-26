# Reminder service

Микросервис для работы с напоминаниями


# Функционал

- Управление напоминаниями (CRUD)
- Отправка напоминаний в очередь RabbitMQ
- Обработка ошибок отправки напоминаний


# Стек

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Redis
- RabbitMQ (aio-pika)


# Схема взаимодействия

![Схема](https://gist.githubusercontent.com/imbalet/39006a5be11887095d5af0d4139cc240/raw/90a0bb67f51faf185f27df895913787ea179195d/schema_reminder_service.svg)


# Установка и запуск

## Установка зависимостей

### uv

```bash
uv sync
```

### Poetry

```bash
poetry install
```

### pip

```bash
# Создать виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate

pip3 install -e .
```


## Запуск

```bash
uvicorn reminder_service.main:app --port 8001
```

Или через uv

```bash
uv run -m uvicorn reminder_service.main:app --reload --port 8001
```


# Конфигурация

## Приложение

В `.env` файле в корне проекта нужно указать следующие переменные окружения:

`LOG_LEVEL="INFO"` - Уровень логирования приложения DEBUG/INFO/WARNING/ERROR/CRITICAL  
`DB_USER="postgres"` - Имя пользователя PostgreSQL  
`DB_PASS="your_password"` - Пароль пользователя PostgreSQL  
`DB_NAME="your_db_name"` - Название базы данных PostgreSQL  
`DB_HOST="localhost"` - Хост PostgreSQL  
`DB_PORT="5432"` - Порт PostgreSQL  

`RMQ_DLQ_FAILED_REMINDERS_NAME="<your_dlq_name>"` - Название dead letter queue RabbitMQ для обработки ошибок отправки напоминаний  
`RMQ_DLX_FAILED_REMINDERS_NAME="<your_dlx_name>"` - Название обменника для DLQ RabbitMQ для обработки ошибок отправки напоминаний  
`RMQ_DELIVERY_METHOD_ADD_QUEUE="<your_queue_name>"` - Название очереди RabbitMQ для публикации событий добавления метода доставки  
`RMQ_DELIVERY_METHOD_REMOVE_QUEUE="<your_queue_name>"` - Название очереди RabbitMQ для публикации событий удаления метода доставки  
`RMQ_REMINDER_DEACTIVATE_QUEUE="<your_queue_name>"` - Название очереди RabbitMQ для обработки деактивированных напоминаний (напоминаний без метода доставки)  
`RMQ_REMINDERS_QUEUE="<your_queue_name>"` - Название очереди RabbitMQ для отправки напоминаний  

`RMQ_USER="guest"` - Имя пользователя RabbitMQ  
`RMQ_PASS="<your_password>"` - Пароль пользователя RabbitMQ  
`RMQ_HOST="localhost"` - Хост RabbitMQ  
`RMQ_PORT="5672"` - Порт RabbitMQ  

`REDIS_HOST="localhost"` - Хост Redis  
`REDIS_PORT="6379"` - Порт Redis  
`REDIS_PASSWORD="<your_password>"` - Пароль Redis  

## Тесты

В `tests/.env.test` файле нужно указать следующие переменные окружения:

`TEST_DB_USER="postgres"` - Имя пользователя PostgreSQL  
`TEST_DB_PASS="<your_password>"` - Пароль пользователя PostgreSQL  
`TEST_DB_NAME="<your_db_name>"` - Название тестовой базы данных PostgreSQL  
`TEST_DB_HOST="localhost"` - Хост PostgreSQL  
`TEST_DB_PORT="5432"` - Порт PostgreSQL  

>Важно: используйте отдельную чистую базу только для тестов. Все данные из неё будут удалены при запуске тестов. Название тестовой базы не должно совпадать с основной.

# API

Методы принимают заголовок `app-user-id`, который должен установить api-gateway при валидации запросов пользователей при помощи JWT или другого метода аутентификации. Не допускается использование сервиса без api-gateway в целях безопасности.

Описание API методов: [api.md](./api.md)


# TODO
- [ ] Реализовать более точную отправку уведомлений с TTL
- [ ]  ...
- [ ]  ...

