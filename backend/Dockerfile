# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn dj-database-url psycopg2-binary whitenoise

# Copy application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --settings=chemical_visualizer.settings_prod || true

# Create media directory
RUN mkdir -p media

# Expose port
EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "chemical_visualizer.wsgi:application"]
