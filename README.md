# MomAid Backend

Purpose: give engineers enough operational and architectural context to run, test, modify, and deploy the MomAid API without reading the whole repository first.

MomAid is a Django REST Framework backend for a maternal health mobile product. It serves account onboarding, JWT authentication, maternal profile data, partner linking and tasks, video feeds, anonymous MumChat posts, healthcare resources, remedies, exercises, and breast milk support listings.

Production base URL:

```txt
https://momaid-backend.onrender.com/
```

Local base URL:

```txt
http://localhost:8000/
```

OpenAPI schema and Swagger UI are exposed at:

```txt
GET /api/schema/
GET /api/docs/
```

## Local Setup

Prerequisites: Docker, Docker Compose, and a shell with access to this repository.

Run locally in four commands:

```bash
git clone git@github.com:rufoabrahamguyo/momAid-backend.git
cd momAid-backend
cp .env.example .env
docker compose up --build
```

The API runs on `http://localhost:8000/`. Mailpit runs on `http://localhost:8025/`. Adminer runs on `http://localhost:8080/`.

The Compose stack starts PostgreSQL, Redis, the Django API, a Celery worker, Celery beat, Mailpit, and Adminer. The API container runs migrations through `docker/scripts/entrypoint.sh` before starting `python manage.py runserver 0.0.0.0:8000`.

Required local environment keys:

```env
SECRET_KEY=local-development-secret
POSTGRES_DB=momaid
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
REDIS_URL=redis://redis:6379/0
CLOUDINARY_CLOUD_NAME=<cloudinary-cloud-name>
CLOUDINARY_CLOUD_API_KEY=<cloudinary-api-key>
CLOUDINARY_CLOUD_API_SECRET=<cloudinary-api-secret>
ANONYMOUS_SALT=<stable-local-salt>
```

Cloudinary keys are read at Django settings import time. Use real development credentials or the server will fail before requests are served.

## Project Structure

```txt
api/apps/
  accounts/        Custom User, MotherProfile, PartnerProfile, registration, OTP, JWT profile APIs.
  feeds/           Video, VideoAttributes, Comment, VideoHistory APIs.
  healthcare/      EmergencyContact and Hospital APIs.
  mumchat/         Anonymous MumChatPost and MumChatReply APIs.
  partner/         InviteCode, PartnerTask, PartnerTaskCompletion APIs.
  remedies/        BabyCondition and nested Remedy read APIs.
  exercises/       Exercise read APIs.
  milk_support/    MilkListing APIs with nearby search.
  opportunities/   Model/ViewSet scaffold; URL router is currently commented out.
  welcome/         Health check endpoint.
api/core/
  exceptions.py    DRF exception normalization.
  middleware.py    process_exception logging and global rate limiter.
  pagination.py    Shared page-number pagination classes.
  renderers.py     Shared utility functions.
  throttles.py     DRF throttle classes for auth, OTP, login, and upload scopes.
api/mumaid/
  settings/        base, dev, prod, and test settings.
  celery.py        Celery application.
  urls.py          Root URL routing.
docker/
  Dockerfiles and process startup scripts.
requirements/
  base.txt, dev.txt, prod.txt.
tests/
  Pytest configuration support. There are currently no committed test modules beyond conftest.py.
```

## API Documentation

Start with the common contract:

- [API Reference](./docs/api/README.md)
- [Authentication API](./docs/api/auth.md)
- [Feeds API](./docs/api/feeds.md)
- [MumChat API](./docs/api/mumchat.md)
- [Partner API](./docs/api/partner.md)
- [Healthcare, Milk Support, Remedies, And Exercises API](./docs/api/resources.md)
- [Local Setup Notes](./docs/api/local-setup.md)
- [Architecture](./docs/architecture.md)

Authentication uses Simple JWT:

```http
Authorization: Bearer <access_token>
```

Tokens are issued by:

```txt
POST /api/auth/v1/login/
POST /api/auth/v1/verify/token/
```

Access tokens live for 120 minutes. Refresh tokens live for 1 day, rotate on refresh, and are blacklisted after rotation.

## Tests And Quality Gates

Run the test suite:

```bash
docker compose run --rm api pytest
```

Run linting:

```bash
docker compose run --rm api ruff check .
```

Pytest is configured in `pytest.ini` with:

```txt
DJANGO_SETTINGS_MODULE=mumaid.settings.test
pythonpath=api
testpaths=tests api/apps
```

The current repository has test configuration but no committed test modules beyond `tests/conftest.py`. New behavior should include focused tests under `tests/` or the owning `api/apps/<domain>/` package.

## Contributing

1. Keep changes scoped to the domain app that owns the behavior.
2. Add or update serializers, views, permissions, and tests together when changing API behavior.
3. Use public identifiers consistently where the API already exposes them. For example, MumChat uses `public_id` in URLs; feeds comments still use integer `id` in comment paths.
4. Preserve existing response shapes unless the client contract is intentionally changing.
5. Run `pytest` and `ruff check .` before opening a pull request.
6. Update docs in the same change when endpoints, fields, auth requirements, rate limits, or deployment behavior change.

## Deployment

Production is configured for Render using Docker.

The API image is built from `docker/Dockerfile.api`. Runtime settings are loaded from `mumaid.settings.prod`, which requires:

```env
SECRET_KEY=<strong-secret>
ALLOWED_HOSTS=<comma-separated-hosts>
CORS_ALLOWED_ORIGINS=<comma-separated-origins>
DATABASE_URL=<render-postgres-url>
REDIS_URL=<render-redis-url>
CLOUDINARY_CLOUD_NAME=<cloudinary-cloud-name>
CLOUDINARY_CLOUD_API_KEY=<cloudinary-api-key>
CLOUDINARY_CLOUD_API_SECRET=<cloudinary-api-secret>
ANONYMOUS_SALT=<stable-secret-salt>
BREVO_API_KEY=<brevo-api-key>
DEFAULT_FROM_EMAIL=<verified-sender>
SENTRY_DSN=<optional-sentry-dsn>
```

`docker/scripts/entrypoint.sh` applies migrations and runs `collectstatic --noinput --clear`. `docker/scripts/start-api.sh` starts Gunicorn:

```bash
gunicorn mumaid.wsgi:application --bind 0.0.0.0:${PORT:-8000}
```

Production security settings enforce HTTPS, secure cookies, HSTS, `X_FRAME_OPTIONS=DENY`, Redis-backed Django cache/session storage, Cloudinary media storage, and WhiteNoise static file storage.

Celery worker and beat images are defined in `docker/Dockerfile.worker`. `docker-compose.prod.yml` currently leaves worker and beat services commented out with a note to enable them when the deployment plan supports additional processes.
