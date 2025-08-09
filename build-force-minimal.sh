#!/bin/bash
# EMERGENCY BUILD SCRIPT - Forces minimal installation

set -e

echo "🚨 FORCING MINIMAL INSTALLATION - NO RUST COMPILATION"

# Remove any cached pip files that might cause issues
rm -rf ~/.cache/pip/* 2>/dev/null || true
rm -rf /tmp/pip-* 2>/dev/null || true

# Upgrade pip to latest
pip install --upgrade pip --no-cache-dir

# Install packages one by one to avoid dependency conflicts
echo "📦 Installing FastAPI..."
pip install --no-cache-dir fastapi==0.104.1

echo "📦 Installing Uvicorn..."
pip install --no-cache-dir "uvicorn[standard]==0.24.0"

echo "📦 Installing Pydantic..."
pip install --no-cache-dir pydantic==2.5.0

echo "📦 Installing Python Multipart..."
pip install --no-cache-dir python-multipart==0.0.6

echo "📦 Installing Python Dotenv..."
pip install --no-cache-dir python-dotenv==1.0.0

echo "📦 Installing Requests..."
pip install --no-cache-dir requests==2.31.0

echo "✅ All packages installed successfully!"

# Verify installation
echo "🔍 Verifying installation..."
python -c "import fastapi, uvicorn, pydantic, requests; print('✅ All imports successful')"

echo "🎉 BUILD COMPLETED - NO RUST COMPILATION REQUIRED!"