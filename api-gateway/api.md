# /api/auth/register

## POST

\[auth\]

Регистрация нового пользователя — создаёт аккаунт и возвращает данные пользователя.

### Тело запроса:

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

UserRegisterRequest

**Свойства:**

| Свойство | Тип    | Обязательное | Описание                       |
| -------- | ------ | ------------ | ------------------------------ |
| `email`  | string | Да           | Электронная почта пользователя |
| `name`   | string | Да           | Имя пользователя               |

## Ответы:

### Код состояния: 201

User was registered

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

UserResponse

**Свойства:**

| Свойство        | Тип    | Обязательное | Описание                                     |
| --------------- | ------ | ------------ | -------------------------------------------- |
| `id`            | string | Да           | Уникальный идентификатор пользователя (UUID) |
| `email`         | string | Да           | Электронная почта пользователя               |
| `registered_at` | string | Да           | Время регистрации (ISO 8601)                 |

### Код состояния: 409

User already exists

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

ErrorResponse

**Свойства:**

| Свойство | Тип    | Обязательное | Описание |
| -------- | ------ | ------------ | -------- |
| `detail` | string | Да           | Detail   |

### Код состояния: 422

Validation Error

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

HTTPValidationError

**Свойства:**

| Свойство | Тип   | Обязательное | Описание |
| -------- | ----- | ------------ | -------- |
| `detail` | array | Нет          | Detail   |

# /api/auth/login

## POST

\[auth\]

Аутентификация пользователя — возвращает access и refresh токены. Поддерживается только прямая аутентификация по email и паролю

### Тело запроса:

**Content-Type:**`application/x-www-form-urlencoded`

**Тип:**`object`

**Название:**

Body\_login\_api\_auth\_login\_post

**Свойства:**

| Свойство        | Тип            | Обязательное | Описание                      |
| --------------- | -------------- | ------------ | ----------------------------- |
| `grant_type`    | string \| null | Нет          | Тип гранта (обычно пусто)     |
| `username`      | string         | Да           | Email или логин пользователя  |
| `password`      | string         | Да           | Пароль пользователя           |
| `scope`         | string         | Нет          | Запрашиваемые права доступа   |
| `client_id`     | string \| null | Нет          | Идентификатор клиента (OAuth) |
| `client_secret` | string \| null | Нет          | Секрет клиента (OAuth)        |

## Ответы:

### Код состояния: 200

Successful Response

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

TokenResponse

**Свойства:**

| Свойство       | Тип    | Обязательное | Описание     |
| -------------- | ------ | ------------ | ------------ |
| `access_token` | string | Да           | Access Token |
| `token_type`   | string | Да           | Token Type   |

**HTTP-only cookie**

| Название        | Тип    | Обязательное | Описание                         |
| --------------- | ------ | ------------ | -------------------------------- |
| `refresh_token` | string | Да           | Кука для обновления access_token |

> Cookie`refresh_token`доступна только браузеру и не видна в JSON-ответе.

### Код состояния: 401

Incorrect username or password

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

ErrorResponse

**Свойства:**

| Свойство | Тип    | Обязательное | Описание |
| -------- | ------ | ------------ | -------- |
| `detail` | string | Да           | Detail   |

### Код состояния: 422

Validation Error

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

HTTPValidationError

**Свойства:**

| Свойство | Тип   | Обязательное | Описание |
| -------- | ----- | ------------ | -------- |
| `detail` | array | Нет          | Detail   |

## OPTIONS

\[auth\]

Поддерживает CORS preflight — отвечает без тела с кодом 200.

## Ответы:

### Код состояния: 200

Successful Response


# /api/auth/refresh

## POST

\[auth\]

Обновление access-токена — использует refresh-куку и выдаёт новый access и refresh.

## Ответы:

### Код состояния: 200

Successful Response

**HTTP-only cookie**

| Название        | Тип    | Обязательное | Описание            |
| --------------- | ------ | ------------ | ------------------- |
| `refresh_token` | string | Да           | Новый Refresh token |

> Cookie`refresh_token`доступна только браузеру и не видна в JSON-ответе.


# /api/auth/logout

## POST

\[auth\]

Выход из учётной записи — удаляет refresh-куку у клиента.

> При вызове эндпоинта`refresh_token`cookie удаляется с клиента.

## Ответы:

### Код состояния: 204

Successful Response

**HTTP-only кука, удаляемая сервером:**

| Название        | Тип    | Обязательное | Описание                    |
| --------------- | ------ | ------------ | --------------------------- |
| `refresh_token` | string | Нет          | Cookie удаляется при logout |


# /api/reminders/

## POST

\[reminders\]

Создание нового напоминания.

### Тело запроса:

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

ReminderCreate

**Свойства:**

| Свойство               | Тип    | Обязательное | Описание                                 |
| ---------------------- | ------ | ------------ | ---------------------------------------- |
| `title`                | string | Да           | Название                                 |
| `content`              | string | Да           | Содержимое напоминания                   |
| `remind_date`          | string | Да           | Дата и время напоминания (ISO 8601)      |
| `delivery_methods_ids` | array  | Да           | Массив UUID методов доставки напоминания |

## Ответы:

### Код состояния: 201

Delivery method created

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

ReminderResponse

**Свойства:**

| Свойство           | Тип                                                     | Обязательное | Описание                                    |
| ------------------ | ------------------------------------------------------- | ------------ | ------------------------------------------- |
| `title`            | string                                                  | Да           | Заголовок напоминания                       |
| `content`          | string                                                  | Да           | Текст напоминания                           |
| `remind_date`      | string                                                  | Да           | Время срабатывания напоминания (ISO 8601)   |
| `id`               | string                                                  | Да           | Уникальный идентификатор напоминания (UUID) |
| `user_id`          | string                                                  | Да           | UUID владельца (пользователя)               |
| `created_at`       | string                                                  | Да           | Время создания (ISO 8601)                   |
| `status`           | string, Enum\['pending', 'sent', 'failed', 'inactive'\] | Да           | Текущий статус отправки напоминания         |
| `edited_at`        | string \| null                                          | Да           | Время последнего редактирования (или null)  |
| `delivery_methods` | array                                                   | Да           | Массив объектов методов доставки            |

### Код состояния: 400

Invalid delivery method(s)

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

ReminderResponse

**Свойства:**

| Свойство           | Тип                                                     | Обязательное | Описание                         |
| ------------------ | ------------------------------------------------------- | ------------ | -------------------------------- |
| `title`            | string                                                  | Да           | Название                         |
| `content`          | string                                                  | Да           | Содержимое напоминания           |
| `remind_date`      | string                                                  | Да           | Дата и время напоминания         |
| `id`               | string                                                  | Да           | UUID                             |
| `user_id`          | string                                                  | Да           | UUID пользователя                |
| `created_at`       | string                                                  | Да           | Дата и время создания            |
| `status`           | string, Enum\['pending', 'sent', 'failed', 'inactive'\] | Да           | Статус                           |
| `edited_at`        | string \| null                                          | Да           | Дата и время редактирования      |
| `delivery_methods` | array                                                   | Да           | Массив объектов методов доставки |

### Код состояния: 422

Validation Error

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

HTTPValidationError

**Свойства:**

| Свойство | Тип   | Обязательное | Описание |
| -------- | ----- | ------------ | -------- |
| `detail` | array | Нет          | Detail   |

# /api/reminders/my

## GET

\[reminders\]

Получить список напоминаний пользователя с пагинацией.

### query

| Имя    | Тип     | Обязательный | Формат |
| ------ | ------- | ------------ | ------ |
| `page` | integer | Нет          | -      |
| `size` | integer | Нет          | -      |

## Ответы:

### Код состояния: 200

Successful Response

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

Page\[ReminderResponse\]

**Свойства:**

| Свойство | Тип     | Обязательное | Описание                               |
| -------- | ------- | ------------ | -------------------------------------- |
| `items`  | array   | Да           | Список напоминаний на текущей странице |
| `total`  | integer | Да           | Общее количество напоминаний           |
| `page`   | integer | Да           | Номер текущей страницы                 |
| `size`   | integer | Да           | Количество элементов на странице       |
| `pages`  | integer | Да           | Всего страниц                          |

### Код состояния: 422

Validation Error

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

HTTPValidationError

**Свойства:**

| Свойство | Тип   | Обязательное | Описание |
| -------- | ----- | ------------ | -------- |
| `detail` | array | Нет          | Detail   |

# /api/reminders/{reminder\_id}

## GET

\[reminders\]

Получить напоминание по идентификатору.

### path

| Имя           | Тип    | Обязательный | Формат |
| ------------- | ------ | ------------ | ------ |
| `reminder_id` | string | Да           | uuid   |

## Ответы:

### Код состояния: 200

Successful Response

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

ReminderResponse

**Свойства:**

| Свойство           | Тип                                                     | Обязательное | Описание                         |
| ------------------ | ------------------------------------------------------- | ------------ | -------------------------------- |
| `title`            | string                                                  | Да           | Название                         |
| `content`          | string                                                  | Да           | Содержимое напоминания           |
| `remind_date`      | string                                                  | Да           | Дата и время напоминания         |
| `id`               | string                                                  | Да           | UUID                             |
| `user_id`          | string                                                  | Да           | UUID пользователя                |
| `created_at`       | string                                                  | Да           | Дата и время создания            |
| `status`           | string, Enum\['pending', 'sent', 'failed', 'inactive'\] | Да           | Статус                           |
| `edited_at`        | string \| null                                          | Да           | Дата и время редактирования      |
| `delivery_methods` | array                                                   | Да           | Массив объектов методов доставки |

### Код состояния: 403

No access to reminder

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

ErrorResponse

**Свойства:**

| Свойство | Тип    | Обязательное | Описание |
| -------- | ------ | ------------ | -------- |
| `detail` | string | Да           | Detail   |

### Код состояния: 422

Validation Error

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

HTTPValidationError

**Свойства:**

| Свойство | Тип   | Обязательное | Описание |
| -------- | ----- | ------------ | -------- |
| `detail` | array | Нет          | Detail   |

## DELETE

\[reminders\]

Delete By Id

### path

| Имя           | Тип    | Обязательный | Формат |
| ------------- | ------ | ------------ | ------ |
| `reminder_id` | string | Да           | uuid   |

## Ответы:

### Код состояния: 204

Successful Response

### Код состояния: 403

No access to reminder

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

ErrorResponse

**Свойства:**

| Свойство | Тип    | Обязательное | Описание |
| -------- | ------ | ------------ | -------- |
| `detail` | string | Да           | Detail   |

### Код состояния: 422

Validation Error

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

HTTPValidationError

**Свойства:**

| Свойство | Тип   | Обязательное | Описание |
| -------- | ----- | ------------ | -------- |
| `detail` | array | Нет          | Detail   |

## PATCH

\[reminders\]

Edit By Id

### path

| Имя           | Тип    | Обязательный | Формат |
| ------------- | ------ | ------------ | ------ |
| `reminder_id` | string | Да           | uuid   |

### Тело запроса:

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

ReminderEdit

**Свойства:**

| Свойство               | Тип            | Обязательное | Описание             |
| ---------------------- | -------------- | ------------ | -------------------- |
| `title`                | string \| null | Да           | Title                |
| `content`              | string \| null | Да           | Content              |
| `remind_date`          | string \| null | Да           | Remind Date          |
| `delivery_methods_ids` | array \| null  | Да           | Delivery Methods Ids |

## Ответы:

### Код состояния: 200

Successful Response

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

ReminderResponse

**Свойства:**

| Свойство           | Тип                                                     | Обязательное | Описание                         |
| ------------------ | ------------------------------------------------------- | ------------ | -------------------------------- |
| `title`            | string                                                  | Да           | Название                         |
| `content`          | string                                                  | Да           | Содержимое напоминания           |
| `remind_date`      | string                                                  | Да           | Дата и время напоминания         |
| `id`               | string                                                  | Да           | UUID                             |
| `user_id`          | string                                                  | Да           | UUID пользователя                |
| `created_at`       | string                                                  | Да           | Дата и время создания            |
| `status`           | string, Enum\['pending', 'sent', 'failed', 'inactive'\] | Да           | Статус                           |
| `edited_at`        | string \| null                                          | Да           | Дата и время редактирования      |
| `delivery_methods` | array                                                   | Да           | Массив объектов методов доставки |

### Код состояния: 403

No access to reminder

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

ErrorResponse

**Свойства:**

| Свойство | Тип    | Обязательное | Описание |
| -------- | ------ | ------------ | -------- |
| `detail` | string | Да           | Detail   |

### Код состояния: 400

No access to reminder

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

ErrorResponse

**Свойства:**

| Свойство | Тип    | Обязательное | Описание |
| -------- | ------ | ------------ | -------- |
| `detail` | string | Да           | Detail   |

### Код состояния: 422

Validation Error

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

HTTPValidationError

**Свойства:**

| Свойство | Тип   | Обязательное | Описание |
| -------- | ----- | ------------ | -------- |
| `detail` | array | Нет          | Detail   |

# /api/delivery/

## POST

\[delivery\]

Добавление метода доставки — создаёт e-mail или Telegram канал для доставки напоминаний.

### Тело запроса:

**Content-Type:**`application/json`

**Любая из следующих схем:**

- **Тип:**`object`  
  **Название:**  
  TelegramDelivery  
  **Свойства:**  
  | Свойство          | Тип    | Обязательное | Описание                  |
  | ----------------- | ------ | ------------ | ------------------------- |
  | `delivery_method` | string | Да           | "telegram" метод доставки |
  | `confirm_code`    | string | Да           | Код подтверждения         |
  
- **Тип:**`object`  
  **Название:**  
  EmailDelivery  
  **Свойства:**  
  | Свойство          | Тип    | Обязательное | Описание               |
  | ----------------- | ------ | ------------ | ---------------------- |
  | `delivery_method` | string | Да           | "email" метод доставки |
  | `contact_value`   | string | Да           | Контакт (email)        |
  ## Ответы:

### Код состояния: 201

Delivery method created

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

DeliveryMethodResponse

**Свойства:**

| Свойство          | Тип                                 | Обязательное | Описание                                                |
| ----------------- | ----------------------------------- | ------------ | ------------------------------------------------------- |
| `id`              | string                              | Да           | Уникальный идентификатор метода (UUID)                  |
| `user_id`         | string                              | Да           | UUID владельца (пользователя)                           |
| `created_at`      | string                              | Да           | Время создания (ISO 8601)                               |
| `delivery_method` | string, Enum\['telegram', 'email'\] | Да           | Тип метода доставки                                     |
| `contact_value`   | string                              | Да           | Контактная информация (email или telegram id)           |
| `meta_data`       | object                              | Да           | Дополнительные параметры (JSON) - username для telegram |

### Код состояния: 400

Invalid or expired Telegram confirmation code

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

ErrorResponse

**Свойства:**

| Свойство | Тип    | Обязательное | Описание |
| -------- | ------ | ------------ | -------- |
| `detail` | string | Да           | Detail   |

### Код состояния: 409

Delivery method already exists

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

ErrorResponse

**Свойства:**

| Свойство | Тип    | Обязательное | Описание |
| -------- | ------ | ------------ | -------- |
| `detail` | string | Да           | Detail   |

### Код состояния: 422

Validation Error

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

HTTPValidationError

**Свойства:**

| Свойство | Тип   | Обязательное | Описание |
| -------- | ----- | ------------ | -------- |
| `detail` | array | Нет          | Detail   |

# /api/delivery/my

## GET

\[delivery\]

Получить все методы доставки пользователя с пагинацией.

### query

| Имя    | Тип     | Обязательный | Формат |
| ------ | ------- | ------------ | ------ |
| `page` | integer | Нет          | -      |
| `size` | integer | Нет          | -      |

## Ответы:

### Код состояния: 200

Successful Response

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

Page\[DeliveryMethodResponse\]

**Свойства:**

| Свойство | Тип     | Обязательное | Описание                            |
| -------- | ------- | ------------ | ----------------------------------- |
| `items`  | array   | Да           | Список методов доставки на странице |
| `total`  | integer | Да           | Общее количество методов            |
| `page`   | integer | Да           | Номер текущей страницы              |
| `size`   | integer | Да           | Размер страницы (элементов)         |
| `pages`  | integer | Да           | Всего страниц                       |

### Код состояния: 422

Validation Error

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

HTTPValidationError

**Свойства:**

| Свойство | Тип   | Обязательное | Описание |
| -------- | ----- | ------------ | -------- |
| `detail` | array | Нет          | Detail   |

# /api/delivery/{method\_id}

## GET

\[delivery\]

Получить метод доставки по идентификатору.

### path

| Имя         | Тип    | Обязательный | Формат |
| ----------- | ------ | ------------ | ------ |
| `method_id` | string | Да           | uuid   |

## Ответы:

### Код состояния: 200

Successful Response

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

DeliveryMethodResponse

**Свойства:**

| Свойство          | Тип                                 | Обязательное | Описание                                                |
| ----------------- | ----------------------------------- | ------------ | ------------------------------------------------------- |
| `id`              | string                              | Да           | Уникальный идентификатор метода (UUID)                  |
| `user_id`         | string                              | Да           | UUID владельца метода                                   |
| `created_at`      | string                              | Да           | Время создания (ISO 8601)                               |
| `delivery_method` | string, Enum\['telegram', 'email'\] | Да           | Тип метода доставки                                     |
| `contact_value`   | string                              | Да           | Контактная информация (email или telegram id)           |
| `meta_data`       | object                              | Да           | Дополнительные параметры (JSON) - username для telegram |

### Код состояния: 403

No access to delivery method

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

ErrorResponse

**Свойства:**

| Свойство | Тип    | Обязательное | Описание |
| -------- | ------ | ------------ | -------- |
| `detail` | string | Да           | Detail   |

### Код состояния: 422

Validation Error

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

HTTPValidationError

**Свойства:**

| Свойство | Тип   | Обязательное | Описание |
| -------- | ----- | ------------ | -------- |
| `detail` | array | Нет          | Detail   |

## DELETE

\[delivery\]

Delete By Id

### path

| Имя         | Тип    | Обязательный | Формат |
| ----------- | ------ | ------------ | ------ |
| `method_id` | string | Да           | uuid   |

## Ответы:

### Код состояния: 204

Successful Response

### Код состояния: 403

No access to delivery method

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

ErrorResponse

**Свойства:**

| Свойство | Тип    | Обязательное | Описание |
| -------- | ------ | ------------ | -------- |
| `detail` | string | Да           | Detail   |

### Код состояния: 422

Validation Error

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

HTTPValidationError

**Свойства:**

| Свойство | Тип   | Обязательное | Описание |
| -------- | ----- | ------------ | -------- |
| `detail` | array | Нет          | Detail   |

# /api/notification/my

## GET

\[notifications\]

Получить список уведомлений пользователя с пагинацией.

### query

| Имя    | Тип     | Обязательный | Формат |
| ------ | ------- | ------------ | ------ |
| `page` | integer | Нет          | -      |
| `size` | integer | Нет          | -      |

## Ответы:

### Код состояния: 200

Successful Response

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

Page\[NotificationResponse\]

**Свойства:**

| Свойство | Тип     | Обязательное | Описание                         |
| -------- | ------- | ------------ | -------------------------------- |
| `items`  | array   | Да           | Список уведомлений на странице   |
| `total`  | integer | Да           | Общее количество уведомлений     |
| `page`   | integer | Да           | Номер текущей страницы           |
| `size`   | integer | Да           | Количество элементов на странице |
| `pages`  | integer | Да           | Всего страниц                    |

### Код состояния: 422

Validation Error

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

HTTPValidationError

**Свойства:**

| Свойство | Тип   | Обязательное | Описание |
| -------- | ----- | ------------ | -------- |
| `detail` | array | Нет          | Detail   |

# /api/notification/{notification\_id}

## GET

\[notifications\]

Получить уведомление по идентификатору.

### path

| Имя               | Тип    | Обязательный | Формат |
| ----------------- | ------ | ------------ | ------ |
| `notification_id` | string | Да           | uuid   |

## Ответы:

### Код состояния: 200

Successful Response

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

NotificationResponse

**Свойства:**

| Свойство     | Тип     | Обязательное | Описание                                    |
| ------------ | ------- | ------------ | ------------------------------------------- |
| `id`         | string  | Да           | Уникальный идентификатор уведомления (UUID) |
| `user_id`    | string  | Да           | UUID владельца уведомления                  |
| `title`      | string  | Да           | Заголовок уведомления                       |
| `content`    | string  | Да           | Текст уведомления                           |
| `created_at` | string  | Да           | Время создания (ISO 8601)                   |
| `is_read`    | boolean | Да           | Флаг прочтено (true/false)                  |

### Код состояния: 403

No access to notification

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

ErrorResponse

**Свойства:**

| Свойство | Тип    | Обязательное | Описание |
| -------- | ------ | ------------ | -------- |
| `detail` | string | Да           | Detail   |

### Код состояния: 422

Validation Error

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

HTTPValidationError

**Свойства:**

| Свойство | Тип   | Обязательное | Описание |
| -------- | ----- | ------------ | -------- |
| `detail` | array | Нет          | Detail   |

## DELETE

\[notifications\]

Удаление уведомления по идентификатору.

### path

| Имя               | Тип    | Обязательный | Формат |
| ----------------- | ------ | ------------ | ------ |
| `notification_id` | string | Да           | uuid   |

## Ответы:

### Код состояния: 204

Notification was deleted

### Код состояния: 403

No access to notification

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

ErrorResponse

**Свойства:**

| Свойство | Тип    | Обязательное | Описание |
| -------- | ------ | ------------ | -------- |
| `detail` | string | Да           | Detail   |

### Код состояния: 422

Validation Error

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

HTTPValidationError

**Свойства:**

| Свойство | Тип   | Обязательное | Описание |
| -------- | ----- | ------------ | -------- |
| `detail` | array | Нет          | Detail   |

## PATCH

\[notifications\]

Отметить уведомление как прочитанное.

### path

| Имя               | Тип    | Обязательный | Формат |
| ----------------- | ------ | ------------ | ------ |
| `notification_id` | string | Да           | uuid   |

## Ответы:

### Код состояния: 200

Successful Response

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

NotificationResponse

**Свойства:**

| Свойство     | Тип     | Обязательное | Описание                                    |
| ------------ | ------- | ------------ | ------------------------------------------- |
| `id`         | string  | Да           | Уникальный идентификатор уведомления (UUID) |
| `user_id`    | string  | Да           | UUID владельца уведомления                  |
| `title`      | string  | Да           | Заголовок уведомления                       |
| `content`    | string  | Да           | Текст уведомления                           |
| `created_at` | string  | Да           | Время создания (ISO 8601)                   |
| `is_read`    | boolean | Да           | Флаг прочтено (true/false)                  |

### Код состояния: 403

No access to notification

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

ErrorResponse

**Свойства:**

| Свойство | Тип    | Обязательное | Описание |
| -------- | ------ | ------------ | -------- |
| `detail` | string | Да           | Detail   |

### Код состояния: 422

Validation Error

**Content-Type:**`application/json`

**Тип:**`object`

**Название:**

HTTPValidationError

**Свойства:**

| Свойство | Тип   | Обязательное | Описание |
| -------- | ----- | ------------ | -------- |
| `detail` | array | Нет          | Detail   |

