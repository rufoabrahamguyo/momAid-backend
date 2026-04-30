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

```
Authorization: Bearer <access_token>
```

**Type:** multipart/form-data

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
    "id": 1,
    "video_file": "https://res.cloudinary.com/...",
    "user": "user_uuid",
    "attributes": {
      "title": "My video title",
      "duration": 12.5,
      "size": 1048576,
      "created_at": "2026-04-26T..."
    }
  },
  "status": 201
}
```

---

## 2. Get Global Feed

Retrieve all videos uploaded across the platform.

**Endpoint:** `GET api/feeds/v1/videos/all/`

---

## 3. Get My Videos

Retrieve videos uploaded by the authenticated user.

**Endpoint:** `GET api/feeds/v1/user/specific/videos/`

**Header:**

```
Authorization: Bearer <access_token>
```

---

## 💬 Comment System

The system supports threaded conversations with a focus on simplicity.

* **1-Level Nesting:** You can comment on a video and reply to a comment.
* **Anti-Spam:** Replies to existing replies are blocked.

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

Retrieve all comments and their nested replies for a specific video.

**Endpoint:** `GET api/feeds/v1/videos/<video_id>/comments/`

### Response

```json
[
  {
    "id": 10,
    "content": "Great advice!",
    "user": "user_name",
    "created_at": "2026-04-26T...",
    "replies": [
      {
        "id": 11,
        "content": "Thanks for the support!",
        "user": "author_name",
        "created_at": "2026-04-26T..."
      }
    ]
  }
]
```

---

## ⚠️ Feed Error Codes

| Status | Detail                                                       |
| ------ | ------------------------------------------------------------ |
| 400    | Upload failed or invalid comment content                     |
| 403    | Forbidden: Attempting to reply to a reply (nested > 1 level) |
| 404    | Video or Comment ID not found                                |
