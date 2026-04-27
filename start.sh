#!/bin/sh


echo "Starting Django..."

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "seed data"
python manage.py seed_stress_data


gunicorn mumaid.wsgi:application --bind 0.0.0.0:8000 &


echo "Starting Celery..."

celery -A mumaid worker --loglevel=info &



wait