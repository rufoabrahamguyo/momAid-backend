# Frontend integration: API map and gaps

Base URL: see project `README.md` (local vs production). All app routes use the `Authorization: Bearer <access_token>` header unless noted.

## Implemented for mobile / web clients

### User profile (any authenticated role)

| Method | Path | Notes |
|--------|------|--------|
| `GET` | `/api/auth/v1/profile/` | Current user JSON (includes `avatar` URL or `null`, `mother_profile` or `null`). |
| `PATCH` | `/api/auth/v1/profile/` | Update nested mother fields and/or profile photo. |

**JSON body (mothers only for nested fields):** `Content-Type: application/json`

```json
{
  "mother_profile": {
    "baby_due_date": "2025-12-01",
    "baby_birth_date": null,
    "push_notifications_enabled": true
  }
}
```

Only the mother role may send `mother_profile`; other roles get a 400 on that key.

**Profile photo — upload:** `Content-Type: multipart/form-data` with one file field:

- `avatar` — image file; max size **5 MB** (enforced in the API).

**Profile photo — remove:** JSON body:

```json
{ "avatar": null }
```

**`GET` whoami:** `/api/auth/v1/whoami/` also returns the same user shape (including `avatar`) for active users.

### Opportunities — interest and contact preference

- `POST` an opportunity’s interest action can include `contact_preference` (string, e.g. email / phone / app), stored per interest and used in admin notification and CSV export. See the opportunities API in `README.md`.

