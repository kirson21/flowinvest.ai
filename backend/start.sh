#!/bin/bash
# Start script for f01i.ai backend

# Set environment variables
export ENVIRONMENT=production
export PORT=${PORT:-8001}

# Start the server
uvicorn server:app --host 0.0.0.0 --port $PORT --no-reload