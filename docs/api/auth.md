# Authentication And Profile API

Purpose: document MomAid account creation, OTP activation, JWT session management, and profile endpoints exactly as implemented in `apps.accounts`.

Base path:

```txt
/api/auth/
```

Authentication header for protected endpoints:

```http
Authorization: Bearer <access_token>
```

## Data Model

`accounts.User` fields exposed by `UserSerializer`:

| Field | Type | Notes |
| --- | --- | --- |
| `public_id` | UUID | Public user identifier. |
| `email` | string | Unique login identifier. |
| `username` | string or null | Optional display name. |
| `image` | URL string or null | Secure Cloudinary URL when set. |
| `role` | string | One of `mother`, `partner`, `admin`. |
| `is_active` | boolean | Account active flag. |
| `joined_at` | ISO datetime | Creation timestamp. |
| `updated_at` | ISO datetime | Update timestamp. |
| `profile` | object or null | `MotherProfileSerializer`, `PartnerProfileSerializer`, or null for admin. |

`MotherProfile` response fields:

```json
{
  "public_id": "4244a0e8-7984-44e7-a706-8febc8641580",
  "user": "9a8be513-245e-454a-972f-91d2436e658f",
  "baby_due_date": "2026-12-25",
  "baby_birth_date": null,
  "partner": null,
  "current_pregnancy_week": 10
}
```

`PartnerProfile` response fields:

```json
{
  "public_id": "58aaf586-cd5a-4c7a-a600-49af77b81dd7",
  "user": "9a8be513-245e-454a-972f-91d2436e658f"
}
```

## Register

Create a user and send an activation OTP.

```txt
POST /api/auth/v1/register/
```

Auth: public.

Request:

```json
{
  "email": "mother@example.com",
  "password": "securepassword123",
  "role": "mother"
}
```

Accepted roles:

```txt
mother
partner
admin
```

Validation:

- `email` must be a valid unique email address.
- `password` must be at least 8 characters.
- `role` must be one of `User.Role.choices`.

Success: `201 Created`

```json
{
  "detail": "Registration successful. Check your email for the activation code."
}
```

Duplicate email error: `400 Bad Request`

```json
{
  "status": "error",
  "message": "Validation failed.",
  "errors": {
    "email": [
      "An account with this email already exists."
    ]
  }
}
```

## Verify OTP

Activate an account and issue JWT tokens.

```txt
POST /api/auth/v1/verify/token/
```

Auth: public.

Request:

```json
{
  "email": "mother@example.com",
  "otp": "123456"
}
```

Validation:

- `email` is normalized to lowercase.
- `otp` must be exactly 6 characters.

Success: `200 OK`

```json
{
  "detail": "Account activated.",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Invalid or expired OTP: `401 Unauthorized`

```json
{
  "detail": "Invalid or expired activation code."
}
```

The exact `detail` text comes from `services.activate_user()`.

## Resend OTP

Request a new activation OTP.

```txt
POST /api/auth/v1/resend-otp/
```

Auth: public.

Request:

```json
{
  "email": "mother@example.com"
}
```

Success: `200 OK`

```json
{
  "detail": "If the email exists, a new code has been sent."
}
```

The response does not reveal whether the account exists.

## Login

Issue Simple JWT tokens for an active user.

```txt
POST /api/auth/v1/login/
```

Auth: public.

Request:

```json
{
  "email": "mother@example.com",
  "password": "securepassword123"
}
```

Success: `200 OK`

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Invalid credentials: `401 Unauthorized`

```json
{
  "status": "error",
  "message": "No active account found with the given credentials",
  "errors": null
}
```

## Refresh Token

Rotate a refresh token and issue a new access token.

```txt
POST /api/auth/v1/login/refresh/token/
```

Auth: public.

Request:

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Success: `200 OK`

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Refresh token behavior:

- `ROTATE_REFRESH_TOKENS=True`
- `BLACKLIST_AFTER_ROTATION=True`
- access token lifetime is 120 minutes
- refresh token lifetime is 1 day

## Logout

Blacklist a refresh token.

```txt
POST /api/auth/v1/logout/
```

Auth: required.

Request:

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Success: `204 No Content`

```txt
No response body
```

Missing refresh token: `400 Bad Request`

```json
{
  "detail": "Refresh token required."
}
```

Invalid refresh token: `400 Bad Request`

```json
{
  "detail": "Invalid or expired token."
}
```

## Current User

Return the authenticated user and role-specific profile.

```txt
GET /api/auth/v1/whoami/
```

Auth: required.

Success: `200 OK`

```json
{
  "public_id": "9a8be513-245e-454a-972f-91d2436e658f",
  "email": "mother@example.com",
  "username": "njeri",
  "image": "https://res.cloudinary.com/momaid/image/upload/v1/profile_pics/user_1",
  "role": "mother",
  "is_active": true,
  "joined_at": "2026-05-02T17:11:37.204474Z",
  "updated_at": "2026-05-14T11:43:20.367781Z",
  "profile": {
    "public_id": "4244a0e8-7984-44e7-a706-8febc8641580",
    "user": "9a8be513-245e-454a-972f-91d2436e658f",
    "baby_due_date": "2026-12-25",
    "baby_birth_date": null,
    "partner": null,
    "current_pregnancy_week": 10
  }
}
```

## Update User Profile

Partially update `username` and/or `email`.

```txt
PATCH /api/auth/v1/update/user/
```

Auth: required.

Request:

```json
{
  "username": "njeri",
  "email": "new-email@example.com"
}
```

Success: `200 OK`

The response is the full `UserSerializer` body.

Validation error: `400 Bad Request`

```json
{
  "status": "error",
  "message": "Validation failed.",
  "errors": {
    "email": [
      "Enter a valid email address."
    ]
  }
}
```

## Update Mother Profile

Partially update pregnancy and baby dates for a mother profile.

```txt
PATCH /api/auth/v1/update/mother/
```

Auth: required.

Request:

```json
{
  "baby_due_date": "2026-12-25",
  "baby_birth_date": null
}
```

Success: `200 OK`

```json
{
  "detail": "Profile updated."
}
```

No mother profile: `404 Not Found`

```json
{
  "detail": "Mother profile not found."
}
```

The exact `detail` text comes from `services.update_mother_profile()`.

## Upload Profile Image

Upload or replace the authenticated user's profile image.

```txt
PUT /api/auth/v1/profile/image/
```

Auth: required.

Content type:

```txt
multipart/form-data
```

Form fields:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `profile_pic` | file | Yes | Passed to `services.upload_profile_image()`. |

cURL:

```bash
curl -X PUT http://localhost:8000/api/auth/v1/profile/image/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "profile_pic=@./avatar.jpg"
```

Success: `200 OK`

```json
{
  "detail": "Profile image updated.",
  "url": "https://res.cloudinary.com/momaid/image/upload/v123/profile.jpg"
}
```

Missing file: `400 Bad Request`

```json
{
  "detail": "Image file is required."
}
```

## Rate Limits

Auth routes are limited by both DRF throttles and `GlobalRateLimiter`.

| Path fragment | Scope | Limit |
| --- | --- | --- |
| `register` | `login_limit` | `5/minute` |
| `login` | `login_limit` | `5/minute` |
| `verify` | `otp_limit` | `3/minute` |
| `resend-otp` | `otp_limit` | `3/minute` |
| `profile/image` | `upload_limit` | `5/day` |

Rate-limit response:

```json
{
  "detail": "Too many requests.",
  "retry_after": 42
}
```
