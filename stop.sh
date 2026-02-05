#!/bin/bash

# Chemical Equipment Visualizer - Stop Script
# This script stops all running services

set -e

echo "🛑 Stopping Chemical Equipment Visualizer services..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Stop backend
if [ -f "backend.pid" ]; then
    PID=$(cat backend.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "   Stopping backend (PID: $PID)..."
        kill $PID
    fi
    rm backend.pid
fi

# Stop frontend
if [ -f "frontend.pid" ]; then
    PID=$(cat frontend.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "   Stopping frontend (PID: $PID)..."
        kill $PID
    fi
    rm frontend.pid
fi

# Kill any remaining processes on default ports
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

echo "✅ All services stopped."
