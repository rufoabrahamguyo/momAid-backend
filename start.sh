#!/bin/sh

set -e

echo "Running in Production Environment (Render + Neon)"


echo "Applying database migrations..."
python manage.py migrate --noinput



echo "Starting Gunicorn..."
exec gunicorn mumaid.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - &


echo "Starting Celery Worker..."
celery -A mumaid worker --loglevel=info &

wait