# momAid Backend API

Welcome to the **momAid Backend API**.

This document provides an overview of available endpoints and how to use them.

**Frontend / mobile:** see **[Frontend integration: API map and gaps](docs/FRONTEND_INTEGRATION.md)** (auth profile, avatar upload, opportunities interest + contact preference; remaining gaps: FCM, feeds/video, etc.).

---

## Base URL

```
development: http://localhost:8000/
production: https://momaid-backend.onrender.com/

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

## 4. Google Login (OAuth2)

momAid supports **Google Sign-In** for authentication.

### Endpoint

```
POST api/auth/v1/google/login/
```

### Request Body

```json
none
```

### Response

```json
{
  "access": "jwt_access_token_here",
  "refresh": "jwt_refresh_token_here",
  "email": "user@gmail.com",
  "is_new_user": true
}
```

### Flow Summary

1. User signs in with Google on frontend
2. Frontend receives Google ID token
3. Send token to backend
4. Backend verifies token and returns JWT
5. User is authenticated

---

## 5. Logout User

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

## 6. Get Current User (Who Am I)

**Endpoint:**

```
GET api/auth/v1/whoami/
```

### Request

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
  "avatar": "https://momaid-backend.onrender.com/media/avatars/2026/04/01/photo.png",
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

Use `"avatar": null` when the user has no profile photo. Same fields appear on **`GET api/auth/v1/profile/`** (and **`PATCH`** for updates: JSON for `mother_profile` and for clearing the photo, or `multipart/form-data` with an `avatar` file to upload). Details: [docs/FRONTEND_INTEGRATION.md](docs/FRONTEND_INTEGRATION.md).

---

# Authentication Header

For protected routes:

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

# Tests (local, without Docker DB)

```bash
python manage.py test --settings=mumaid.settings.test
```

This uses SQLite in memory so PostgreSQL (e.g. `POSTGRES_HOST=db`) is not required.

---
