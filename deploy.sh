#!/bin/bash

# Chemical Equipment Visualizer - Deployment Script
# This script deploys the application for production use

set -e

echo "🚀 Chemical Equipment Visualizer - Deployment"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
BACKEND_PORT=${BACKEND_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-3000}

echo ""
echo "📦 Step 1: Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

echo ""
echo "📦 Step 2: Installing backend dependencies..."
cd backend
pip install -r requirements.txt gunicorn whitenoise -q
cd ..

echo ""
echo "🗄️ Step 3: Running database migrations..."
cd backend
python manage.py migrate --run-syncdb
cd ..

echo ""
echo "📦 Step 4: Building frontend..."
cd frontend-web
if [ ! -d "node_modules" ]; then
    npm install
fi
REACT_APP_API_URL=http://localhost:$BACKEND_PORT/api npm run build
cd ..

echo ""
echo "🌐 Step 5: Starting services..."

# Kill any existing processes on the ports
lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true

# Start backend with gunicorn
echo "   Starting backend on port $BACKEND_PORT..."
cd backend
./../.venv/bin/gunicorn chemical_visualizer.wsgi:application \
    --bind 0.0.0.0:$BACKEND_PORT \
    --workers 3 \
    --daemon \
    --access-logfile ../logs/backend-access.log \
    --error-logfile ../logs/backend-error.log \
    --pid ../backend.pid
cd ..

# Create logs directory
mkdir -p logs

# Start frontend with serve (or use Python's http.server)
echo "   Starting frontend on port $FRONTEND_PORT..."
cd frontend-web
npx serve -s build -l $FRONTEND_PORT &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
cd ..

sleep 2

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost:$FRONTEND_PORT"
echo "   Backend API: http://localhost:$BACKEND_PORT/api"
echo "   Admin Panel: http://localhost:$BACKEND_PORT/admin"
echo ""
echo "📋 To stop the services:"
echo "   ./stop.sh"
echo ""
