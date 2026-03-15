#!/bin/bash
# API Container Startup Script

echo "🚀 Starting API container..."

# Start the API server
echo "🌐 Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
