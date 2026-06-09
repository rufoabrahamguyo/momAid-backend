# 🔐 Authentication & Identity API

This module handles user onboarding, security, and profile customization for the MumAid platform.

---

## 🚀 Authentication Flow

1. **Register**: Create an account (default status: inactive).
2. **Verify**: Submit the OTP sent to your email to activate the account.
3. **Login**: Exchange credentials for JWT access and refresh tokens.
4. **Authorize**: Include the access token in the header of all protected requests.

---

## 1. Register User

Create a new account. An OTP will be sent to the provided email address for verification.

**Endpoint:** `POST api/auth/v1/register/`

### Request Body

```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "role": "mother"
}
```

> Supported roles: `mother`, `partner`

### Response

```json
{
  "detail": "User created. Please activate your account.",
  "status": 201
}
```

---

## 2. Verify OTP

Activate the account using the 6-digit code sent via email.

**Endpoint:** `POST api/auth/v1/verify/token/`

### Request Body

```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

### Response

```json
{
  "detail": "Email verified successfully",
  "status": 200,
  "access": "access_token_string",
  "refresh": "refresh_token_string",
}
```

---

## 3. Login (Standard)

Authenticate and receive JWT tokens for session management.

**Endpoint:** `POST api/auth/v1/login/`

### Request Body

```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

### Response

```json
{
  "access": "access_token_string",
  "refresh": "refresh_token_string",
  "status": 200
}
```

<!-- ---

## 4. Google Social Login

Authenticate using a Google ID token provided by the frontend integration.

**Endpoint:** `POST api/auth/v1/google/social-login/`

### Request Body

```json
{
  "token": "GOOGLE_ID_TOKEN_HERE"
}
```

### Response

```json
{
  "access": "access_token_here",
  "refresh": "refresh_token_here",
  "status": 200
}
``` -->

---

## 4. Token Management

### Refresh Token

Generate a new access token when the current one expires.

**Endpoint:** `POST api/auth/v1/login/refresh/token/`

```json
{
  "refresh": "your_refresh_token"
}
```

### 5. Logout

Blacklist the refresh token to end the session securely.

**Endpoint:** `POST api/auth/v1/logout/`

```json
{
  "refresh": "your_refresh_token"
}
```

**Success Response:** `205 Reset Content`

---

## 6. User Profile

### Get Current User (whoami)

Retrieve details of the currently authenticated user.

**Endpoint:** `GET api/auth/v1/whoami/`

**Header:**

```
Authorization: Bearer <access_token>
```

### Response

```json
{
  "public_id": "9a8be513-245e-454a-972f-91d2436e658f",
    "email": "test1@gmail.com",
    "username": "test1",
    "image": "https://res.cloudinary.com/deynddrmf/image/upload/v1/profile_pics/user_1",
    "role": "mother",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false,
    "joined_at": "2026-05-02T17:11:37.204474Z",
    "updated_at": "2026-05-14T11:43:20.367781Z",
    "profile": {
        "public_id": "4244a0e8-7984-44e7-a706-8febc8641580",
        "user": "9a8be513-245e-454a-972f-91d2436e658f",
        "baby_due_date": "2026-12-25",
        "baby_birth_date": "2026-12-24",
        "partner": null
    }
}
```

---

### 7. Upload Profile Image

Update the user's avatar. Images are stored and served via Cloudinary.

**Endpoint:** `PUT api/auth/v1/profile/image/`

* **Method:** PUT
* **Header:** Authorization: Bearer <access_token>
* **Type:** multipart/form-data

### Fields

* `profile_pic`: (File) - .jpg, .jpeg, or .png (Max 10MB)

### Success Response

```json
{
  "detail": "Profile image updated",
  "url": "https://res.cloudinary.com/momaid/image/upload/v123/profile.jpg",
  "status": 200
}
```

---

## 7. Verify OTP

Resend the otp back to the user.

**Endpoint:** `POST api/auth/v1/resend-otp`

### Request Body

```json
{
  "email": "user@example.com",
}
```

### Response

```json
{
  "detail": "If the email exists, a code has been sent.",
}
```

---

## 8. Update User Profile

Update user profile by passing in email/username or both.

**Endpoint:** `POST api/auth/v1/update/user/`

### Request Body
```json
{
  "email": "",
  "username": ""
}
```

### Response
```json
{
  "detail": "User Profile updated successfully"
}
```

---

## 9. Update Mother Profile

Update mother profile. 

**Endpoint:** `POST api/auth/v1/update/mother/`

### Request Body
```json
{
  "baby_due_date": "2026-12-25",
  "baby_birth_date": "2026-12-24",
}
```

### Response
```json
{
  "detail": "Mother Profile updated successfully"
}
```

---

## ⚠️ Common Error Codes

| Status | Detail                                           |
| ------ | ------------------------------------------------ |
| 400    | Missing required fields or invalid OTP           |
| 401    | Token expired, invalid, or incorrect credentials |
| 412>=530  | Image file size too large (exceeds 10MB limit)   |
