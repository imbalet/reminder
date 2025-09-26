# /api/delivery/

## POST

\[delivery\]

Create Method

### header

| Имя             | Тип    | Обязательный | Формат |
| --------------- | ------ | ------------ | ------ |
| ` app-user-id ` | string | Да           | uuid   |

### Тело запроса:

**Content-Type:** ` application/json `

**Любая из следующих схем:**

- **Тип:** ` object `  
  **Название:**  
  TelegramDelivery  
  **Свойства:**  
  | Свойство            | Тип    | Обязательное | Описание        |
  | ------------------- | ------ | ------------ | --------------- |
  | ` delivery_method ` | string | Да           | Delivery Method |
  | ` confirm_code `    | string | Да           | Confirm Code    |
  
- **Тип:** ` object `  
  **Название:**  
  EmailDelivery  
  **Свойства:**  
  | Свойство            | Тип    | Обязательное | Описание        |
  | ------------------- | ------ | ------------ | --------------- |
  | ` delivery_method ` | string | Да           | Delivery Method |
  | ` contact_value `   | string | Да           | Contact Value   |
  ## Ответы:

### Код состояния: 201

Delivery method created

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

DeliveryMethodResponse

**Свойства:**

| Свойство            | Тип                                 | Обязательное | Описание           |
| ------------------- | ----------------------------------- | ------------ | ------------------ |
| ` id `              | string                              | Да           | Id                 |
| ` user_id `         | string                              | Да           | User Id            |
| ` created_at `      | string                              | Да           | Created At         |
| ` delivery_method ` | string, Enum\['telegram', 'email'\] | Да           | DeliveryMethodEnum |
| ` contact_value `   | string                              | Да           | Contact Value      |
| ` meta_data `       | object                              | Да           | MetaData           |

### Код состояния: 400

Invalid or expired Telegram confirmation code

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

ErrorResponse

**Свойства:**

| Свойство   | Тип    | Обязательное | Описание |
| ---------- | ------ | ------------ | -------- |
| ` detail ` | string | Да           | Detail   |

### Код состояния: 409

Delivery method already exists

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

ErrorResponse

**Свойства:**

| Свойство   | Тип    | Обязательное | Описание |
| ---------- | ------ | ------------ | -------- |
| ` detail ` | string | Да           | Detail   |

### Код состояния: 422

Validation Error

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

HTTPValidationError

**Свойства:**

| Свойство   | Тип   | Обязательное | Описание |
| ---------- | ----- | ------------ | -------- |
| ` detail ` | array | Нет          | Detail   |

# /api/delivery/my

## GET

\[delivery\]

Get All Methods

### query

| Имя      | Тип     | Обязательный | Формат |
| -------- | ------- | ------------ | ------ |
| ` page ` | integer | Нет          |  -     |
| ` size ` | integer | Нет          |  -     |

### header

| Имя             | Тип    | Обязательный | Формат |
| --------------- | ------ | ------------ | ------ |
| ` app-user-id ` | string | Да           | uuid   |

## Ответы:

### Код состояния: 200

Successful Response

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

Page\[DeliveryMethodResponse\]

**Свойства:**

| Свойство  | Тип     | Обязательное | Описание |
| --------- | ------- | ------------ | -------- |
| ` items ` | array   | Да           | Items    |
| ` total ` | integer | Да           | Total    |
| ` page `  | integer | Да           | Page     |
| ` size `  | integer | Да           | Size     |
| ` pages ` | integer | Да           | Pages    |

### Код состояния: 422

Validation Error

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

HTTPValidationError

**Свойства:**

| Свойство   | Тип   | Обязательное | Описание |
| ---------- | ----- | ------------ | -------- |
| ` detail ` | array | Нет          | Detail   |

# /api/delivery/{method\_id}

## GET

\[delivery\]

Get Method

### path

| Имя           | Тип    | Обязательный | Формат |
| ------------- | ------ | ------------ | ------ |
| ` method_id ` | string | Да           | uuid   |

### header

| Имя             | Тип    | Обязательный | Формат |
| --------------- | ------ | ------------ | ------ |
| ` app-user-id ` | string | Да           | uuid   |

## Ответы:

### Код состояния: 200

Successful Response

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

DeliveryMethodResponse

**Свойства:**

| Свойство            | Тип                                 | Обязательное | Описание           |
| ------------------- | ----------------------------------- | ------------ | ------------------ |
| ` id `              | string                              | Да           | Id                 |
| ` user_id `         | string                              | Да           | User Id            |
| ` created_at `      | string                              | Да           | Created At         |
| ` delivery_method ` | string, Enum\['telegram', 'email'\] | Да           | DeliveryMethodEnum |
| ` contact_value `   | string                              | Да           | Contact Value      |
| ` meta_data `       | object                              | Да           | MetaData           |

### Код состояния: 403

No access to delivery method

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

ErrorResponse

**Свойства:**

| Свойство   | Тип    | Обязательное | Описание |
| ---------- | ------ | ------------ | -------- |
| ` detail ` | string | Да           | Detail   |

### Код состояния: 422

Validation Error

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

HTTPValidationError

**Свойства:**

| Свойство   | Тип   | Обязательное | Описание |
| ---------- | ----- | ------------ | -------- |
| ` detail ` | array | Нет          | Detail   |

## DELETE

\[delivery\]

Delete Method

### path

| Имя           | Тип    | Обязательный | Формат |
| ------------- | ------ | ------------ | ------ |
| ` method_id ` | string | Да           | uuid   |

### header

| Имя             | Тип    | Обязательный | Формат |
| --------------- | ------ | ------------ | ------ |
| ` app-user-id ` | string | Да           | uuid   |

## Ответы:

### Код состояния: 204

Successful Response

### Код состояния: 403

No access to delivery method

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

ErrorResponse

**Свойства:**

| Свойство   | Тип    | Обязательное | Описание |
| ---------- | ------ | ------------ | -------- |
| ` detail ` | string | Да           | Detail   |

### Код состояния: 422

Validation Error

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

HTTPValidationError

**Свойства:**

| Свойство   | Тип   | Обязательное | Описание |
| ---------- | ----- | ------------ | -------- |
| ` detail ` | array | Нет          | Detail   |

# /api/notification/my

## GET

\[notifications\]

Get All Notifications

### query

| Имя      | Тип     | Обязательный | Формат |
| -------- | ------- | ------------ | ------ |
| ` page ` | integer | Нет          |  -     |
| ` size ` | integer | Нет          |  -     |

### header

| Имя             | Тип    | Обязательный | Формат |
| --------------- | ------ | ------------ | ------ |
| ` app-user-id ` | string | Да           | uuid   |

## Ответы:

### Код состояния: 200

Successful Response

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

Page\[NotificationResponse\]

**Свойства:**

| Свойство  | Тип     | Обязательное | Описание |
| --------- | ------- | ------------ | -------- |
| ` items ` | array   | Да           | Items    |
| ` total ` | integer | Да           | Total    |
| ` page `  | integer | Да           | Page     |
| ` size `  | integer | Да           | Size     |
| ` pages ` | integer | Да           | Pages    |

### Код состояния: 422

Validation Error

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

HTTPValidationError

**Свойства:**

| Свойство   | Тип   | Обязательное | Описание |
| ---------- | ----- | ------------ | -------- |
| ` detail ` | array | Нет          | Detail   |

# /api/notification/{notification\_id}

## GET

\[notifications\]

Get Notification

### path

| Имя                 | Тип    | Обязательный | Формат |
| ------------------- | ------ | ------------ | ------ |
| ` notification_id ` | string | Да           | uuid   |

### header

| Имя             | Тип    | Обязательный | Формат |
| --------------- | ------ | ------------ | ------ |
| ` app-user-id ` | string | Да           | uuid   |

## Ответы:

### Код состояния: 200

Successful Response

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

NotificationResponse

**Свойства:**

| Свойство       | Тип     | Обязательное | Описание   |
| -------------- | ------- | ------------ | ---------- |
| ` id `         | string  | Да           | Id         |
| ` user_id `    | string  | Да           | User Id    |
| ` title `      | string  | Да           | Title      |
| ` content `    | string  | Да           | Content    |
| ` created_at ` | string  | Да           | Created At |
| ` is_read `    | boolean | Да           | Is Read    |

### Код состояния: 403

No access to notification

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

ErrorResponse

**Свойства:**

| Свойство   | Тип    | Обязательное | Описание |
| ---------- | ------ | ------------ | -------- |
| ` detail ` | string | Да           | Detail   |

### Код состояния: 422

Validation Error

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

HTTPValidationError

**Свойства:**

| Свойство   | Тип   | Обязательное | Описание |
| ---------- | ----- | ------------ | -------- |
| ` detail ` | array | Нет          | Detail   |

## DELETE

\[notifications\]

Delete Notification

### path

| Имя                 | Тип    | Обязательный | Формат |
| ------------------- | ------ | ------------ | ------ |
| ` notification_id ` | string | Да           | uuid   |

### header

| Имя             | Тип    | Обязательный | Формат |
| --------------- | ------ | ------------ | ------ |
| ` app-user-id ` | string | Да           | uuid   |

## Ответы:

### Код состояния: 204

Notification was deleted

### Код состояния: 403

No access to notification

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

ErrorResponse

**Свойства:**

| Свойство   | Тип    | Обязательное | Описание |
| ---------- | ------ | ------------ | -------- |
| ` detail ` | string | Да           | Detail   |

### Код состояния: 422

Validation Error

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

HTTPValidationError

**Свойства:**

| Свойство   | Тип   | Обязательное | Описание |
| ---------- | ----- | ------------ | -------- |
| ` detail ` | array | Нет          | Detail   |

## PATCH

\[notifications\]

Read Notification

### path

| Имя                 | Тип    | Обязательный | Формат |
| ------------------- | ------ | ------------ | ------ |
| ` notification_id ` | string | Да           | uuid   |

### header

| Имя             | Тип    | Обязательный | Формат |
| --------------- | ------ | ------------ | ------ |
| ` app-user-id ` | string | Да           | uuid   |

## Ответы:

### Код состояния: 200

Successful Response

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

NotificationResponse

**Свойства:**

| Свойство       | Тип     | Обязательное | Описание   |
| -------------- | ------- | ------------ | ---------- |
| ` id `         | string  | Да           | Id         |
| ` user_id `    | string  | Да           | User Id    |
| ` title `      | string  | Да           | Title      |
| ` content `    | string  | Да           | Content    |
| ` created_at ` | string  | Да           | Created At |
| ` is_read `    | boolean | Да           | Is Read    |

### Код состояния: 403

No access to notification

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

ErrorResponse

**Свойства:**

| Свойство   | Тип    | Обязательное | Описание |
| ---------- | ------ | ------------ | -------- |
| ` detail ` | string | Да           | Detail   |

### Код состояния: 422

Validation Error

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

HTTPValidationError

**Свойства:**

| Свойство   | Тип   | Обязательное | Описание |
| ---------- | ----- | ------------ | -------- |
| ` detail ` | array | Нет          | Detail   |

