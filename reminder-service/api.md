# /api/reminders/

## POST

\[reminders\]

Create

### header

| Имя             | Тип    | Обязательный | Формат |
| --------------- | ------ | ------------ | ------ |
| ` app-user-id ` | string | Да           | uuid   |

### Тело запроса:

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

ReminderCreate

**Свойства:**

| Свойство                 | Тип    | Обязательное | Описание             |
| ------------------------ | ------ | ------------ | -------------------- |
| ` title `                | string | Да           | Title                |
| ` content `              | string | Да           | Content              |
| ` remind_date `          | string | Да           | Remind Date          |
| ` delivery_methods_ids ` | array  | Да           | Delivery Methods Ids |

## Ответы:

### Код состояния: 201

Delivery method created

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

ReminderResponse

**Свойства:**

| Свойство             | Тип                                                     | Обязательное | Описание         |
| -------------------- | ------------------------------------------------------- | ------------ | ---------------- |
| ` title `            | string                                                  | Да           | Title            |
| ` content `          | string                                                  | Да           | Content          |
| ` remind_date `      | string                                                  | Да           | Remind Date      |
| ` id `               | string                                                  | Да           | Id               |
| ` user_id `          | string                                                  | Да           | User Id          |
| ` created_at `       | string                                                  | Да           | Created At       |
| ` status `           | string, Enum\['pending', 'sent', 'failed', 'inactive'\] | Да           | Status           |
| ` edited_at `        | string \| null                                          | Да           | Edited At        |
| ` delivery_methods ` | array                                                   | Да           | Delivery Methods |

### Код состояния: 400

Invalid delivery method(s)

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

ReminderResponse

**Свойства:**

| Свойство             | Тип                                                     | Обязательное | Описание         |
| -------------------- | ------------------------------------------------------- | ------------ | ---------------- |
| ` title `            | string                                                  | Да           | Title            |
| ` content `          | string                                                  | Да           | Content          |
| ` remind_date `      | string                                                  | Да           | Remind Date      |
| ` id `               | string                                                  | Да           | Id               |
| ` user_id `          | string                                                  | Да           | User Id          |
| ` created_at `       | string                                                  | Да           | Created At       |
| ` status `           | string, Enum\['pending', 'sent', 'failed', 'inactive'\] | Да           | Status           |
| ` edited_at `        | string \| null                                          | Да           | Edited At        |
| ` delivery_methods ` | array                                                   | Да           | Delivery Methods |

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

# /api/reminders/my

## GET

\[reminders\]

Get My

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

Page\[ReminderResponse\]

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

# /api/reminders/{reminder\_id}

## GET

\[reminders\]

Get By Id

### path

| Имя             | Тип    | Обязательный | Формат |
| --------------- | ------ | ------------ | ------ |
| ` reminder_id ` | string | Да           | uuid   |

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

ReminderResponse

**Свойства:**

| Свойство             | Тип                                                     | Обязательное | Описание         |
| -------------------- | ------------------------------------------------------- | ------------ | ---------------- |
| ` title `            | string                                                  | Да           | Title            |
| ` content `          | string                                                  | Да           | Content          |
| ` remind_date `      | string                                                  | Да           | Remind Date      |
| ` id `               | string                                                  | Да           | Id               |
| ` user_id `          | string                                                  | Да           | User Id          |
| ` created_at `       | string                                                  | Да           | Created At       |
| ` status `           | string, Enum\['pending', 'sent', 'failed', 'inactive'\] | Да           | Status           |
| ` edited_at `        | string \| null                                          | Да           | Edited At        |
| ` delivery_methods ` | array                                                   | Да           | Delivery Methods |

### Код состояния: 403

No access to reminder

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

\[reminders\]

Delete By Id

### path

| Имя             | Тип    | Обязательный | Формат |
| --------------- | ------ | ------------ | ------ |
| ` reminder_id ` | string | Да           | uuid   |

### header

| Имя             | Тип    | Обязательный | Формат |
| --------------- | ------ | ------------ | ------ |
| ` app-user-id ` | string | Да           | uuid   |

## Ответы:

### Код состояния: 204

Successful Response

### Код состояния: 403

No access to reminder

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

\[reminders\]

Edit By Id

### path

| Имя             | Тип    | Обязательный | Формат |
| --------------- | ------ | ------------ | ------ |
| ` reminder_id ` | string | Да           | uuid   |

### header

| Имя             | Тип    | Обязательный | Формат |
| --------------- | ------ | ------------ | ------ |
| ` app-user-id ` | string | Да           | uuid   |

### Тело запроса:

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

ReminderEdit

**Свойства:**

| Свойство                 | Тип            | Обязательное | Описание             |
| ------------------------ | -------------- | ------------ | -------------------- |
| ` title `                | string \| null | Нет          | Title                |
| ` content `              | string \| null | Нет          | Content              |
| ` remind_date `          | string \| null | Нет          | Remind Date          |
| ` delivery_methods_ids ` | array \| null  | Нет          | Delivery Methods Ids |

## Ответы:

### Код состояния: 200

Successful Response

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

ReminderResponse

**Свойства:**

| Свойство             | Тип                                                     | Обязательное | Описание         |
| -------------------- | ------------------------------------------------------- | ------------ | ---------------- |
| ` title `            | string                                                  | Да           | Title            |
| ` content `          | string                                                  | Да           | Content          |
| ` remind_date `      | string                                                  | Да           | Remind Date      |
| ` id `               | string                                                  | Да           | Id               |
| ` user_id `          | string                                                  | Да           | User Id          |
| ` created_at `       | string                                                  | Да           | Created At       |
| ` status `           | string, Enum\['pending', 'sent', 'failed', 'inactive'\] | Да           | Status           |
| ` edited_at `        | string \| null                                          | Да           | Edited At        |
| ` delivery_methods ` | array                                                   | Да           | Delivery Methods |

### Код состояния: 403

No access to reminder

**Content-Type:** ` application/json `

**Тип:** ` object `

**Название:**

ErrorResponse

**Свойства:**

| Свойство   | Тип    | Обязательное | Описание |
| ---------- | ------ | ------------ | -------- |
| ` detail ` | string | Да           | Detail   |

### Код состояния: 400

No access to reminder

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

