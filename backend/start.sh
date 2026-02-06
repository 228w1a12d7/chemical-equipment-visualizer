#!/bin/bash
set -e

# Default port if not set
PORT=${PORT:-8000}

echo "Running migrations..."
python manage.py migrate --noinput

# Create superuser if not exists
echo "Checking superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
"

echo "Starting gunicorn on port $PORT..."
# Start gunicorn
exec gunicorn chemical_visualizer.wsgi:application --bind 0.0.0.0:$PORT --workers 3
