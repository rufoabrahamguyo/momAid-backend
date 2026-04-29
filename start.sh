#!/bin/sh

echo "Starting Django..."

echo "Applying database migrations..."
python manage.py migrate --noinput

# 2. Start Gunicorn

echo "Starting Gunicorn..."
gunicorn mumaid.wsgi:application --bind 0.0.0.0:8000 --workers 1 --threads 2 &

# 3. Start Celery
echo "Starting Celery..."
celery -A mumaid worker --loglevel=info --concurrency=1 --pool=solo &

wait
