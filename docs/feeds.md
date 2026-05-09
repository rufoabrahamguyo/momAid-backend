# 🎬 Feeds & Community API

This module handles video content creation, social feeds, and the interactive community comment system.

---

## 📹 Video Management

Videos are uploaded and stored via Cloudinary. Metadata like duration and file size are automatically processed by the backend.

---

## 1. Upload Video

Upload a video file with custom attributes.

**Endpoint:** `POST api/feeds/v1/upload/video/`

**Header:**

```txt
Authorization: Bearer <access_token>
```

**Type:** `multipart/form-data`

### Request Body

| Field                   | Type   | Description                  |
| ----------------------- | ------ | ---------------------------- |
| video_file_path         | File   | The video file to upload     |
| attributes[title]       | String | Title of the video           |
| attributes[description] | String | (Optional) Brief description |

### Success Response

```json
{
  "detail": "Video uploaded successfully",
  "data": {
    "public_id": "public_id string will appear",
    "video_file": "https://res.cloudinary.com/...",
    "created_at": "2026-04-26T...",
    "user": "user_uuid",
    "attributes": {
      "public_id": "public_id string will appear",
      "title": "My video title",
      "duration": 12.5,
      "size": 1048576,
      ...
    }
  },
  "status": 201
}
```

---

## 2. Get Global Feed

Retrieve all videos uploaded across the platform using Infinite Scroll (Cursor Pagination).

**Endpoint:** `GET api/feeds/v1/videos/all/`

### Success Response

```json
{
  "next": "http://api.site.com/api/.../?cursor=cD0yMDI2LTA1...",
  "previous": null,
  "results": [
    {
      "public_id": "public_id string will appear",
      "video_file": "https://res.cloudinary.com/...",
      "user": {
        "public_id": "public_id string will appear",
        "username": "dev_user"
        ...
      },
      "attributes": {
        "public_id": "public_id string will appear",
        "title": "My video title",
        "duration": 12.5
        ...
      }
    }
  ]
}
```

---

## 3. Get My Videos

Retrieve videos uploaded by the authenticated user using Cursor Pagination.

**Endpoint:** `GET api/feeds/v1/user/specific/videos/`

**Header:**

```txt
Authorization: Bearer <access_token>
```

### Success Response

```json
{
  "next": "http://api.site.com/api/.../?cursor=cD0yMDI2LTA1...",
  "previous": null,
  "results": [
    {
      "public_id": "public_id string will appear",
      "video_file": "https://res.cloudinary.com/...",
      "user": {
        "public_id": "public_id string will appear",
        "username": "my_account"
        ...
      },
      "attributes": {
        "public_id": "public_id string will appear",
        "title": "Backend API Walkthrough",
        "duration": 20.4
        ...
      }
    }
  ]
}
```

---

## 💬 Comment System

The system supports threaded conversations with a focus on simplicity.

* **1-Level Nesting:** Users can comment on a video and reply to a comment.
* **Anti-Spam Protection:** Replies to existing replies are blocked.
* **Paginated Comments:** Optimized using Limit/Offset Pagination.

---

## 4. Create Video Comment

Post a top-level comment on a specific video.

**Endpoint:** `POST api/feeds/v1/videos/<video_id>/comments/create/`

### Request Body

```json
{
  "content": "This was so helpful, thank you!"
}
```

---

## 5. Reply to a Comment

Reply to an existing comment.

**Endpoint:** `POST api/feeds/v1/comments/<comment_id>/reply/`

### Request Body

```json
{
  "content": "I totally agree with this point."
}
```

---

## 6. Get Video Comments

Retrieve paginated top-level comments and their nested replies.

**Endpoint:** `GET api/feeds/v1/videos/<video_id>/comments/`

### Success Response

```json
{
  "count": 42,
  "next": "http://api.site.com/api/.../?limit=20&offset=20",
  "previous": null,
  "results": [
    {
      "public_id": "public_id string will appear",
      "content": "Great advice!",
      "user": {
        "username": "user_name",
        "avatar": "https://cdn.site.com/avatar.jpg"
      },
      "created_at": "2026-04-26T...",
      "replies": [
        {
          "public_id": "public_id string will appear",
          "content": "Thanks!",
          "user": {
            "public_id": "public_id string will appear",
            "username": "author_name"
            ...
          },
          "created_at": "2026-04-26T..."
        }
      ]
    }
  ]
}
```

---

## 🚀 Performance & Architecture

* **N+1 Query Optimized:** Uses `select_related` and `prefetch_related` to minimize database hits.
* **Stable Cursor Pagination:** Video feeds are ordered by `created_at DESC`.
* **Efficient Comment Loading:** Replies are prefetched for faster nested serialization.
* **Cloudinary Integration:** Media URLs are automatically generated as absolute URLs.
* **Context-Aware Serializers:** Request context is passed into serializers for dynamic response handling.

---

## ⚠️ Feed Error Codes

| Status | Detail                                                |
| ------ | ----------------------------------------------------- |
| 400    | Invalid data or multipart/form-data formatting issues |
| 403    | Only 1-level deep replies are permitted               |
| 404    | The requested Video or Comment ID does not exist      |
| 500    | Database error or Cloudinary upload timeout           |
