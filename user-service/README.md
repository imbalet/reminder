# User service
Микросервис для хранения профилей пользователей, управления методами доставки и работы с системными уведомлениями.


# Функционал
- Работа с методами доставки напоминаний (добавлени, удаление)
- Хранение профилей пользователей, связь с методами доставки
- Подтверждение методов доставки (только Telegram) по коду
- Работа с системными уведомлениями


# Стек
- Python 3.12
- FastAPI
- Postgresql
- Redis
- Rabbitmq


# Схема взаимодействия
![Схема](https://gist.githubusercontent.com/imbalet/39006a5be11887095d5af0d4139cc240/raw/3cd4536a2fbc82315479186c4a0ab4a2b350f8cf/schema_user_service.svg)


# Установка и запуск
## Установка зависимостей
### uv
```bash
# Создать виртуальное окружение
uv venv .venv
source .venv/bin/activate

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
# В корне проекта
export PYTHONPATH=$(pwd)

uvicorn src.main:app --port 8003
```


# Конфигурация
## Приложение
В `.env` файле в корне проекта нужно указать следущие переменные окружения:

`LOG_LEVEL="INFO"` - Уровень логгирования приложения DEBUG/INFO/WARNING/ERROR/CRITICAL  
`DB_USER="postgres"` - Имя пользователя Postgres  
`DB_PASS="your_password"` - Пароль пользователя Postgres  
`DB_NAME="your_db_name"` - Название базы данных Postgres  
`DB_HOST="localhost"` - Хост Postgres  
`DB_PORT="5432"` - Порт Postgres  

`RMQ_DLQ_NAME="<your_dlq_name>"` - Название dead letter queue RabbitMQ  
`RMQ_USER_ADD_QUEUE="<your_queue_name>"` - Название очереди событий регистрации пользователей  
`RMQ_USER="guest"` - Имя пользователя RabbitMQ  
`RMQ_PASS="<your_password>"` - Пароль пользователя RabbitMQ  
`RMQ_HOST="localhost"` - Хост RabbitMQ  
`RMQ_PORT="5672"` - Порт RabbitMQ  

`REDIS_HOST="localhost"` - Хост Redis  
`REDIS_PORT="6379"` - Порт Redis  
`REDIS_PASSWORD="<your_password>"` Пароль Redis  

## Тесты
В `teats/.env.test` файле нужно указать следущие переменные окружения:

`TEST_DB_USER="postgres"` - Имя пользователя Postgres  
`TEST_DB_PASS="<your_password>"` - Пароль пользователя Postgres  
`TEST_DB_NAME="<your_db_name>"` - Название тестовой базы данных Postgres  
`TEST_DB_HOST="localhost"` - Хост Postgres  
`TEST_DB_PORT="5432"` - Порт Postgres  


# API
Методы принимают заголовок `app-user-id`, который должен уствновить api-gateway при валидации запросов пользователей при помощи JWT или другого метода аутентификации. Не допускается использование сервиса без api-gateway в целях безопасности.

Описание API методов: [api.md](./api.md)


# TODO
- [ ] Реализовать работу с email
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
