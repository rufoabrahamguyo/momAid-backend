# Local Setup

Purpose: provide the shortest reliable path to run the MomAid backend locally and verify the API is serving requests.

## Prerequisites

- Docker
- Docker Compose
- Git
- Cloudinary development credentials

## Start The Stack

From a clean machine:

```bash
git clone git@github.com:rufoabrahamguyo/momAid-backend.git
cd momAid-backend
cp .env.example .env
docker compose up --build
```

This is the supported local path. The development Dockerfile installs `requirements/dev.txt`, sets `PYTHONPATH=/app/api`, and runs Django with `DJANGO_SETTINGS_MODULE=mumaid.settings.dev`.

## Required `.env` Values

Set these values before starting the stack:

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
ANONYMOUS_SALT=local-anonymous-salt
```

Notes:

- `api/mumaid/settings/base.py` reads Cloudinary values and `ANONYMOUS_SALT` at import time. Missing values can prevent the server from booting.
- `docker-compose.yml` maps PostgreSQL to host port `5433`, but containers connect to `db:5432`.
- `docker-compose.yml` maps Redis to host port `6380`, but containers connect to `redis:6379`.
- `.env.example` currently contains duplicate `REDIS_URL` entries. For Docker Compose, use `redis://redis:6379/0`.

## Services And Ports

| Service | Container role | Host URL |
| --- | --- | --- |
| `api` | Django development server | `http://localhost:8000/` |
| `db` | PostgreSQL 15 | `localhost:5433` |
| `redis` | Redis 7 | `localhost:6380` |
| `worker` | Celery worker | n/a |
| `beat` | Celery beat | n/a |
| `mailpit` | Local SMTP capture | `http://localhost:8025/` |
| `adminer` | Database UI | `http://localhost:8080/` |

## Verify The API

Health check:

```bash
curl http://localhost:8000/api/health/
```

Open Swagger UI:

```txt
http://localhost:8000/api/docs/
```

Open OpenAPI schema:

```txt
http://localhost:8000/api/schema/
```

## Common Commands

Run migrations manually:

```bash
docker compose run --rm api python manage.py migrate
```

Create an admin user:

```bash
docker compose run --rm api python manage.py createsuperuser
```

Run tests:

```bash
docker compose run --rm api pytest
```

Run linting:

```bash
docker compose run --rm api ruff check .
```

Open Django shell:

```bash
docker compose run --rm api python manage.py shell
```

View logs for the API:

```bash
docker compose logs -f api
```

Stop containers and keep volumes:

```bash
docker compose down
```

Stop containers and remove the local database volume:

```bash
docker compose down -v
```

## Request Smoke Test

Register a mother account:

```bash
curl -X POST http://localhost:8000/api/auth/v1/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "mother@example.com",
    "password": "securepassword123",
    "role": "mother"
  }'
```

Read the OTP from Mailpit at:

```txt
http://localhost:8025/
```

Activate the account:

```bash
curl -X POST http://localhost:8000/api/auth/v1/verify/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "mother@example.com",
    "otp": "123456"
  }'
```

Use the returned `access` token:

```bash
curl http://localhost:8000/api/auth/v1/whoami/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

Replace `123456` with the actual OTP delivered to Mailpit.

## Troubleshooting

If Django fails during settings import, check:

- `SECRET_KEY`
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_CLOUD_API_KEY`
- `CLOUDINARY_CLOUD_API_SECRET`
- `ANONYMOUS_SALT`

If the API cannot connect to PostgreSQL from inside Docker, check that:

```env
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

If the API cannot connect to Redis from inside Docker, check that:

```env
REDIS_URL=redis://redis:6379/0
```

If emails are not visible in Mailpit, check that development settings are active:

```env
DJANGO_SETTINGS_MODULE=mumaid.settings.dev
EMAIL_HOST=mailpit
EMAIL_PORT=1025
```
