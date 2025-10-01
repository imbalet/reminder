# Auth service <!-- omit from toc -->

Микросервис для регистрации, авторизации, управления ключами и JWKS

- [Функционал](#функционал)
- [Стек](#стек)
- [Схема взаимодействия](#схема-взаимодействия)
- [Установка и запуск](#установка-и-запуск)
  - [Локальный запуск](#локальный-запуск)
    - [Конфигурация](#конфигурация)
    - [Установка зависимостей](#установка-зависимостей)
    - [Запуск](#запуск)
    - [Тесты](#тесты)
  - [Запуск из Docker compose](#запуск-из-docker-compose)
    - [Конфигурация](#конфигурация-1)
    - [Запуск](#запуск-1)
    - [Тесты](#тесты-1)
- [API](#api)
- [Сервис ключей](#сервис-ключей)
- [Работа с RabbitMQ](#работа-с-rabbitmq)
- [TODO](#todo)



## Функционал

- Регистрация и авторизация пользователя
- Управление ключами подписи JWT токенов (ротация, выпуск новых ключей)
- JWKS эндпоинт 


## Стек

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- RabbitMQ (aio-pika)
- PyJWT


## Схема взаимодействия

![Схема](https://gist.githubusercontent.com/imbalet/39006a5be11887095d5af0d4139cc240/raw/00fad2241245872eaaf55fb438f78a6233ba9787/schema_auth_service.svg)




## Установка и запуск

### Локальный запуск

#### Конфигурация

##### Приложение <!-- omit from toc -->

В `.env` файле в корне проекта нужно указать следующие переменные окружения:

| Переменная                      | Пример            | Описание                                                                             |
| ------------------------------- | ----------------- | ------------------------------------------------------------------------------------ |
| `LOG_LEVEL`                     | `INFO`            | Уровень логирования DEBUG/INFO/WARNING/ERROR/CRITICAL                                |
| `DB_USER`                       | `postgres`        | Имя пользователя PostgreSQL                                                          |
| `DB_PASS`                       | `your_password`   | Пароль пользователя PostgreSQL                                                       |
| `DB_NAME`                       | `your_db_name`    | Название базы данных PostgreSQL                                                      |
| `DB_HOST`                       | `localhost`       | Хост PostgreSQL                                                                      |
| `DB_PORT`                       | `5432`            | Порт PostgreSQL                                                                      |
| `RMQ_USER_ADD_QUEUE`            | `<queue_name>`    | Название очереди событий регистрации пользователей                                   |
| `RMQ_USER`                      | `guest`           | Имя пользователя RabbitMQ                                                            |
| `RMQ_PASS`                      | `<your_password>` | Пароль пользователя RabbitMQ                                                         |
| `RMQ_HOST`                      | `localhost`       | Хост RabbitMQ                                                                        |
| `RMQ_PORT`                      | `5672`            | Порт RabbitMQ                                                                        |
| `ALGORITHM`                     | `RS256`           | Алгоритм подписи JWT токенов. Поддерживается только `RS256`                          |
| `ACCESS_TOKEN_EXPIRE_MINUTES`   | `15`              | Срок действия access token в минутах                                                 |
| `REFRESH_TOKEN_EXPIRE_DAYS`     | `7`               | Срок действия refresh token в днях                                                   |
| `KEY_PAIR_EXPIRES_DAYS`         | `15`              | Срок действия пары ключей для подписи JWT в днях                                     |
| `ROTATING_BEFORE_EXPIRING_DAYS` | `2`               | Время в днях, за которое до истечения срока действия пары ключей выполняется ротация |

##### Тесты <!-- omit from toc -->

В `tests/.env.test` файле нужно указать следующие переменные окружения:

| Переменная     | Пример            | Описание                                 |
| -------------- | ----------------- | ---------------------------------------- |
| `TEST_DB_USER` | `postgres`        | Имя пользователя PostgreSQL              |
| `TEST_DB_PASS` | `<your_password>` | Пароль пользователя PostgreSQL           |
| `TEST_DB_NAME` | `<your_db_name>`  | Название тестовой базы данных PostgreSQL |
| `TEST_DB_HOST` | `localhost`       | Хост PostgreSQL                          |
| `TEST_DB_PORT` | `5432`            | Порт PostgreSQL                          |

>Важно: используйте отдельную чистую базу только для тестов. Все данные из неё будут удалены при запуске тестов. Название тестовой базы не должно совпадать с основной.



#### Установка зависимостей

##### uv <!-- omit from toc -->

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
uvicorn auth_service.main:app --port 8000
```

Или через uv

```bash
uv run -m uvicorn auth_service.main:app --port 8000
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


| Переменная                      | Пример            | Описание                                                                             |
| ------------------------------- | ----------------- | ------------------------------------------------------------------------------------ |
| `APP_PORT`                      | `8000`            | Порт, по которому приложение будет доступно на хосте                                 |
| `LOG_LEVEL`                     | `INFO`            | Уровень логирования DEBUG/INFO/WARNING/ERROR/CRITICAL                                |
| `DB_USER`                       | `postgres`        | Имя пользователя PostgreSQL                                                          |
| `DB_PASS`                       | `your_password`   | Пароль пользователя PostgreSQL                                                       |
| `DB_NAME`                       | `your_db_name`    | Название базы данных PostgreSQL                                                      |
| `RMQ_USER_ADD_QUEUE`            | `<queue_name>`    | Название очереди событий регистрации пользователей                                   |
| `RMQ_USER`                      | `guest`           | Имя пользователя RabbitMQ                                                            |
| `RMQ_PASS`                      | `<your_password>` | Пароль пользователя RabbitMQ                                                         |
| `RMQ_HOST`                      | `localhost`       | Хост RabbitMQ                                                                        |
| `RMQ_PORT`                      | `5672`            | Порт RabbitMQ                                                                        |
| `ALGORITHM`                     | `RS256`           | Алгоритм подписи JWT токенов. Поддерживается только `RS256`                          |
| `ACCESS_TOKEN_EXPIRE_MINUTES`   | `15`              | Срок действия access token в минутах                                                 |
| `REFRESH_TOKEN_EXPIRE_DAYS`     | `7`               | Срок действия refresh token в днях                                                   |
| `KEY_PAIR_EXPIRES_DAYS`         | `15`              | Срок действия пары ключей для подписи JWT в днях                                     |
| `ROTATING_BEFORE_EXPIRING_DAYS` | `2`               | Время в днях, за которое до истечения срока действия пары ключей выполняется ротация |


#### Запуск 

При использовании этого метода, запускается два контейнера: с приложением и с базой данных.
Прочие зависимости (RabbitMQ, Redis) должны запускаться отдельно.

Запуск:

```bash
docker compose -p app-auth-service up --build -d
```

> Важно, перед запуском необходимо верно указать все переменные окружения в файле `.env`.  
> При использовании локальных Redis, RabbitMQ необходимо указать ip адрес интерфейса хоста.
> Узнать его можно командой `ip addr show docker0`  
> Или же использовать `host.docker.internal` в поддерживаемых системах.

Остановка:

```bash
docker compose -p app-auth-service down
```

#### Тесты

Для запуска тестов необходимо выполнить:

```bash
docker compose -f docker-compose.test.yml -p auth-test up --build --abort-on-container-exit --exit-code-from app
docker compose -f docker-compose.test.yml -p auth-test down -v --rmi local
```

## API

Описание API методов: [api.md](./api.md)

## Сервис ключей

Был реализован собственный сервис для работы с ключами.   
Реализовано:
- Сохранение ключей в файл 
- Загрузка ключей из файла
- Хранение данных о ключах в формате json
- Автоматическая ротация ключей
- JWKS данные

Все ключи вместе с файлом data.json для хранения данных о ключах хранятся в папке `.secrets`.  
При запуске папка автоматически создается и происходит ротация ключей при необходимости. При отсутствии ключей они создаются и хранятся в папке `.secrets`.

## Работа с RabbitMQ

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

## TODO
- [ ] Реализовать шифрование приватных ключей и более безопасное хранение
- [ ] ...