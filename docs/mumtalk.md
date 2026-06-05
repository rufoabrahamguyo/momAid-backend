# MumTalk API

MumTalk is the anonymous community posting feature. A signed-in user can create posts, and the backend stores ownership as a salted `author_hash` instead of exposing the user record. Frontend clients never receive `author_hash`, user id, email, username, or profile data from MumTalk responses.

Base path:

```txt
api/mumtalk/
```

Authentication uses the normal JWT header for protected endpoints:

```txt
Authorization: Bearer <access_token>
```

## Data Model

A MumTalk post returned to the frontend has this shape:

```json
{
  "public_id": "1cfa39e2-7f25-4e71-91e2-b9b4f8c71f57",
  "title": "Feeling anxious today",
  "content": "Has anyone else felt this way in the third trimester?",
  "created_at": "2026-06-05T14:28:00Z",
  "updated_at": "2026-06-05T14:28:00Z"
}
```

Fields:

| Field | Type | Frontend notes |
| --- | --- | --- |
| `public_id` | UUID string | Public post identifier. Use this as `post_id` in detail, update, and delete paths. |
| `title` | string or null | Optional, max 255 characters, currently unique across all MumTalk posts. |
| `content` | string or null | Optional, max 300 characters. |
| `created_at` | ISO datetime string | Read-only. |
| `updated_at` | ISO datetime string | Read-only. |

Important current constraints:

- The create/update serializer accepts only `title` and `content` from the frontend.
- `public_id`, `created_at`, and `updated_at` are read-only.
- `author_hash` is backend-only and is never returned.
- There are no likes, comments, categories, images, author display names, or search filters in the current MumTalk API.

## Pagination

List endpoints use page-number pagination.

Defaults:

- `page_size`: `20`
- `max_page_size`: `100`

Query params:

| Param | Example | Meaning |
| --- | --- | --- |
| `page` | `?page=2` | Page number to fetch. |
| `page_size` | `?page_size=50` | Number of posts per page, capped at 100. |

Paginated response shape:

```json
{
  "count": 42,
  "next": "http://api.site.com/api/mumtalk/v1/posts/?page=2",
  "previous": null,
  "results": [
    {
      "public_id": "1cfa39e2-7f25-4e71-91e2-b9b4f8c71f57",
      "title": "Feeling anxious today",
      "content": "Has anyone else felt this way in the third trimester?",
      "created_at": "2026-06-05T14:28:00Z",
      "updated_at": "2026-06-05T14:28:00Z"
    }
  ]
}
```

Posts are ordered newest first by `created_at`.

## Current Paths

| Method | Path | Auth | Current behavior |
| --- | --- | --- | --- |
| `GET` | `api/mumtalk/v1/posts/` | Optional | List all MumTalk posts, newest first, paginated. |
| `POST` | `api/mumtalk/v1/posts/create/` | Required | Create a post for the authenticated user. |
| `GET` | `api/mumtalk/v1/posts/<post_id>/` | Optional | Get one post by `public_id`. |
| `DELETE` | `api/mumtalk/v1/posts/<post_id>/delete/` | Required | Delete one of the authenticated user's own posts. |
| `GET` | `api/mumtalk/v1/posts/me/` | Required | Intended to list the authenticated user's own posts, but currently shadowed by the detail route. See note below. |
| `PUT` | `api/mumtalk/v1/posts/<post_id>/update/` | Required | Update one of the authenticated user's own posts. Partial payloads are accepted. |

Routing note:

`api/mumtalk/v1/posts/me/` is currently declared after `api/mumtalk/v1/posts/<post_id>/`. Because of that order, Django matches `me` as `<post_id>` first. So a frontend call to `GET api/mumtalk/v1/posts/me/` currently behaves like a detail lookup for a post whose `public_id` is `"me"` and will normally return:

```json
{
  "detail": "Post not found."
}
```

Until the route order changes, do not rely on `api/mumtalk/v1/posts/me/` for "my posts" in frontend flows.

## 1. List All Posts

Retrieve all MumTalk posts across the platform.

Endpoint:

```txt
GET api/mumtalk/v1/posts/
```

Auth:

```txt
Optional
```

Query examples:

```txt
GET api/mumtalk/v1/posts/?page=1
GET api/mumtalk/v1/posts/?page=2&page_size=10
```

Success response: `200 OK`

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
      "created_at": "2026-06-05T14:28:00Z",
      "updated_at": "2026-06-05T14:28:00Z"
    },
    {
      "public_id": "3b9c589c-ec7a-4d12-a40d-21a5c157fe10",
      "title": "Hospital bag tips",
      "content": "What did you actually use from your hospital bag?",
      "created_at": "2026-06-04T10:15:00Z",
      "updated_at": "2026-06-04T10:15:00Z"
    }
  ]
}
```

Frontend expectations:

- Use `results` for rendering the feed.
- Use `next` and `previous` for pagination controls or infinite loading.
- There is currently no backend search, filtering, or ordering query support for this endpoint.

## 2. Create Post

Create a new anonymous MumTalk post for the authenticated user.

Endpoint:

```txt
POST api/mumtalk/v1/posts/create/
```

Header:

```txt
Authorization: Bearer <access_token>
```

Request body:

```json
{
  "title": "Feeling anxious today",
  "content": "Has anyone else felt this way in the third trimester?"
}
```

Accepted fields:

| Field | Type | Required by serializer | Notes |
| --- | --- | --- | --- |
| `title` | string | No | Max 255 characters. Must be unique if provided. |
| `content` | string | No | Max 300 characters. |

Success response: `201 Created`

```json
{
  "detail": "Post created successfully."
}
```

Frontend expectations:

- The create response does not include the created post object or `public_id`.
- If the UI needs the new post data immediately, refetch the list after a successful create.
- The backend derives ownership from the JWT user and does not accept an author field.

Possible errors:

`401 Unauthorized` when the token is missing or invalid.

`400 Bad Request` for validation errors, for example a duplicate title or content longer than 300 characters:

```json
{
  "title": [
    "mum talk post with this title already exists."
  ]
}
```

## 3. Get Post Detail

Fetch one MumTalk post by its `public_id`.

Endpoint:

```txt
GET api/mumtalk/v1/posts/<post_id>/
```

Auth:

```txt
Optional
```

Example:

```txt
GET api/mumtalk/v1/posts/1cfa39e2-7f25-4e71-91e2-b9b4f8c71f57/
```

Success response: `200 OK`

```json
{
  "public_id": "1cfa39e2-7f25-4e71-91e2-b9b4f8c71f57",
  "title": "Feeling anxious today",
  "content": "Has anyone else felt this way in the third trimester?",
  "created_at": "2026-06-05T14:28:00Z",
  "updated_at": "2026-06-05T14:28:00Z"
}
```

Not found response: `404 Not Found`

```json
{
  "detail": "Post not found."
}
```

Frontend expectations:

- `post_id` should be the post `public_id` returned from list/detail responses.
- The path converter is currently `str`, but the lookup is against a UUID field. Invalid values will not resolve to a real post.

## 4. Delete Post

Delete one of the authenticated user's own posts.

Endpoint:

```txt
DELETE api/mumtalk/v1/posts/<post_id>/delete/
```

Header:

```txt
Authorization: Bearer <access_token>
```

Success response: `204 No Content`

```txt
No response body
```

Not found or not owner response: `404 Not Found`

```json
{
  "detail": "Post not found or you do not have permission to delete this post."
}
```

Frontend expectations:

- There is no separate `403` for "not my post"; the backend returns `404` for both missing posts and permission mismatch.
- On `204`, remove the post from local UI state or refetch the feed.

## 5. List My Posts

Intended endpoint for listing posts created by the authenticated user.

Endpoint:

```txt
GET api/mumtalk/v1/posts/me/
```

Header:

```txt
Authorization: Bearer <access_token>
```

Intended success response: `200 OK`

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
      "created_at": "2026-06-05T14:28:00Z",
      "updated_at": "2026-06-05T14:28:00Z"
    }
  ]
}
```

Current behavior:

Because of route ordering, this path is currently shadowed by the detail route and will normally return `404` as described in the routing note above.

Frontend expectations:

- Treat this endpoint as unavailable until the backend route order is fixed.
- There is currently no owner marker in the public feed response, so the frontend cannot reliably infer "my posts" from `GET api/mumtalk/v1/posts/`.

## 6. Update Post

Update one of the authenticated user's own posts.

Endpoint:

```txt
PUT api/mumtalk/v1/posts/<post_id>/update/
```

Header:

```txt
Authorization: Bearer <access_token>
```

Request body:

```json
{
  "title": "Feeling calmer today",
  "content": "Thank you for the advice yesterday."
}
```

Partial request bodies are accepted even though the method is `PUT`:

```json
{
  "content": "Thank you for the advice yesterday."
}
```

Success response: `200 OK`

```json
{
  "detail": "Post updated successfully"
}
```

Not found or not owner response: `404 Not Found`

```json
{
  "detail": "Post not found or you do not have permission to edit this post."
}
```

Possible validation error: `400 Bad Request`

```json
{
  "content": [
    "Ensure this field has no more than 300 characters."
  ]
}
```

Frontend expectations:

- The update response does not include the updated post object.
- Refetch detail/list data after a successful update if the UI needs fresh timestamps or updated text.
- There is no separate `PATCH` endpoint right now.

## Rate Limit Headers

MumTalk paths are handled by the global rate limiter. Successful responses may include:

```txt
X-MomAid-Tier: anon
X-MomAid-Limit: 60
X-MomAid-Remaining: 59
```

The tier is usually:

- `anon` for unauthenticated MumTalk requests.
- `user` for authenticated MumTalk requests.

Rate limit response: `429 Too Many Requests`

```json
{
  "detail": "Request limit exceeded for user.",
  "retry_after": 42
}
```

The response may also include:

```txt
X-MomAid-Retry-After: 42
```

## Frontend Implementation Notes

- Use `public_id` everywhere the URL asks for `<post_id>`.
- Show posts as anonymous. The API does not expose author identity or display metadata.
- For create/update/delete, assume success responses are message-only or empty and refetch what the screen needs.
- For edit/delete ownership checks, the backend uses the authenticated user's salted hash. A user can only modify posts created under the same account.
- `title` is currently unique globally. If the product does not want unique titles, the backend model will need to change.
- Empty or missing `title` and `content` may pass serializer validation because both model fields allow `null` and `blank`. Frontend validation should enforce any stricter UX rules needed by the product.
