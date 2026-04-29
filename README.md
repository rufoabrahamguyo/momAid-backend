# momAid Backend API

Welcome to the **momAid Backend API**.

This document provides an overview of available endpoints and how to use them.

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

## 4. Refresh Token

**Endpoint:**

```
POST api/auth/v1/login/refresh/token/
```

### Request Body

```json
{
  "refresh": "refresh_token_here"
}
```

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

### Responses

```json
205 Reset Content
```

```json
{
  "detail": "Refresh token required"
}
```

---

## 6. Get Current User

**Endpoint:**

```
GET api/auth/v1/whoami/
```

### Response (example)

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "role": "mother",
  "is_active": true
}
```

---

## 7. Upload Profile Image

**Endpoint:**

```
PUT api/auth/v1/profile/image/
```

### Headers

```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

### Request Body (form-data)

```
profile_pic: <image_file>
```

### Validation Rules

* Max size: 10MB
* Allowed formats: jpg, jpeg, png

### Success Response

```json
{
  "detail": "Profile image updated",
  "url": "https://res.cloudinary.com/..."
}
```

### Error Responses

```json
{
  "detail": "No image provided"
}
```

```json
{
  "detail": "Image must be <= 10MB"
}
```

```json
{
  "detail": "Only jpg, jpeg, png allowed"
}
```
---

## 8. Login User Via Google

**Endpoint:**

```
POST api/auth/v1/google/social-login/
```

### Request Body

```json
{
  "token": "ID_TOKEN_FROM_FRONTEND"
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

# Feeds & Video Features (NEW)

## 9. Upload User Video

**Endpoint:**

```
POST api/feeds/v1/upload/video/
```

### Headers

```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

### Request Body (form-data)

```
video_file_path: <video_file>
attributes[title]: "My video title"
attributes[description]: "Optional description"
```

### Notes

* Video is uploaded to Cloudinary
* Duration and size are auto-extracted

### Success Response

```json
{
  "detail": "Video uploaded successfully",
  "data": {
    "id": 1,
    "video_file": "https://res.cloudinary.com/...",
    "user": "user_id",
    "attributes": {
      "id": 10,
      "title": "My video title",
      "description": "Optional description",
      "duration": 12.5,
      "size": 1048576,
      "created_at": "2026-04-26T...",
      "updated_at": "2026-04-26T..."
    }
  }
}
```

### Error Response

```json
{
  "error": "Upload failed"
}
```

---

## 10. Get All Videos (Feed)

**Endpoint:**

```
GET api/feeds/v1/videos/all/
```

### Response

```json
[
  {
    "id": 1,
    "video_file": "https://...",
    "user": "user_id",
    "attributes": {
      "title": "...",
      "description": "...",
      "duration": 10,
      "size": 12345,
      "created_at": "..."
    }
  }
]
```

---

## 11. Get User Specific Videos

**Endpoint:**

```
GET api/feeds/v1/user/specific/videos/
```

### Response

```json
[
  {
    "id": 1,
    "video_file": "https://...",
    "user": "user_id",
    "attributes": {
      "title": "...",
      "description": "...",
      "duration": 10,
      "size": 12345,
      "created_at": "..."
    }
  }
]
```

# 💬 COMMENT SYSTEM

The system supports:

* Comments on videos
* 1-level replies only
* Backend-controlled user assignment
* Nested comment retrieval

---

## Comment Model Rules

* user is set by backend (`request.user`)
* video is set via URL
* replies only allowed one level deep
* no self-assigned user or video from frontend

---

## Create Comment

```
POST api/feeds/v1/videos/<video_id>/comments/create/
```

### Body

```json
{
  "content": "Nice video!"
}
```

---

## Get Video Comments

```
GET api/feeds/v1/videos/<video_id>/comments/
```

### Response

```json
[
  {
    "id": 1,
    "content": "Nice video",
    "created_at": "...",
    "replies": [
      {
        "id": 2,
        "content": "I agree",
        "created_at": "..."
      }
    ]
  }
]
```

---

## Reply to Comment

```
POST api/feeds/v1/comments/<comment_id>/reply/
```

### Body

```json
{
  "content": "Reply message"
}
```

### Rules

* Only 1-level replies allowed
* Replies to replies are blocked

---

# Authentication Header

```
Authorization: Bearer <access_token>
```

---


# Status Codes

* `200` → Success
* `201` → Created
* `205` → Logout success
* `400` → Bad request
* `401` → Unauthorized
* `403` → Forbidden

---

# API Modules Overview

* Authentication → `/api/auth/`
* Feeds (Videos) → `/api/feeds/`
* Opportunities → `/api/opportunities/`
* Remedies → `/api/remedies/`
* Exercises → `/api/exercises/`
* Milk Support → `/api/milk/`
* Partner → `/api/partner/`
* Healthcare → `/api/healthcare/`

---

# API Docs

Swagger UI available at:

```
/api/docs/
```
