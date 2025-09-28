# Notification service <!-- omit from toc -->

Микросервис для отправки напоминаний пользователям по указанным каналам связи.

- [Функционал](#функционал)
- [Стек](#стек)
- [Конфигурация](#конфигурация)
  - [Приложение](#приложение)
- [Установка и запуск](#установка-и-запуск)
  - [Установка зависимостей](#установка-зависимостей)
  - [Запуск](#запуск)
- [Отправка напоминаний](#отправка-напоминаний)



## Функционал

- Получение напоминаний из очереди RabbitMQ 
- Отправка напоминаний по указанным каналам доставки


## Стек

- Python 3.12
- aiogram
- RabbitMQ (aio-pika)


## Конфигурация

### Приложение

В `.env` файле в корне проекта укажите следующие переменные окружения:


| Переменная                    | Описание                                                                 | Пример / значение по умолчанию |
| ----------------------------- | ------------------------------------------------------------------------ | ------------------------------ |
| LOG_LEVEL                     | Уровень логирования приложения: DEBUG/INFO/WARNING/ERROR/CRITICAL        | INFO                           |
| TG_BOT_TOKEN                  | Токен Telegram-бота, используемый для отправки уведомлений               | <your_telegram_bot_token>      |
| RMQ_DLQ_FAILED_REMINDERS_NAME | Название dead letter queue для обработки неуспешных отправок напоминаний | <your_dlq_name>                |
| RMQ_DLX_FAILED_REMINDERS_NAME | Название обменника (DLX) для DLQ                                         | <your_dlx_name>                |
| RMQ_REMINDERS_QUEUE           | Основная очередь для сообщений о напоминаниях                            | <your_reminders_queue_name>    |
| RMQ_USER                      | Имя пользователя RabbitMQ                                                | guest                          |
| RMQ_PASS                      | Пароль пользователя RabbitMQ                                             | <your_password>                |
| RMQ_HOST                      | Хост RabbitMQ                                                            | localhost                      |
| RMQ_PORT                      | Порт RabbitMQ                                                            | 5672                           |



## Установка и запуск

### Установка зависимостей

#### UV <!-- omit from toc -->

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


### Запуск

```bash
python src/notification_service/main.py
```

Или

```bash
python -m notification_service.main
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

