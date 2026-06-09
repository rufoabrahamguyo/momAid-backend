#!/bin/sh
set -e

echo "🕐 Starting Celery beat..."

exec celery -A mumaid beat \
    --loglevel=info \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler