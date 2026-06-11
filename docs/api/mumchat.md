# MumChat API

Purpose: document anonymous community posts and nested replies implemented by `apps.mumchat`.

Base path:

```txt
/api/mumchat/
```

Protected endpoints require:

```http
Authorization: Bearer <access_token>
```

Public endpoints:

```txt
GET /api/mumchat/v1/posts/
GET /api/mumchat/v1/posts/<post_id>/
```

## Privacy Model

MumChat stores ownership as a salted hash, not as serialized user identity.

Implementation:

```txt
core.renderers.hash_user_identity(request.user.id)
```

Stored fields:

```txt
MumChatPost.author_hash
MumChatReply.author_replier_hash
```

The API never returns `author_hash`, `author_replier_hash`, user id, email, username, or profile data from MumChat serializers. Ownership checks for update and delete compare the authenticated user's hash with the stored hash.

`ANONYMOUS_SALT` must remain stable per environment. Changing it prevents existing posts from matching their original authors.

## Post Response Shape

`MumChatPostSerializer` returns:

```json
{
  "public_id": "1cfa39e2-7f25-4e71-91e2-b9b4f8c71f57",
  "title": "Feeling anxious today",
  "content": "Has anyone else felt this way in the third trimester?",
  "reply_count": 1,
  "replies": [
    {
      "public_id": "8f7c8f10-8e6b-4504-944f-85c0b2c23235",
      "content": "I understand how you feel.",
      "parent_reply": null,
      "is_root_reply": true,
      "children": [],
      "created_at": "2026-06-05T15:00:00Z"
    }
  ],
  "created_at": "2026-06-05T14:28:00Z",
  "updated_at": "2026-06-05T14:28:00Z"
}
```

Fields:

| Field | Type | Notes |
| --- | --- | --- |
| `public_id` | UUID | Use this as `<post_id>` in URLs. |
| `title` | string or null | Unique model field, max 255 characters, validated non-blank when supplied. |
| `content` | string or null | Max 300 characters, validated non-blank when supplied. |
| `reply_count` | integer | Count of all replies related to the post. |
| `replies` | array | Root replies only; nested replies are under `children`. |
| `created_at` | ISO datetime | Read-only. |
| `updated_at` | ISO datetime | Read-only. |

## Pagination

List endpoints use `MumChatPagination`:

```txt
page_size = 20
page_size_query_param = page_size
max_page_size = 100
```

Response:

```json
{
  "count": 42,
  "next": "http://localhost:8000/api/mumchat/v1/posts/?page=2",
  "previous": null,
  "results": []
}
```

Posts are ordered by `MumChatPost.Meta.ordering = ["-created_at"]`.

## Endpoint Summary

| Method | Path | Auth | Behavior |
| --- | --- | --- | --- |
| `GET` | `/api/mumchat/v1/posts/` | No | List all posts. |
| `POST` | `/api/mumchat/v1/posts/create/` | Yes | Create a post owned by the authenticated user's anonymous hash. |
| `GET` | `/api/mumchat/v1/posts/me/` | Yes | List posts owned by the authenticated user's anonymous hash. |
| `GET` | `/api/mumchat/v1/posts/<post_id>/` | No | Retrieve one post by `public_id`. |
| `DELETE` | `/api/mumchat/v1/posts/<post_id>/delete/` | Yes | Delete a post owned by the authenticated user. |
| `PATCH` | `/api/mumchat/v1/posts/<post_id>/update/` | Yes | Partially update a post owned by the authenticated user. |
| `POST` | `/api/mumchat/v1/posts/<post_id>/replies/create/` | Yes | Create a root reply or nested reply. |

## List Posts

```txt
GET /api/mumchat/v1/posts/
```

Auth: public.

Success: `200 OK`

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "public_id": "1cfa39e2-7f25-4e71-91e2-b9b4f8c71f57",
      "title": "Feeling anxious today",
      "content": "Has anyone else felt this way in the third trimester?",
      "reply_count": 0,
      "replies": [],
      "created_at": "2026-06-05T14:28:00Z",
      "updated_at": "2026-06-05T14:28:00Z"
    },
    {
      "public_id": "3b9c589c-ec7a-4d12-a40d-21a5c157fe10",
      "title": "Hospital bag tips",
      "content": "What did you actually use from your hospital bag?",
      "reply_count": 0,
      "replies": [],
      "created_at": "2026-06-04T10:15:00Z",
      "updated_at": "2026-06-04T10:15:00Z"
    }
  ]
}
```

There is no search, category filter, image field, author display field, like count, or sort parameter.

## Create Post

```txt
POST /api/mumchat/v1/posts/create/
```

Auth: required.

Request:

```json
{
  "title": "Feeling anxious today",
  "content": "Has anyone else felt this way in the third trimester?"
}
```

Accepted fields:

| Field | Type | Required by model | Serializer validation |
| --- | --- | --- | --- |
| `title` | string | No | If supplied, must not be blank. Max 255. Unique. |
| `content` | string | No | If supplied, must not be blank. Max 300. |

Success: `201 Created`

```json
{
  "detail": "Post created successfully."
}
```

The create response does not include the created post. Refetch the list or detail view if the client needs the new `public_id`.

Validation error: `400 Bad Request`

```json
{
  "status": "error",
  "message": "Validation failed.",
  "errors": {
    "content": [
      "Content cannot be blank."
    ]
  }
}
```

Duplicate title error:

```json
{
  "status": "error",
  "message": "Validation failed.",
  "errors": {
    "title": [
      "mum chat post with this title already exists."
    ]
  }
}
```

## List My Posts

```txt
GET /api/mumchat/v1/posts/me/
```

Auth: required.

Success: `200 OK`

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "public_id": "1cfa39e2-7f25-4e71-91e2-b9b4f8c71f57",
      "title": "Feeling anxious today",
      "content": "Has anyone else felt this way in the third trimester?",
      "reply_count": 0,
      "replies": [],
      "created_at": "2026-06-05T14:28:00Z",
      "updated_at": "2026-06-05T14:28:00Z"
    }
  ]
}
```

The route is declared before `/api/mumchat/v1/posts/<post_id>/`, so `me` is not shadowed by the detail route.

## Get Post Detail

```txt
GET /api/mumchat/v1/posts/<post_id>/
```

Auth: public.

`post_id` is `MumChatPost.public_id`.

Success: `200 OK`

```json
{
  "public_id": "1cfa39e2-7f25-4e71-91e2-b9b4f8c71f57",
  "title": "Feeling anxious today",
  "content": "Has anyone else felt this way in the third trimester?",
  "reply_count": 0,
  "replies": [],
  "created_at": "2026-06-05T14:28:00Z",
  "updated_at": "2026-06-05T14:28:00Z"
}
```

Missing post: `404 Not Found`

```json
{
  "status": "error",
  "message": "Not found.",
  "errors": null
}
```

## Update Post

```txt
PATCH /api/mumchat/v1/posts/<post_id>/update/
```

Auth: required. The authenticated user must own the post.

Request:

```json
{
  "title": "Feeling calmer today",
  "content": "Thank you for the advice yesterday."
}
```

Partial updates are accepted:

```json
{
  "content": "Thank you for the advice yesterday."
}
```

Success: `200 OK`

```json
{
  "detail": "Post updated successfully."
}
```

Missing post or not owner: `404 Not Found`

```json
{
  "status": "error",
  "message": "Not found.",
  "errors": null
}
```

The backend intentionally does not distinguish between missing content and content owned by another user.

## Delete Post

```txt
DELETE /api/mumchat/v1/posts/<post_id>/delete/
```

Auth: required. The authenticated user must own the post.

Success: `204 No Content`

```txt
No response body
```

Missing post or not owner: `404 Not Found`

```json
{
  "status": "error",
  "message": "Not found.",
  "errors": null
}
```

## Create Reply

Create a root reply to a post or a nested reply to another reply.

```txt
POST /api/mumchat/v1/posts/<post_id>/replies/create/
```

Auth: required.

Root reply request:

```json
{
  "content": "I understand how you feel."
}
```

Nested reply request:

```json
{
  "content": "Thank you for sharing.",
  "parent_id": "8f7c8f10-8e6b-4504-944f-85c0b2c23235"
}
```

`parent_id` is read manually from `request.data` and must be a `MumChatReply.public_id` for the same post.

Success: `201 Created`

```json
{
  "reply": "Thank you for sharing.",
  "posted_at": "2026-06-05T15:10:00Z"
}
```

Blank reply: `400 Bad Request`

```json
{
  "status": "error",
  "message": "Validation failed.",
  "errors": {
    "content": [
      "Reply cannot be blank."
    ]
  }
}
```

Maximum depth exceeded: `400 Bad Request`

```json
{
  "detail": "Maximum reply depth of 5 reached."
}
```

Reply rules:

- Root replies have `parent_reply: null`.
- Nested replies are returned recursively in `children`.
- Maximum nesting depth is 5 as enforced by `MumChatReplyCreateView.MAX_REPLY_DEPTH`.
- Reply ownership is anonymous and not exposed.

## Rate Limits

MumChat uses the global limits and `UserRateThrottle` on create post and create reply.

| Caller | Limit |
| --- | --- |
| anonymous list/detail | `20/minute` |
| authenticated requests | `1000/day` |

Rate-limit response: `429 Too Many Requests`

```json
{
  "detail": "Too many requests.",
  "retry_after": 42
}
```
