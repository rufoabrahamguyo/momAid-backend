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

---

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
```

---

## 5. Token Management

### Refresh Token

Generate a new access token when the current one expires.

**Endpoint:** `POST api/auth/v1/login/refresh/token/`

```json
{
  "refresh": "your_refresh_token"
}
```

### Logout

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
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "role": "mother",
  "is_active": true,
  "status": 200
}
```

---

### Upload Profile Image

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

## ⚠️ Common Error Codes

| Status | Detail                                           |
| ------ | ------------------------------------------------ |
| 400    | Missing required fields or invalid OTP           |
| 401    | Token expired, invalid, or incorrect credentials |
| 412>=530  | Image file size too large (exceeds 10MB limit)   |
