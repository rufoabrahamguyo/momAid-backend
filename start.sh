#!/bin/sh



echo "Starting Django..."

gunicorn mumaid.wsgi:application --bind 0.0.0.0:8000 &



echo "Starting Celery..."

celery -A mumaid worker --loglevel=info &



wait