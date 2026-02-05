#!/bin/bash
# Build script for Render deployment

set -e

echo "Installing Python dependencies..."
cd backend
pip install -r requirements.txt
pip install gunicorn whitenoise

echo "Running migrations..."
python manage.py migrate --run-syncdb

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build complete!"
