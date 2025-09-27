# API Документация

## /api/auth/register

### POST

\[auth\]

Регистрация пользователя

#### Тело запроса

**Content-Type:** `application/json`

**Тип:** `object`

**Название:** `UserRegisterRequest`

| Свойство   | Тип    | Обязательное | Описание |
| ---------- | ------ | ------------ | -------- |
| `email`    | string | Да           | Email    |
| `name`     | string | Да           | Name     |
| `password` | string | Да           | Password |

#### Ответы

**Код состояния: 201**
User was registered

**Content-Type:** `application/json`

**Тип:** `object`

**Название:** `UserResponse`

| Свойство        | Тип    | Обязательное | Описание      |
| --------------- | ------ | ------------ | ------------- |
| `email`         | string | Да           | Email         |
| `id`            | string | Да           | Id            |
| `registered_at` | string | Да           | Registered At |

**Код состояния: 409**
User already exists

**Content-Type:** `application/json`

**Тип:** `object`

**Название:** `ErrorResponse`

| Свойство | Тип    | Обязательное | Описание |
| -------- | ------ | ------------ | -------- |
| `detail` | string | Да           | Detail   |

**Код состояния: 422**
Validation Error

**Content-Type:** `application/json`

**Тип:** `object`

**Название:** `HTTPValidationError`

| Свойство | Тип   | Обязательное | Описание |
| -------- | ----- | ------------ | -------- |
| `detail` | array | Нет          | Detail   |

---

## /api/auth/login

### POST

\[auth\]

Аутентификация пользователя, выдача access (в теле ответа) и refresh токенов (в cookies).

#### Тело запроса

**Content-Type:** `application/x-www-form-urlencoded`

**Тип:** `object`

**Название:** `Body_login_api_auth_login_post`

| Свойство        | Тип    | Обязательное | Описание |
| --------------- | ------ | ------------ | -------- |
| `grant_type`    | string | null         | Нет      | Grant Type    |
| `username`      | string | Да           | Username |
| `password`      | string | Да           | Password |
| `scope`         | string | Нет          | Scope    |
| `client_id`     | string | null         | Нет      | Client Id     |
| `client_secret` | string | null         | Нет      | Client Secret |

#### Ответы

**Код состояния: 200**
Successful Response

**Content-Type:** `application/json`

**Тип:** `object`

**Название:** `TokenResponse`

| Свойство       | Тип    | Обязательное | Описание     |
| -------------- | ------ | ------------ | ------------ |
| `access_token` | string | Да           | Access Token |
| `token_type`   | string | Да           | Token Type   |

**HTTP-only cookie**

| Название        | Тип    | Обязательное | Описание                         |
| --------------- | ------ | ------------ | -------------------------------- |
| `refresh_token` | string | Да           | Кука для обновления access_token |

> Cookie `refresh_token` доступна только браузеру и не видна в JSON-ответе.

**Код состояния: 401**
Incorrect username or password

**Content-Type:** `application/json`

**Тип:** `object`

**Название:** `ErrorResponse`

| Свойство | Тип    | Обязательное | Описание |
| -------- | ------ | ------------ | -------- |
| `detail` | string | Да           | Detail   |

**Код состояния: 422**
Validation Error

**Content-Type:** `application/json`

**Тип:** `object`

**Название:** `HTTPValidationError`

| Свойство | Тип   | Обязательное | Описание |
| -------- | ----- | ------------ | -------- |
| `detail` | array | Нет          | Detail   |

---

## /api/auth/refresh

### POST

\[auth\]

Обновление access токена при помощи refresh токена, также происходит ротация refresh токена.

#### Ответы

**Код состояния: 200**
Successful Response

**Content-Type:** `application/json`

**Тип:** `object`

**Название:** `TokenResponse`

| Свойство       | Тип    | Обязательное | Описание           |
| -------------- | ------ | ------------ | ------------------ |
| `access_token` | string | Да           | Новый Access Token |
| `token_type`   | string | Да           | Token Type         |


**HTTP-only cookie**

| Название        | Тип    | Обязательное | Описание            |
| --------------- | ------ | ------------ | ------------------- |
| `refresh_token` | string | Да           | Новый Refresh token |

> Cookie `refresh_token` доступна только браузеру и не видна в JSON-ответе.

---

## /api/auth/logout

### POST

\[auth\]

Logout

> При вызове эндпоинта `refresh_token` cookie удаляется с клиента.

#### Ответы

**Код состояния: 204**
Successful Response

**Content-Type:** `application/json`

**HTTP-only кука, удаляемая сервером:**

| Название        | Тип    | Обязательное | Описание                    |
| --------------- | ------ | ------------ | --------------------------- |
| `refresh_token` | string | Нет          | Cookie удаляется при logout |

---

## /.well-known/jwks.json

### GET

\[jwks\]

Получения публичных ключей для валидации JWT токенов

#### Ответы

**Код состояния: 200**
Successful Response

**Content-Type:** `application/json`

**Тип:** `object`

**Название:** `ResponseGetJwksWellKnownJwksJsonGet`

**Структура ответа:**

| Свойство | Тип   | Обязательное | Описание                  |
| -------- | ----- | ------------ | ------------------------- |
| `keys`   | array | Да           | Список JWK ключей сервера |

**Пример одного элемента в массиве `keys`:**

| Свойство | Тип    | Обязательное | Описание                    |
| -------- | ------ | ------------ | --------------------------- |
| `kty`    | string | Да           | Тип ключа (например, RSA)   |
| `use`    | string | Да           | Использование ключа (`sig`) |
| `alg`    | string | Да           | Алгоритм подписи (`RS256`)  |
| `kid`    | string | Да           | Идентификатор ключа         |
| `n`      | string | Да           | Модуль RSA в base64url      |
| `e`      | string | Да           | Экспонента RSA в base64url  |

> Все ключи находятся в массиве `keys`, который может содержать несколько ключей.
