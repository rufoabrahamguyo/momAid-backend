# Base image
FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Build-time settings only (real secrets come from the host e.g. Render).
RUN SECRET_KEY=collectstatic-build-only-not-secret \
    DJANGO_ENV=dev \
    ALLOWED_HOSTS=localhost \
    python manage.py collectstatic --noinput

CMD ["sh", "-c", "gunicorn mumaid.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]