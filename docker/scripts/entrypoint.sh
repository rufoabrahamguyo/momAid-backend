#!/bin/env bash
set -e

echo "⏳ Waiting for database..."

echo "✅ Database is ready"
echo "🔄 Applying migrations..."
python manage.py migrate --noinput

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "🚀 Starting service..."
exec "$@"