#!/bin/sh
set -e

echo "Starting Gunicorn..."
exec gunicorn mumaid.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 1 \
    --threads 2 \
    --worker-class gthread \
    --worker-tmp-dir /dev/shm \
    --timeout 60 \
    --keep-alive 2 \
    --max-requests 500 \
    --max-requests-jitter 50 \
    --log-level warning \
    --access-logfile - \
    --error-logfile -