# MomAid Architecture

Purpose: explain how the MomAid backend is structured, why the major technical decisions exist, and where engineers should make changes safely.

MomAid is a modular Django REST Framework service deployed as a Dockerized API with PostgreSQL, Redis, Celery, and Cloudinary. The codebase is organized by product domain under `api/apps/` and shared infrastructure under `api/core/`.

## Runtime Topology

Local development runs through `docker-compose.yml`:

```txt
api      Django development server on :8000
db       PostgreSQL 15 on host port 5433
redis    Redis 7 on host port 6380
worker   Celery worker for default, notifications, emails queues
beat     Celery beat using django_celery_beat.schedulers:DatabaseScheduler
mailpit  SMTP capture on :1025 and web UI on :8025
adminer  Database UI on :8080
```

Production uses `docker/Dockerfile.api`, `mumaid.settings.prod`, and Gunicorn via `docker/scripts/start-api.sh`.

Why this shape:

- Django and DRF are appropriate for a CRUD-heavy mobile API with role-based access, serializer validation, admin support, and relational data.
- PostgreSQL is the system of record because account, profile, task, listing, and content ownership relationships are relational and need transactional integrity.
- Redis is used for production cache/session storage, rate limiting state, Celery broker, and Celery result backend. Keeping this in one managed Redis instance minimizes platform complexity on Render.
- Celery isolates email and notification work from request latency. The current production compose file comments worker and beat out until the hosting plan supports additional long-running processes.
- Cloudinary stores user-uploaded media because profile images and feed videos need durable object storage and CDN delivery outside the web container filesystem.

## Request Path

Root routing starts in `api/mumaid/urls.py`:

```txt
/api/auth/        apps.accounts.urls
/api/remedies/    apps.remedies.urls
/api/exercises/   apps.exercises.urls
/api/milk/        apps.milk_support.urls
/api/partner/     apps.partner.urls
/api/healthcare/  apps.healthcare.urls
/api/feeds/       apps.feeds.urls
/api/mumchat/     apps.mumchat.urls
/api/health/      apps.welcome.urls
/api/schema/      drf-spectacular schema
/api/docs/        Swagger UI
```

Middleware order matters:

```txt
SecurityMiddleware
WhiteNoiseMiddleware
CorsMiddleware
SessionMiddleware
CommonMiddleware
CsrfViewMiddleware
core.middleware.ErrorHandlerMiddleware
AuthenticationMiddleware
MessageMiddleware
XFrameOptionsMiddleware
core.middleware.GlobalRateLimiter
```

`GlobalRateLimiter` runs after authentication middleware so it can rate-limit by `request.user.id` for authenticated users and by remote address for anonymous requests.

## Domain Boundaries

`apps.accounts` owns identity:

- `User`
- `MotherProfile`
- `PartnerProfile`
- registration, OTP activation, JWT login/refresh/logout, current user, profile image, profile updates

`apps.partner` owns partner workflows:

- `InviteCode`
- `PartnerTask`
- `PartnerTaskCompletion`
- invite code generation, partner linking, task creation/listing/completion

`apps.feeds` owns video content:

- `Video`
- `VideoAttributes`
- `Comment`
- `VideoHistory`
- video upload, global/user feeds, comments, one-level comment replies, watch history

`apps.mumchat` owns anonymous community posts:

- `MumChatPost`
- `MumChatReply`
- anonymous author hashes, post CRUD, nested replies

`apps.healthcare` owns healthcare utility data:

- `EmergencyContact`
- `Hospital`
- user emergency contacts and nearby hospital lookup

`apps.milk_support` owns milk listing exchange data:

- `MilkListing`
- active listings, nearby search, owner-only delete

`apps.remedies` and `apps.exercises` expose read-only maternal resource catalog data:

- `BabyCondition`
- `Remedy`
- `Exercise`

`apps.opportunities` currently contains commented URL scaffolding and is not mounted.

Why domain apps instead of one large API app:

- Each mobile feature has different ownership and authorization rules. Keeping serializers, views, models, and tests together reduces accidental cross-feature coupling.
- Database migrations stay local to the product area that owns the schema.
- Shared behavior remains in `api/core/`, which keeps domain apps from depending on each other for utility code.

## Identity And Privacy

The custom `accounts.User` uses `email` as `USERNAME_FIELD` and exposes `public_id` as a stable external identifier. Roles are stored as `User.Role`:

```txt
mother
partner
admin
```

Mother and partner-specific fields live in `MotherProfile` and `PartnerProfile` rather than on `User`.

MumChat deliberately does not expose user identity. `core.renderers.hash_user_identity(user_id)` computes a SHA-256 hash from `ANONYMOUS_SALT` and the integer user id. That hash is stored as `MumChatPost.author_hash` and `MumChatReply.author_replier_hash`.

Why this decision:

- Anonymous community posts still need ownership checks for edit/delete.
- Storing a salted deterministic hash allows ownership checks without returning email, username, profile data, or integer user ids through MumChat serializers.
- The salt must be stable for a given environment. Rotating `ANONYMOUS_SALT` invalidates ownership matching for existing MumChat content.

## API Contracts

Global DRF settings in `api/mumaid/settings/base.py` enforce:

```txt
DEFAULT_PERMISSION_CLASSES = IsAuthenticated
DEFAULT_AUTHENTICATION_CLASSES = JWTAuthentication
DEFAULT_RENDERER_CLASSES = JSONRenderer
DEFAULT_PAGINATION_CLASS = core.pagination.StandardResultsPagination
EXCEPTION_HANDLER = core.exceptions.momaid_exception_handler
```

Views that should be public set `AllowAny`; examples include registration, login, OTP verification, OTP resend, MumChat list/detail, and the health check.

The current API does not have one uniform response envelope. DRF exceptions pass through `momaid_exception_handler` as:

```json
{
  "status": "error",
  "message": "Validation failed.",
  "errors": {
    "field": [
      "Error text."
    ]
  }
}
```

Many views return direct bodies such as:

```json
{
  "detail": "Post created successfully."
}
```

Why document the inconsistency instead of hiding it:

- Mobile clients need the current contract, not the intended one.
- Future cleanup can converge these envelopes intentionally and version the client impact.

## Pagination

Default pagination is page-number based:

```txt
page_size = 20
page_size_query_param = page_size
max_page_size = 100
```

Feeds use custom cursor and limit/offset paginators for video lists, video history, comments, and partner tasks. This matches expected mobile behavior:

- video feeds need forward-only infinite scrolling and stable newest-first ordering;
- comments and partner task lists are smaller and fit limit/offset access patterns.

## Rate Limiting

The backend uses DRF throttles and `core.middleware.GlobalRateLimiter`.

Configured rates:

```txt
anon:         20/minute
user:         1000/day
otp_limit:    3/minute
login_limit:  5/minute
auth_limit:   40/day
upload_limit: 5/day
```

Why both layers exist:

- DRF throttles let individual views use scoped controls such as `LoginRateThrottle`, `OtpRateThrottle`, and `UploadRateThrottle`.
- The middleware provides a uniform backstop across routes, including views that do not declare explicit throttle classes.

The middleware uses cache keys shaped as:

```txt
rl:<tier>:<identifier>
```

In production, the cache backend is Redis. In development, it is local memory, so rate-limit state is process-local.

## Storage

Development storage:

- database: PostgreSQL in the `db` container;
- cache: `LocMemCache`;
- media: local filesystem;
- static files: Django staticfiles storage;
- email: Mailpit SMTP.

Production storage:

- database: `DATABASE_URL` through `dj_database_url` with SSL required;
- cache/session/Celery: Redis from `REDIS_URL`;
- media: Cloudinary through `cloudinary_storage.storage.MediaCloudinaryStorage`;
- static files: WhiteNoise compressed manifest storage;
- email: Brevo through `anymail.backends.brevo.EmailBackend`.

Why no local media filesystem in production:

- Render containers are ephemeral.
- Uploaded media must survive deploys and be served efficiently to mobile clients.

## Deployment Lifecycle

`docker/scripts/entrypoint.sh` runs:

```txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear
exec "$@"
```

`docker/scripts/start-api.sh` runs Gunicorn with one worker, two threads, request recycling, and stdout/stderr logs.

Why migrations run in the container entrypoint:

- Render deploys can boot a fresh container with the latest image and apply schema changes before traffic reaches application code.
- This is simple for a single API service. If multiple API replicas are introduced, migration execution should move to a one-off release job to avoid concurrent migration attempts.

## Known Implementation Risks

- `apps.partner.views.ListPartnerTaskView` calls `mother.get_current_mother_week()`, but `MotherProfile` defines `get_current_pregnancy_week()`. The current task-list endpoint can fail until that method call is corrected.
- `apps.healthcare.views.EmergencyTriggerView` references `request.user.phone`, `support_person_phone`, and `ob_phone`, which are not fields on `accounts.User`. The endpoint is mounted but not currently aligned with the user model.
- `api/apps/opportunities/urls.py` is commented out, so opportunities are not part of the live API.
- The error envelope is mixed between normalized DRF exceptions and direct view responses.
- `docs/api/README.md` is the source of truth for current endpoint behavior until the OpenAPI annotations are expanded enough for generated schema to be complete.
