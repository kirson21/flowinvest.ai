# Railway Dockerfile for Flow Invest Backend

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ .

# Expose port
EXPOSE 8001

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8001

# Start command
CMD ["python", "server.py"]