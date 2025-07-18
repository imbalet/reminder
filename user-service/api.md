



# `POST /api/delivery/`


**Описание**: Create Method
## Параметры:

### Header параметры:

|Имя|Тип|Обязательный|Формат|
| :---: | :---: | :---: | :---: |
|`app-user-id`|string|Да|uuid|

## Тело запроса:

### Content-Type: `application/json`


**Тип**: `object`

**Название**: DeliveryMethodAdd

**Свойства:**
|Свойство|Тип|Обязательное|Описание|
| :---: | :---: | :---: | :---: |
|`delivery_method`|string, Enum['telegram', 'email']|Да|DeliveryMethodEnum|
|`contact_value`|string \| null|Нет|Контакт (для email)|
|`confirm_code`|string \| null|Нет|Код подтверждения (для telegram)|

## Ответы:

### Код состояния: 201


**Описание**: Delivery method created
#### Content-Type: `application/json`


**Тип**: `object`

**Название**: DeliveryMethodResponse

**Свойства:**
|Свойство|Тип|Обязательное|Описание|
| :---: | :---: | :---: | :---: |
|`delivery_method`|string, Enum['telegram', 'email']|Да|DeliveryMethodEnum|
|`contact_value`|string \| null|Нет|Contact Value|
|`confirm_code`|string \| null|Нет|Confirm Code|
|`id`|string|Да|Id|
|`user_id`|string|Да|User Id|

### Код состояния: 400


**Описание**: Invalid or expired Telegram confirmation code
#### Content-Type: `application/json`


**Тип**: `object`

**Название**: ErrorResponse

**Свойства:**
|Свойство|Тип|Обязательное|Описание|
| :---: | :---: | :---: | :---: |
|`detail`|string|Да|Detail|

### Код состояния: 409


**Описание**: Delivery method already exists
#### Content-Type: `application/json`


**Тип**: `object`

**Название**: ErrorResponse

**Свойства:**
|Свойство|Тип|Обязательное|Описание|
| :---: | :---: | :---: | :---: |
|`detail`|string|Да|Detail|

### Код состояния: 422


**Описание**: Validation Error
#### Content-Type: `application/json`


**Тип**: `object`

**Название**: HTTPValidationError

**Свойства:**
|Свойство|Тип|Обязательное|Описание|
| :---: | :---: | :---: | :---: |
|`detail`|array|Нет|Detail|


---

# `GET /api/delivery/internal/users/{user_id}`


**Описание**: Get All User Methods
> Только для внутреннего использования. НЕ имеет валидации
## Параметры:

### Path параметры:

|Имя|Тип|Обязательный|Формат|
| :---: | :---: | :---: | :---: |
|`user_id`|string|Да|uuid|

## Ответы:

### Код состояния: 200


**Описание**: Successful Response
#### Content-Type: `application/json`


**Тип**: `array`

**Название**: Response Get All User Methods Api Delivery Internal Users  User Id  Get

**Элементы массива:**

**Тип**: `object`

**Название**: DeliveryMethodResponse

**Свойства:**
|Свойство|Тип|Обязательное|Описание|
| :---: | :---: | :---: | :---: |
|`delivery_method`|string, Enum['telegram', 'email']|Да|DeliveryMethodEnum|
|`contact_value`|string \| null|Нет|Contact Value|
|`confirm_code`|string \| null|Нет|Confirm Code|
|`id`|string|Да|Id|
|`user_id`|string|Да|User Id|

### Код состояния: 422


**Описание**: Validation Error
#### Content-Type: `application/json`


**Тип**: `object`

**Название**: HTTPValidationError

**Свойства:**
|Свойство|Тип|Обязательное|Описание|
| :---: | :---: | :---: | :---: |
|`detail`|array|Нет|Detail|


---

# `GET /api/delivery/my`


**Описание**: Get All Methods
## Параметры:

### Header параметры:

|Имя|Тип|Обязательный|Формат|
| :---: | :---: | :---: | :---: |
|`app-user-id`|string|Да|uuid|

## Ответы:

### Код состояния: 200


**Описание**: Successful Response
#### Content-Type: `application/json`


**Тип**: `array`

**Название**: Response Get All Methods Api Delivery My Get

**Элементы массива:**

**Тип**: `object`

**Название**: DeliveryMethodResponse

**Свойства:**
|Свойство|Тип|Обязательное|Описание|
| :---: | :---: | :---: | :---: |
|`delivery_method`|string, Enum['telegram', 'email']|Да|DeliveryMethodEnum|
|`contact_value`|string \| null|Нет|Contact Value|
|`confirm_code`|string \| null|Нет|Confirm Code|
|`id`|string|Да|Id|
|`user_id`|string|Да|User Id|

### Код состояния: 422


**Описание**: Validation Error
#### Content-Type: `application/json`


**Тип**: `object`

**Название**: HTTPValidationError

**Свойства:**
|Свойство|Тип|Обязательное|Описание|
| :---: | :---: | :---: | :---: |
|`detail`|array|Нет|Detail|


---

# `GET /api/delivery/{method_id}`


**Описание**: Get Method
## Параметры:

### Path параметры:

|Имя|Тип|Обязательный|Формат|
| :---: | :---: | :---: | :---: |
|`method_id`|string|Да|uuid|

### Header параметры:

|Имя|Тип|Обязательный|Формат|
| :---: | :---: | :---: | :---: |
|`app-user-id`|string|Да|uuid|

## Ответы:

### Код состояния: 200


**Описание**: Delivery method created
#### Content-Type: `application/json`


**Тип**: `object`

**Название**: DeliveryMethodResponse

**Свойства:**
|Свойство|Тип|Обязательное|Описание|
| :---: | :---: | :---: | :---: |
|`delivery_method`|string, Enum['telegram', 'email']|Да|DeliveryMethodEnum|
|`contact_value`|string \| null|Нет|Contact Value|
|`confirm_code`|string \| null|Нет|Confirm Code|
|`id`|string|Да|Id|
|`user_id`|string|Да|User Id|

### Код состояния: 403


**Описание**: No access to delivery method
#### Content-Type: `application/json`


**Тип**: `object`

**Название**: ErrorResponse

**Свойства:**
|Свойство|Тип|Обязательное|Описание|
| :---: | :---: | :---: | :---: |
|`detail`|string|Да|Detail|

### Код состояния: 422


**Описание**: Validation Error
#### Content-Type: `application/json`


**Тип**: `object`

**Название**: HTTPValidationError

**Свойства:**
|Свойство|Тип|Обязательное|Описание|
| :---: | :---: | :---: | :---: |
|`detail`|array|Нет|Detail|

# `DELETE /api/delivery/{method_id}`


**Описание**: Delete Method
## Параметры:

### Path параметры:

|Имя|Тип|Обязательный|Формат|
| :---: | :---: | :---: | :---: |
|`method_id`|string|Да|uuid|

### Header параметры:

|Имя|Тип|Обязательный|Формат|
| :---: | :---: | :---: | :---: |
|`app-user-id`|string|Да|uuid|

## Ответы:

### Код состояния: 204


**Описание**: Successful Response
### Код состояния: 403


**Описание**: No access to delivery method
#### Content-Type: `application/json`


**Тип**: `object`

**Название**: ErrorResponse

**Свойства:**
|Свойство|Тип|Обязательное|Описание|
| :---: | :---: | :---: | :---: |
|`detail`|string|Да|Detail|

### Код состояния: 422


**Описание**: Validation Error
#### Content-Type: `application/json`


**Тип**: `object`

**Название**: HTTPValidationError

**Свойства:**
|Свойство|Тип|Обязательное|Описание|
| :---: | :---: | :---: | :---: |
|`detail`|array|Нет|Detail|


---

# `GET /api/notification/my`


**Описание**: Get All Notifications
## Параметры:

### Header параметры:

|Имя|Тип|Обязательный|Формат|
| :---: | :---: | :---: | :---: |
|`app-user-id`|string|Да|uuid|

## Ответы:

### Код состояния: 200


**Описание**: Successful Response
#### Content-Type: `application/json`


**Тип**: `array`

**Название**: Response Get All Notifications Api Notification My Get

**Элементы массива:**

**Тип**: `object`

**Название**: NotificationResponse

**Свойства:**
|Свойство|Тип|Обязательное|Описание|
| :---: | :---: | :---: | :---: |
|`user_id`|string|Да|User Id|
|`title`|string|Да|Title|
|`content`|string|Да|Content|
|`id`|string|Да|Id|
|`created_at`|string|Да|Created At|
|`is_read`|boolean|Да|Is Read|

### Код состояния: 422


**Описание**: Validation Error
#### Content-Type: `application/json`


**Тип**: `object`

**Название**: HTTPValidationError

**Свойства:**
|Свойство|Тип|Обязательное|Описание|
| :---: | :---: | :---: | :---: |
|`detail`|array|Нет|Detail|


---

# `GET /api/notification/{notification_id}`


**Описание**: Get Notification
## Параметры:

### Path параметры:

|Имя|Тип|Обязательный|Формат|
| :---: | :---: | :---: | :---: |
|`notification_id`|string|Да|uuid|

### Header параметры:

|Имя|Тип|Обязательный|Формат|
| :---: | :---: | :---: | :---: |
|`app-user-id`|string|Да|uuid|

## Ответы:

### Код состояния: 200


**Описание**: Successful Response
#### Content-Type: `application/json`


**Тип**: `object`

**Название**: NotificationResponse

**Свойства:**
|Свойство|Тип|Обязательное|Описание|
| :---: | :---: | :---: | :---: |
|`user_id`|string|Да|User Id|
|`title`|string|Да|Title|
|`content`|string|Да|Content|
|`id`|string|Да|Id|
|`created_at`|string|Да|Created At|
|`is_read`|boolean|Да|Is Read|

### Код состояния: 403


**Описание**: No access to notification
#### Content-Type: `application/json`


**Тип**: `object`

**Название**: ErrorResponse

**Свойства:**
|Свойство|Тип|Обязательное|Описание|
| :---: | :---: | :---: | :---: |
|`detail`|string|Да|Detail|

### Код состояния: 422


**Описание**: Validation Error
#### Content-Type: `application/json`


**Тип**: `object`

**Название**: HTTPValidationError

**Свойства:**
|Свойство|Тип|Обязательное|Описание|
| :---: | :---: | :---: | :---: |
|`detail`|array|Нет|Detail|

# `PATCH /api/notification/{notification_id}`


**Описание**: Read Notification
## Параметры:

### Path параметры:

|Имя|Тип|Обязательный|Формат|
| :---: | :---: | :---: | :---: |
|`notification_id`|string|Да|uuid|

### Header параметры:

|Имя|Тип|Обязательный|Формат|
| :---: | :---: | :---: | :---: |
|`app-user-id`|string|Да|uuid|

## Ответы:

### Код состояния: 200


**Описание**: Successful Response
#### Content-Type: `application/json`


**Тип**: `object`

**Название**: NotificationResponse

**Свойства:**
|Свойство|Тип|Обязательное|Описание|
| :---: | :---: | :---: | :---: |
|`user_id`|string|Да|User Id|
|`title`|string|Да|Title|
|`content`|string|Да|Content|
|`id`|string|Да|Id|
|`created_at`|string|Да|Created At|
|`is_read`|boolean|Да|Is Read|

### Код состояния: 403


**Описание**: No access to notification
#### Content-Type: `application/json`


**Тип**: `object`

**Название**: ErrorResponse

**Свойства:**
|Свойство|Тип|Обязательное|Описание|
| :---: | :---: | :---: | :---: |
|`detail`|string|Да|Detail|

### Код состояния: 422


**Описание**: Validation Error
#### Content-Type: `application/json`


**Тип**: `object`

**Название**: HTTPValidationError

**Свойства:**
|Свойство|Тип|Обязательное|Описание|
| :---: | :---: | :---: | :---: |
|`detail`|array|Нет|Detail|


---
