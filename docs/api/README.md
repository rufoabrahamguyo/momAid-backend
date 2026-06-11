# MomAid API Reference

Purpose: define the API-wide contract for authentication, request formats, response formats, errors, pagination, and rate limiting across the MomAid backend.

Base URLs:

```txt
Production:  https://momaid-backend.onrender.com/
Local:       http://localhost:8000/
```

Every path in this document is relative to the base URL.

## Authentication

MomAid uses `rest_framework_simplejwt.authentication.JWTAuthentication`.

Authenticated requests must send:

```http
Authorization: Bearer <access_token>
```

JWT token policy:

| Token | Lifetime | Behavior |
| --- | ---: | --- |
| `access` | 120 minutes | Sent on API requests. |
| `refresh` | 1 day | Rotates on refresh. |
| rotated refresh token | 1 day | Previous refresh token is blacklisted after rotation. |

Public endpoints explicitly set `AllowAny`; all other views inherit the global `IsAuthenticated` permission unless they override it.

## Content Types

JSON endpoints accept:

```http
Content-Type: application/json
```

Upload endpoints accept:

```http
Content-Type: multipart/form-data
```

The current upload endpoints are:

```txt
PUT  /api/auth/v1/profile/image/
POST /api/feeds/v1/upload/video/
```

## Error Contract

The DRF exception handler normalizes framework exceptions into:

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

Several API views also return direct response bodies instead of raising DRF exceptions. Those bodies currently use `detail`, `error`, or `message`:

```json
{
  "detail": "Refresh token required."
}
```

```json
{
  "error": "Invalid code."
}
```

Clients should treat HTTP status as authoritative and read `errors`, `detail`, `error`, or `message` defensively until the backend has a single response envelope.

Common statuses:

| Status | Meaning in this codebase |
| ---: | --- |
| `200` | Read, login, update, idempotent completion, or invite-code success. |
| `201` | Registration, create, upload, comment, reply, history save, or task creation success. |
| `204` | Logout or delete success with no response body. |
| `400` | Validation failure or invalid request state. |
| `401` | Missing/invalid JWT or invalid OTP activation. |
| `403` | Authenticated user does not satisfy the role or ownership rule. |
| `404` | Object not found, profile not found, or ownership-concealing not-found response. |
| `429` | Global or DRF throttle limit exceeded. |
| `500` | Unhandled server error. |
| `503` | Redis quota exhaustion maintenance response from middleware. |

## Rate Limiting

MomAid has two rate-limiting layers:

1. DRF throttle classes configured in `REST_FRAMEWORK`.
2. `core.middleware.GlobalRateLimiter`, which applies to all non-exempt paths.

Configured rates:

| Scope | Limit | Applies to |
| --- | --- | --- |
| `anon` | `20/minute` | Unauthenticated requests outside special paths. |
| `user` | `1000/day` | Authenticated requests outside special paths. |
| `otp_limit` | `3/minute` | Paths containing `resend-otp` or `verify`. |
| `login_limit` | `5/minute` | Paths containing `login` or `register`. |
| `auth_limit` | `40/day` | Available DRF scope; not currently assigned directly by a view. |
| `upload_limit` | `5/day` | Paths containing `profile/image`; feeds video upload relies on the global user limit. |

Exempt prefixes:

```txt
/admin/
/static/
/media/
/api/docs/
/api/schema/
```

Successful responses from the middleware include:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
```

Rate-limit response:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 42
```

```json
{
  "detail": "Too many requests.",
  "retry_after": 42
}
```

## Pagination

Default page-number pagination:

```json
{
  "count": 42,
  "next": "http://localhost:8000/api/mumchat/v1/posts/?page=2",
  "previous": null,
  "results": []
}
```

Default query parameters:

| Param | Default | Max | Used by |
| --- | ---: | ---: | --- |
| `page` | `1` | n/a | Page-number endpoints. |
| `page_size` | `20` | `100` | `core.pagination.StandardResultsPagination`, MumChat. |
| `limit` | `10` | `50` | Feed comments through `CommentLimitPaginator`. |
| `limit` | `10` | `20` | Partner tasks through `TaskLimitPaginator`. |
| `offset` | `0` | n/a | Feed comments and partner task pagination. |
| `cursor` | n/a | n/a | Feed video/history cursor pagination; page size is `10`. |

## Endpoint Inventory

Health:

| Method | Path | Auth |
| --- | --- | --- |
| `GET` | `/api/health/` | No |

Success response:

```json
{
  "detail": "API is up."
}
```

Auth and profile:

| Method | Path | Auth |
| --- | --- | --- |
| `POST` | `/api/auth/v1/register/` | No |
| `POST` | `/api/auth/v1/login/` | No |
| `POST` | `/api/auth/v1/login/refresh/token/` | No |
| `POST` | `/api/auth/v1/logout/` | Yes |
| `POST` | `/api/auth/v1/verify/token/` | No |
| `POST` | `/api/auth/v1/resend-otp/` | No |
| `GET` | `/api/auth/v1/whoami/` | Yes |
| `PUT` | `/api/auth/v1/profile/image/` | Yes |
| `PATCH` | `/api/auth/v1/update/user/` | Yes |
| `PATCH` | `/api/auth/v1/update/mother/` | Yes |

Feeds:

| Method | Path | Auth |
| --- | --- | --- |
| `POST` | `/api/feeds/v1/upload/video/` | Yes |
| `GET` | `/api/feeds/v1/user/specific/videos/` | Yes |
| `GET` | `/api/feeds/v1/videos/all/` | Yes |
| `GET` | `/api/feeds/v1/videos/<int:video_id>/comments/` | Yes |
| `POST` | `/api/feeds/v1/videos/<int:video_id>/comments/create/` | Yes |
| `POST` | `/api/feeds/v1/comments/<int:comment_id>/reply/` | Yes |
| `POST` | `/api/feeds/v1/history/create/<uuid:video_id>/` | Yes |
| `GET` | `/api/feeds/v1/history/continue/` | Yes |
| `GET` | `/api/feeds/v1/history/list/` | Yes |

MumChat:

| Method | Path | Auth |
| --- | --- | --- |
| `GET` | `/api/mumchat/v1/posts/` | No |
| `POST` | `/api/mumchat/v1/posts/create/` | Yes |
| `GET` | `/api/mumchat/v1/posts/me/` | Yes |
| `GET` | `/api/mumchat/v1/posts/<str:post_id>/` | No |
| `DELETE` | `/api/mumchat/v1/posts/<str:post_id>/delete/` | Yes |
| `PATCH` | `/api/mumchat/v1/posts/<str:post_id>/update/` | Yes |
| `POST` | `/api/mumchat/v1/posts/<str:post_id>/replies/create/` | Yes |

Partner:

| Method | Path | Auth |
| --- | --- | --- |
| `POST` | `/api/partner/v1/generate/code/` | Yes |
| `POST` | `/api/partner/v1/link/partner/` | Yes |
| `POST` | `/api/partner/v1/create/partner/tasks/` | Admin |
| `GET` | `/api/partner/v1/list/partner/tasks/` | Yes |
| `GET` | `/api/partner/v1/list/completion/tasks/` | Partner |
| `POST` | `/api/partner/v1/<int:task_id>/complete/` | Partner |
| `GET` | `/api/partner/v1/admin/partner/tasks/` | Admin |

Healthcare:

| Method | Path | Auth |
| --- | --- | --- |
| `GET` | `/api/healthcare/emergency-contacts/` | Yes |
| `POST` | `/api/healthcare/emergency-contacts/` | Yes |
| `GET` | `/api/healthcare/emergency-contacts/<int:pk>/` | Yes, owner |
| `PUT` | `/api/healthcare/emergency-contacts/<int:pk>/` | Yes, owner |
| `PATCH` | `/api/healthcare/emergency-contacts/<int:pk>/` | Yes, owner |
| `DELETE` | `/api/healthcare/emergency-contacts/<int:pk>/` | Yes, owner |
| `GET` | `/api/healthcare/hospitals/nearby/` | Yes |
| `POST` | `/api/healthcare/emergency/` | Yes; current implementation references undefined `User` fields. |

Milk support:

| Method | Path | Auth |
| --- | --- | --- |
| `GET` | `/api/milk/listings/` | Yes |
| `POST` | `/api/milk/listings/` | Yes |
| `GET` | `/api/milk/listings/<int:pk>/` | Yes |
| `DELETE` | `/api/milk/listings/<int:pk>/` | Yes, owner |

Maternal resources:

| Method | Path | Auth |
| --- | --- | --- |
| `GET` | `/api/remedies/conditions/` | Yes |
| `GET` | `/api/exercises/` | Yes |

Opportunities has model/view scaffolding, but `api/apps/opportunities/urls.py` is commented out. No opportunity routes are currently mounted by `api/mumaid/urls.py`.
