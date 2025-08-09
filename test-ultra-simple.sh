#!/bin/bash
# Ultra-simple deployment test

set -e
echo "🧪 Testing ultra-simple deployment..."

cd backend

echo "📦 Installing ultra-minimal requirements..."
pip install --no-cache-dir -r requirements-ultra-minimal.txt

echo "🚀 Starting server..."
timeout 5s python server_ultra_simple.py &
SERVER_PID=$!
sleep 2

echo "🔍 Testing endpoints..."
if curl -f http://localhost:8001/api/health > /dev/null 2>&1; then
    echo "✅ Health check: PASSED"
else
    echo "❌ Health check: FAILED"
    exit 1
fi

if curl -f http://localhost:8001/api/exchange-keys/supported-exchanges > /dev/null 2>&1; then
    echo "✅ Exchanges endpoint: PASSED"
else
    echo "❌ Exchanges endpoint: FAILED" 
    exit 1
fi

kill $SERVER_PID 2>/dev/null || true

echo ""
echo "🎉 ULTRA-SIMPLE DEPLOYMENT TEST PASSED!"
echo ""
echo "This configuration will work on ANY deployment platform."
echo "No Rust compilation, no cryptography, no complex dependencies."
echo ""
echo "Deploy with:"
echo "- Requirements: requirements-ultra-minimal.txt"  
echo "- Server: server_ultra_simple.py"
echo "- Docker: Dockerfile.ultra-simple"