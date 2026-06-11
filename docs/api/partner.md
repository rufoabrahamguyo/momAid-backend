# Partner API

Purpose: document partner linking, partner task templates, and partner task completion behavior implemented by `apps.partner`.

Base path:

```txt
/api/partner/
```

All partner endpoints require JWT authentication. Admin endpoints additionally require `IsAdminUser`.

```http
Authorization: Bearer <access_token>
```

## Models And Identifiers

`InviteCode`:

| Field | Type | Notes |
| --- | --- | --- |
| `public_id` | UUID or null | Internal model field; not returned by the generate endpoint. |
| `creator` | User | Mother account that generated the code. |
| `code` | string | Unique 6-character uppercase alphanumeric code. |
| `created_at` | ISO datetime | Creation timestamp. |
| `expires_at` | ISO datetime | Defaults to 2 hours after creation. |

`PartnerTask` serializer fields:

| Field | Type | Notes |
| --- | --- | --- |
| `public_id` | UUID or null | Read-only public identifier. |
| `baby_age_weeks_min` | integer | Inclusive lower week bound. |
| `baby_age_weeks_max` | integer | Inclusive upper week bound. |
| `title` | string | Max 100 characters. |
| `description` | string | Task instructions. |
| `icon` | string | Max 10 characters. |
| `order` | integer | Sort order for admin-managed templates. |
| `is_recurring` | boolean | Whether task can recur conceptually. |
| `estimated_time` | string | Max 20 characters. |
| `why_it_matters` | string or null | Supporting rationale. |

`PartnerTaskCompletion` serializer fields:

| Field | Type | Notes |
| --- | --- | --- |
| `public_id` | UUID or null | Completion public identifier. |
| `status` | string | Defaults to `completed`. |
| `completed_at` | ISO datetime | Creation timestamp. |
| `attrs` | object | Intended nested task data. Current serializer does not set `source="task"`, so this field may be absent or null in practice. |

## Current Runtime Caveats

Two partner endpoints have implementation defects in the current code:

- `POST /api/partner/v1/generate/code/` imports `timezone` from Python's `datetime` module and then calls `timezone.now()`. That raises `AttributeError`; the view catches it and returns `500` with `{"error": "An internal error occurred. Please try again later."}`.
- `GET /api/partner/v1/list/partner/tasks/` calls `mother.get_current_mother_week()`, but `MotherProfile` defines `get_current_pregnancy_week()`. Once a partner is linked, task listing can fail with a server error.

These are implementation issues, not client contract requirements.

## Generate Invite Code

Generate or replace the authenticated user's active invite code.

```txt
POST /api/partner/v1/generate/code/
```

Auth: required.

Intended success: `200 OK`

```json
{
  "code": "AB1234",
  "expires_at": "2026-06-05T16:28:00Z"
}
```

Current failure path: `500 Internal Server Error`

```json
{
  "error": "An internal error occurred. Please try again later."
}
```

## Link Partner

Link the authenticated partner profile to the mother who generated an invite code.

```txt
POST /api/partner/v1/link/partner/
```

Auth: required. The authenticated user must have `partner_profile`.

Request:

```json
{
  "invite_code": "AB1234"
}
```

The backend uppercases and trims `invite_code`.

Success: `200 OK`

```json
{
  "message": "Successfully linked!"
}
```

No partner profile: `404 Not Found`

```json
{
  "detail": "Partner profile not found"
}
```

Expired code: `400 Bad Request`

```json
{
  "error": "Code expired."
}
```

Invalid code: `404 Not Found`

```json
{
  "error": "Invalid code."
}
```

Mother profile missing on invite creator: `404 Not Found`

```json
{
  "detail": "Mother profile not found"
}
```

## Create Partner Task Template

Create a global task template.

```txt
POST /api/partner/v1/create/partner/tasks/
```

Auth: admin only.

Request:

```json
{
  "baby_age_weeks_min": 1,
  "baby_age_weeks_max": 4,
  "title": "Sterilize bottles",
  "description": "Wash and sterilize feeding equipment after use.",
  "icon": "bottle",
  "order": 10,
  "is_recurring": true,
  "estimated_time": "15 min",
  "why_it_matters": "Clean feeding equipment reduces infection risk."
}
```

Success: `201 Created`

```json
{
  "detail": "Resource created successfully"
}
```

Validation error when `baby_age_weeks_min > baby_age_weeks_max`: `400 Bad Request`

```json
{
  "non_field_errors": [
    "Min week cannot be greater than Max week."
  ]
}
```

Non-admin users receive `403 Forbidden`.

## List Partner Tasks

List tasks relevant to the linked mother's current pregnancy week.

```txt
GET /api/partner/v1/list/partner/tasks/
```

Auth: required. The authenticated user must have `partner_profile` and must be linked to a mother.

Intended success: `200 OK`

The endpoint uses `TaskLimitPaginator`.

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "public_id": "6725a9bb-e3dd-444f-b9cf-b9604c54d159",
      "baby_age_weeks_min": 1,
      "baby_age_weeks_max": 4,
      "title": "Sterilize bottles",
      "description": "Wash and sterilize feeding equipment after use.",
      "icon": "bottle",
      "order": 10,
      "is_recurring": true,
      "estimated_time": "15 min",
      "why_it_matters": "Clean feeding equipment reduces infection risk."
    }
  ]
}
```

No partner profile: `404 Not Found`

```json
{
  "detail": "Partner profile not found."
}
```

No linked mother: `400 Bad Request`

```json
{
  "detail": "Link to a mother first"
}
```

Current linked-user failure:

```txt
AttributeError: 'MotherProfile' object has no attribute 'get_current_mother_week'
```

## Complete A Task

Mark a task complete for the authenticated partner.

```txt
POST /api/partner/v1/<int:task_id>/complete/
```

`task_id` is the integer `PartnerTask.id`, not `PartnerTask.public_id`.

Auth: required. The authenticated user must have `role="partner"`.

Request:

```json
{
  "status": "completed",
  "notes": "Completed after the evening feed."
}
```

Success on first completion: `201 Created`

```json
{
  "detail": "Task completed successfully"
}
```

Already completed: `200 OK`

```json
{
  "detail": "Task already marked as completed"
}
```

Missing task: `404 Not Found`

```json
{
  "detail": "Task does not exist"
}
```

Non-partner user: `403 Forbidden`

```json
{
  "detail": "Only partners can complete these tasks"
}
```

## List Completed Tasks

List task completions for the authenticated partner.

```txt
GET /api/partner/v1/list/completion/tasks/
```

Auth: required. The authenticated user must have `role="partner"`.

Success: `200 OK`

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "public_id": "e1ca3a74-0e8e-4201-8912-e3f2d3e3c1ac",
      "status": "completed",
      "completed_at": "2026-06-05T15:30:00Z"
    }
  ]
}
```

Non-partner user: `403 Forbidden`

```json
{
  "detail": "Access denied"
}
```

## List Admin Partner Tasks

List all partner task templates for admin users.

```txt
GET /api/partner/v1/admin/partner/tasks/
```

Auth: admin only.

Success: `200 OK`

Response is a page-number paginated list of `PartnerTaskSerializer` objects.

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "public_id": "6725a9bb-e3dd-444f-b9cf-b9604c54d159",
      "baby_age_weeks_min": 1,
      "baby_age_weeks_max": 4,
      "title": "Sterilize bottles",
      "description": "Wash and sterilize feeding equipment after use.",
      "icon": "bottle",
      "order": 10,
      "is_recurring": true,
      "estimated_time": "15 min",
      "why_it_matters": "Clean feeding equipment reduces infection risk."
    }
  ]
}
```

## Rate Limits

Partner endpoints use the global authenticated user limit:

```txt
user: 1000/day
```

Rate-limit response: `429 Too Many Requests`

```json
{
  "detail": "Too many requests.",
  "retry_after": 42
}
```
