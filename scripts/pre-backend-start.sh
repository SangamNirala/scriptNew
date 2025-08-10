#!/bin/bash

# Pre-Backend Start Script for Enhanced Prompt Template System
# This script runs automatically before the backend starts to ensure dependencies are ready

echo "🔧 Enhanced Prompt Template System - Pre-Backend Startup"
echo "⏰ $(date)"
echo ""

# Change to backend directory
cd /app/backend

# Run startup check
echo "🚀 Running startup dependency check..."
python3 /app/scripts/startup-check.py

STARTUP_EXIT_CODE=$?

if [ $STARTUP_EXIT_CODE -eq 0 ]; then
    echo "✅ Startup check passed - Backend dependencies are ready"
else
    echo "⚠️  Startup check had issues - Backend may have limited functionality"
fi

echo "🏁 Pre-startup complete - Starting backend..."
echo ""

exit 0