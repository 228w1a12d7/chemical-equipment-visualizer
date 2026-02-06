# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Create media directory
RUN mkdir -p media

# Make start script executable
RUN chmod +x start.sh

# Expose port
EXPOSE 8000

# Run with start script (runs migrations + gunicorn)
CMD ["./start.sh"]
