# momAid Backend API

Welcome to the **momAid Backend API**.

This document provides an overview of available endpoints and how to use them.

> ⚠️ Please read carefully before integrating.

---

## Base URL

```
http://localhost:8000/
```

---

# Authentication Flow Overview

1. Register user
2. Verify OTP
3. Login user
4. Use access token for protected routes
5. Logout when done

---

# API Endpoints

## 1. Register User

**Endpoint:**

```
POST api/auth/v1/register/
```

### Request Body

```json
{
  "email": "youremail@example.com",
  "password": "your_password",
  "role": "mother"
}
```

### Response

```json
{
  "detail": "User created. Please activate your account."
}
```

---

## 2. Verify OTP

**Endpoint:**

```
POST api/auth/v1/verify/token/
```

### Request Body

```json
{
  "email": "youremail@example.com",
  "otp": "123456"
}
```

### Response

```json
{
  "detail": "Email verified successfully"
}
```

---

## 3. Login User

**Endpoint:**

```
POST api/auth/v1/login/
```

### Request Body

```json
{
  "email": "youremail@example.com",
  "password": "your_password"
}
```

### Response

```json
{
  "access": "access_token_here",
  "refresh": "refresh_token_here"
}
```

---

## 4. Logout User

**Endpoint:**

```
POST api/auth/v1/logout/
```

### Request Body

```json
{
  "refresh": "refresh_token_here"
}
```

### Response

```json
{
  "status": 205
}
```

---

## 5. Get Current User (Who Am I)

**Endpoint:**

```
GET api/auth/v1/whoami/
```

### Request Body

None (requires authentication)

### Response

```json
{
  "id": "dfbe66d7-44c7-451a-9e27-a9c538f2b82f",
  "email": "user@example.com",
  "role": "mother",
  "is_active": true,
  "joined_at": "2026-04-22T21:59:12.707219Z",
  "updated_at": "2026-04-22T22:00:05.824922Z",
  "mother_profile": {
    "id": 6,
    "baby_due_date": null,
    "baby_birth_date": null,
    "push_notifications_enabled": true,
    "user": "dfbe66d7-44c7-451a-9e27-a9c538f2b82f",
    "partner": null
  }
}
```

---

# Notes

* All protected endpoints require JWT authentication.
* Include the token in headers:

```
Authorization: Bearer <access_token>
```

---

# Status Codes

* `200` → Success
* `201` → Created
* `205` → Reset/Logout success
* `400` → Bad request
* `401` → Unauthorized
* `403` → Forbidden

---

# Author
This README was created and authored by **Rufo Abraham.**