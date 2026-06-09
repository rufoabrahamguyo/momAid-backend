#!/bin/sh
set -e

echo "⚙️  Starting Celery worker..."
exec celery -A mumaid worker \
    --loglevel=info \
    --concurrency=${CELERY_CONCURRENCY:-4} \
    --max-tasks-per-child=1000 \
    -Q default,notifications,emails

    