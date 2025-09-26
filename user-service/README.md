# User service

Микросервис для хранения профилей пользователей, управления методами доставки и работы с системными уведомлениями.


# Функционал

- Управление методами доставки напоминаний (добавление, удаление)
- Хранение профилей пользователей и их связь с методами доставки
- Подтверждение методов доставки (только Telegram) по коду
- Отправка системных уведомлений


# Стек

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Redis
- RabbitMQ (aio-pika)


# Схема взаимодействия

![Схема](https://gist.githubusercontent.com/imbalet/39006a5be11887095d5af0d4139cc240/raw/4ab3716f57078d3a0a83f3f68a9d45ccc56963b9/schema_user_service.svg)


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
uvicorn user_service.main:app --port 8002
```

Или через uv

```bash
uv run -m uvicorn user_service.main:app --reload --port 8002
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
`RMQ_USER_ADD_QUEUE="<your_queue_name>"` - Название очереди событий регистрации пользователей  
`RMQ_DELIVERY_METHOD_ADD_QUEUE="<your_queue_name>"` - Название очереди RabbitMQ для публикации событий добавления метода доставки  
`RMQ_DELIVERY_METHOD_REMOVE_QUEUE="<your_queue_name>"` - Название очереди RabbitMQ для публикации событий удаления метода доставки  
`RMQ_REMINDER_DEACTIVATE_QUEUE="<your_queue_name>"` - Название очереди RabbitMQ для обработки деактивированных напоминаний (напоминаний без метода доставки)  

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
- [ ] Реализовать работу с email
- [ ]  ...
- [ ]  ...

