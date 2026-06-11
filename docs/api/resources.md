# Healthcare, Milk Support, Remedies, And Exercises API

Purpose: document the mounted resource APIs that are not part of auth, feeds, MumChat, or partner workflows.

All endpoints in this document require JWT authentication.

```http
Authorization: Bearer <access_token>
```

## Healthcare: Emergency Contacts

Base path:

```txt
/api/healthcare/
```

### List Emergency Contacts

```txt
GET /api/healthcare/emergency-contacts/
```

Success: `200 OK`

```json
[
  {
    "id": 1,
    "user": 12,
    "name": "Amina Otieno",
    "phone": "+254700000001",
    "relationship": "Sister",
    "is_primary": true
  }
]
```

Only contacts owned by the authenticated user are returned.

### Create Emergency Contact

```txt
POST /api/healthcare/emergency-contacts/
```

Request:

```json
{
  "name": "Amina Otieno",
  "phone": "+254700000001",
  "relationship": "Sister",
  "is_primary": true
}
```

Success: `201 Created`

```json
{
  "id": 1,
  "user": 12,
  "name": "Amina Otieno",
  "phone": "+254700000001",
  "relationship": "Sister",
  "is_primary": true
}
```

Validation error: `400 Bad Request`

```json
{
  "status": "error",
  "message": "Validation failed.",
  "errors": {
    "name": [
      "This field is required."
    ]
  }
}
```

### Retrieve, Update, Or Delete Emergency Contact

```txt
GET    /api/healthcare/emergency-contacts/<int:pk>/
PUT    /api/healthcare/emergency-contacts/<int:pk>/
PATCH  /api/healthcare/emergency-contacts/<int:pk>/
DELETE /api/healthcare/emergency-contacts/<int:pk>/
```

The queryset is restricted to `EmergencyContact.objects.filter(user=request.user)`.

Partial update request:

```json
{
  "is_primary": false
}
```

Delete success: `204 No Content`.

Missing contact or contact owned by another user: `404 Not Found`.

## Healthcare: Nearby Hospitals

Return hospitals within a radius of a coordinate.

```txt
GET /api/healthcare/hospitals/nearby/?lat=-1.286389&lng=36.817223&radius_km=25&filters=maternal,pediatric
```

Query parameters:

| Param | Required | Default | Notes |
| --- | --- | --- | --- |
| `lat` | Yes | n/a | Client latitude. |
| `lng` | Yes | n/a | Client longitude. |
| `radius_km` | No | `25` | Maximum distance in kilometers. |
| `filters` | No | empty | Comma-separated: `psychiatric`, `pediatric`, `maternal`. |

Success: `200 OK`

```json
[
  {
    "id": 4,
    "name": "Nairobi Maternal Hospital",
    "address": "Hospital Road, Nairobi",
    "location_lat": "-1.2921000",
    "location_lng": "36.8219000",
    "phone": "+254700000010",
    "has_psychiatric_emergency": false,
    "has_pediatric_emergency": true,
    "has_maternal_emergency": true,
    "distance_km": 0.821
  }
]
```

Missing coordinates: `400 Bad Request`

```json
{
  "error": "lat and lng are required.",
  "detail": "lat and lng are required."
}
```

Invalid coordinates or radius: `400 Bad Request`

```json
{
  "error": "Invalid coordinates or radius.",
  "detail": "Invalid coordinates or radius."
}
```

## Healthcare: Emergency Trigger

```txt
POST /api/healthcare/emergency/
```

Request accepted by `EmergencyTriggerSerializer`:

```json
{
  "location_lat": -1.286389,
  "location_lng": 36.817223
}
```

Current implementation caveat:

`EmergencyTriggerView` references `request.user.phone`, `request.user.support_person_phone`, and `request.user.ob_phone`, but `accounts.User` does not define those fields. The route is mounted, but it is not aligned with the current user model and can fail at runtime before queuing any emergency notification.

## Milk Support

Base path:

```txt
/api/milk/
```

### List Active Milk Listings

```txt
GET /api/milk/listings/
```

Success: `200 OK`

```json
[
  {
    "id": 7,
    "listing_type": "donate",
    "user": 12,
    "quantity_ml": 500,
    "location_lat": "-1.2863890",
    "location_lng": "36.8172230",
    "location_address": "Westlands, Nairobi",
    "expiration_date": "2026-06-15T12:00:00Z",
    "is_active": true,
    "created_at": "2026-06-05T14:28:00Z"
  }
]
```

Nearby search:

```txt
GET /api/milk/listings/?lat=-1.286389&lng=36.817223&radius_km=50
```

Nearby response adds `distance_km`:

```json
[
  {
    "id": 7,
    "listing_type": "donate",
    "user": 12,
    "quantity_ml": 500,
    "location_lat": "-1.2863890",
    "location_lng": "36.8172230",
    "location_address": "Westlands, Nairobi",
    "expiration_date": "2026-06-15T12:00:00Z",
    "is_active": true,
    "created_at": "2026-06-05T14:28:00Z",
    "distance_km": 0.0
  }
]
```

Invalid nearby query: `400 Bad Request`

```json
{
  "error": "Invalid lat, lng, or radius_km.",
  "detail": "Invalid lat, lng, or radius_km."
}
```

### Create Milk Listing

```txt
POST /api/milk/listings/
```

Request:

```json
{
  "listing_type": "donate",
  "quantity_ml": 500,
  "location_lat": -1.286389,
  "location_lng": 36.817223,
  "location_address": "Westlands, Nairobi",
  "expiration_date": "2026-06-15T12:00:00Z",
  "is_active": true
}
```

Valid `listing_type` values:

```txt
donate
need
```

Success: `201 Created`

The create serializer returns the fields accepted by `MilkListingCreateSerializer`.

```json
{
  "listing_type": "donate",
  "quantity_ml": 500,
  "location_lat": "-1.2863890",
  "location_lng": "36.8172230",
  "location_address": "Westlands, Nairobi",
  "expiration_date": "2026-06-15T12:00:00Z",
  "is_active": true
}
```

### Retrieve Or Delete Milk Listing

```txt
GET    /api/milk/listings/<int:pk>/
DELETE /api/milk/listings/<int:pk>/
```

Retrieve success: `200 OK`

```json
{
  "id": 7,
  "listing_type": "donate",
  "user": 12,
  "quantity_ml": 500,
  "location_lat": "-1.2863890",
  "location_lng": "36.8172230",
  "location_address": "Westlands, Nairobi",
  "expiration_date": "2026-06-15T12:00:00Z",
  "is_active": true,
  "created_at": "2026-06-05T14:28:00Z"
}
```

Delete success: `204 No Content`.

Deleting another user's listing: `403 Forbidden`

```json
{
  "status": "error",
  "message": "You can only delete your own listing.",
  "errors": null
}
```

## Remedies

Base path:

```txt
/api/remedies/
```

### List Baby Conditions With Remedies

```txt
GET /api/remedies/conditions/
```

Success: `200 OK`

```json
[
  {
    "id": 1,
    "name": "Colic",
    "icon": "baby",
    "order": 10,
    "remedies": [
      {
        "id": 3,
        "title": "Gentle tummy massage",
        "description": "Use slow clockwise strokes on the baby's abdomen.",
        "duration_minutes": 5,
        "gif_url": "https://example.com/tummy-massage.gif",
        "order": 1
      }
    ]
  }
]
```

The endpoint returns all `BabyCondition` rows ordered by `order`, then `id`, with nested `Remedy` rows ordered by `order`, then `id`.

## Exercises

Base path:

```txt
/api/exercises/
```

### List Exercises

```txt
GET /api/exercises/
```

Success: `200 OK`

```json
[
  {
    "id": 1,
    "title": "Pelvic floor breathing",
    "description": "A guided breathing exercise for postpartum recovery.",
    "video_url": "https://example.com/exercises/pelvic-floor.mp4",
    "thumbnail_url": "https://example.com/exercises/pelvic-floor.jpg",
    "duration_seconds": 120,
    "order": 1
  }
]
```

Exercises are returned in `Exercise.Meta.ordering = ["order", "id"]`.

## Rate Limits

These endpoints use the global authenticated user limit:

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
