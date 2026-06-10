# Feeds API

Purpose: document video upload, video listing, comments, replies, and watch-history behavior implemented by `apps.feeds`.

Base path:

```txt
/api/feeds/
```

All feeds endpoints require JWT authentication through the global DRF permission class.

```http
Authorization: Bearer <access_token>
```

## Models And Identifiers

`Video` response fields:

| Field | Type | Notes |
| --- | --- | --- |
| `public_id` | UUID or null | Public identifier. Used by watch-history creation. |
| `video_file` | URL/string or null | Stored through the configured default storage. |
| `user` | integer | Internal Django user id as currently serialized by `VideoSerializer`. |
| `attributes` | object | Nested `VideoAttributesSerializer`. |
| `created_at` | ISO datetime | Creation timestamp. |
| `updated_at` | ISO datetime | Update timestamp. |

`VideoAttributes` response fields:

| Field | Type | Notes |
| --- | --- | --- |
| `public_id` | UUID or null | Public identifier. |
| `title` | string | Max 50 characters. |
| `description` | string | Required by the model. |
| `duration` | float | Read-only; defaults to `0.0`. |
| `size` | integer or null | Read-only. |

Important identifier split:

- Comment endpoints use the integer database `Video.id` and `Comment.id`.
- Watch-history creation uses `Video.public_id` as a UUID.
- Video list responses currently do not expose integer `id`, so a client cannot derive comment paths from list responses without another source of the internal id.

## Upload Video

Upload a video file and create its metadata.

```txt
POST /api/feeds/v1/upload/video/
```

Content type:

```txt
multipart/form-data
```

Form fields:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `video_file_path` | file | Yes | Write-only upload field. |
| `attributes.title` | string | Yes | Nested serializer field. |
| `attributes.description` | string | Yes | Nested serializer field. |

cURL:

```bash
curl -X POST http://localhost:8000/api/feeds/v1/upload/video/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "video_file_path=@./sample.mp4" \
  -F "attributes.title=Morning stretch" \
  -F "attributes.description=Short postpartum movement guide"
```

Success: `201 Created`

```json
{
  "public_id": "0df6a073-50aa-4b82-8f52-fbbd456c868e",
  "video_file": "videos/sample.mp4",
  "user": 12,
  "attributes": {
    "public_id": "4ae93ab8-8f55-44f4-97de-23916c2d1890",
    "title": "Morning stretch",
    "description": "Short postpartum movement guide",
    "duration": 0.0,
    "size": null
  },
  "created_at": "2026-06-05T14:28:00Z",
  "updated_at": "2026-06-05T14:28:00Z"
}
```

Validation error: `400 Bad Request`

```json
{
  "status": "error",
  "message": "Validation failed.",
  "errors": {
    "attributes": [
      "This field is required."
    ]
  }
}
```

## List All Videos

Return the global video feed, newest first.

```txt
GET /api/feeds/v1/videos/all/
```

Success: `200 OK`

The endpoint uses `VideoCursorPaginator`.

```json
{
  "next": "http://localhost:8000/api/feeds/v1/videos/all/?cursor=cD0yMDI2LTA2LTA1KzE0JTNBMjglM0EwMCUyQjAwJTNBMDA%3D",
  "previous": null,
  "results": [
    {
      "public_id": "0df6a073-50aa-4b82-8f52-fbbd456c868e",
      "video_file": "https://res.cloudinary.com/momaid/video/upload/v1/videos/sample.mp4",
      "user": 12,
      "attributes": {
        "public_id": "4ae93ab8-8f55-44f4-97de-23916c2d1890",
        "title": "Morning stretch",
        "description": "Short postpartum movement guide",
        "duration": 180.0,
        "size": 1048576
      },
      "created_at": "2026-06-05T14:28:00Z",
      "updated_at": "2026-06-05T14:28:00Z"
    }
  ]
}
```

Unhandled view errors return:

```json
{
  "detail": "An internal error has occurred."
}
```

with status `500`.

## List My Videos

Return videos uploaded by the authenticated user.

```txt
GET /api/feeds/v1/user/specific/videos/
```

Success: `200 OK`

Response shape is the same as `GET /api/feeds/v1/videos/all/`.

## Create Top-Level Comment

Create a comment on a video.

```txt
POST /api/feeds/v1/videos/<int:video_id>/comments/create/
```

`video_id` is the integer `Video.id`, not `Video.public_id`.

Request:

```json
{
  "content": "This was helpful."
}
```

Success: `201 Created`

```json
{
  "comment": "This was helpful.",
  "posted_at": "2026-06-05T14:30:00Z"
}
```

Missing video: `404 Not Found`

```json
{
  "status": "error",
  "message": "Not found.",
  "errors": null
}
```

## Reply To Comment

Reply to an existing top-level comment.

```txt
POST /api/feeds/v1/comments/<int:comment_id>/reply/
```

`comment_id` is the integer `Comment.id`, not `Comment.public_id`.

Request:

```json
{
  "content": "I agree."
}
```

Success: `201 Created`

```json
{
  "comment": "I agree.",
  "posted_at": "2026-06-05T14:32:00Z"
}
```

Replying to a reply is rejected: `400 Bad Request`

```json
{
  "detail": "Only 1 level replies allowed"
}
```

## List Video Comments

List top-level comments and one level of replies.

```txt
GET /api/feeds/v1/videos/<int:video_id>/comments/
```

Success: `200 OK`

The endpoint uses `CommentLimitPaginator`.

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "public_id": "361d62ab-9f1b-46d5-8df0-cf349d6e4bd5",
      "content": "This was helpful.",
      "created_at": "2026-06-05T14:30:00Z",
      "replies": [
        {
          "public_id": "9d49e7f4-2f83-4d84-94f9-e2fcf17e1d8c",
          "content": "I agree.",
          "created_at": "2026-06-05T14:32:00Z"
        }
      ]
    }
  ]
}
```

The serializer does not include commenter identity.

## Save Watch History

Create or update the authenticated user's watch position for a video.

```txt
POST /api/feeds/v1/history/create/<uuid:video_id>/
```

`video_id` is `Video.public_id`.

Request:

```json
{
  "last_watched_at": 42.5
}
```

Success: `201 Created`

```json
{
  "detail": "Successfully saved video"
}
```

Missing video: `404 Not Found`

```json
{
  "detail": "Video not found"
}
```

`last_watched_at` is stored as a float in seconds. If omitted, the backend stores `0.0`.

## Continue Watching

Return watch-history rows where progress is greater than zero and less than the video's duration.

```txt
GET /api/feeds/v1/history/continue/
```

Success: `200 OK`

The endpoint uses `VideoCursorPaginator`.

```json
{
  "next": null,
  "previous": null,
  "results": [
    {
      "video": {
        "public_id": "0df6a073-50aa-4b82-8f52-fbbd456c868e",
        "video_file": "https://res.cloudinary.com/momaid/video/upload/v1/videos/sample.mp4",
        "attributes": {
          "public_id": "4ae93ab8-8f55-44f4-97de-23916c2d1890",
          "title": "Morning stretch",
          "description": "Short postpartum movement guide",
          "duration": 180.0,
          "size": 1048576
        },
        "created_at": "2026-06-05T14:28:00Z"
      },
      "last_watched_at": 42.5,
      "updated_at": "2026-06-05T14:40:00Z",
      "progress_percentage": 23.61
    }
  ]
}
```

## List Watch History

Return all watch-history rows for the authenticated user.

```txt
GET /api/feeds/v1/history/list/
```

Success: `200 OK`

Response shape is the same as `GET /api/feeds/v1/history/continue/`.

## Rate Limits

Feeds endpoints use the global authenticated user limit unless a path-specific rule matches:

```txt
user: 1000/day
```

Successful responses include:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
```

Limit exceeded: `429 Too Many Requests`

```json
{
  "detail": "Too many requests.",
  "retry_after": 42
}
```
