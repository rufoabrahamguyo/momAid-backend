# 🤝 Partner & Linking API

This module facilitates the connection between a Mother profile and a Partner profile. Once linked, partners receive curated tasks based on the baby's current age.

---

## 🔗 The Linking Process

1. Mother generates a 6-digit unique invite code.
2. Partner enters this code to link their account.
3. System enables task tracking and collaborative features.

---

## 🎟 Invite & Linking

### 1. Generate Invite Code

Mothers use this to invite a partner to link accounts. Existing codes for the user are cleared upon a new request.

**Endpoint:** `POST api/partner/v1/generate/code/`

**Header:**

```
Authorization: Bearer <mother_access_token>
```

### Response

```json
{
  "code": "AB1234",
  "expires_at": "2026-04-26T15:00:00Z"
}
```

---

### 2. Link Partner Account

Partners use the code provided by the mother to establish the link.

**Endpoint:** `POST api/partner/v1/link/partner/`

**Header:**

```
Authorization: Bearer <partner_access_token>
```

### Request Body

```json
{
  "invite_code": "AB1234"
}
```

### Response

```json
{
  "message": "Successfully linked!",
  "status": 200
}
```

---

## 📋 Partner Tasks

Tasks are automatically filtered based on the `baby_age_weeks` of the linked Mother profile.

---

### 3. List Available Tasks

Retrieve a list of tasks relevant to the current week of the baby.

**Endpoint:** `GET api/partner/v1/list/partner/tasks/`

**Header:**

```
Authorization: Bearer <partner_access_token>
```

### Response Example

```json
[
  {
    "id": 1,
    "title": "Sterilize Bottles",
    "description": "Ensure all feeding equipment is sterilized.",
    "icon": "bottle_icon_url",
    "estimated_time": "15 mins",
    "why_it_matters": "Protects baby's immune system.",
    "is_recurring": true
  }
]
```

---

### 4. Complete a Task

Mark a specific task as completed.

**Endpoint:** `POST api/partner/v1/<task_id>/complete/`

**Header:**

```
Authorization: Bearer <partner_access_token>
```

### Request Body

```json
{
  "status": "completed",
  "notes": "Did this after the evening feed."
}
```

---

### 5. List Completed Tasks

Retrieve the history of tasks completed by the partner.

**Endpoint:** `GET api/partner/v1/list/completion/tasks/`

**Header:**

```
Authorization: Bearer <partner_access_token>
```

---

## 🛡 Staff Operations

### 6. Create New Task Template

Used by administrators to add tasks to the global database.

**Endpoint:** `POST api/partner/v1/create/partner/tasks/`

**Header:**

```
Authorization: Bearer <staff_access_token>
```

### Request Body

```json
{
  "baby_age_weeks_min": 1,
  "baby_age_weeks_max": 4,
  "title": "Newborn Care",
  "description": "Specific steps for the first month.",
  "estimated_time": "30 mins",
  "order": 1
}
```

---

## ⚠️ Partner Error Codes

| Status | Detail                                                   |
| ------ | -------------------------------------------------------- |
| 400    | Code expired or mother's current week calculation failed |
| 401    | Unauthorized (e.g., non-staff trying to create tasks)    |
| 403    | Forbidden: Only users wit                                |
