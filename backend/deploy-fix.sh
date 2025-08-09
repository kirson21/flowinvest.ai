#!/bin/bash
# Deployment Migration Script

echo "=== Flow Invest Backend Deployment Fix ==="
echo "Fixing Rust compilation issues for deployment..."

# Backup current requirements
cp requirements.txt requirements-backup.txt
echo "✅ Backed up original requirements.txt"

# Copy rust-free requirements
cp requirements-rust-free.txt requirements.txt
echo "✅ Switched to Rust-free requirements"

# Test installation
echo "🔄 Testing package installation..."
if pip install -r requirements.txt --dry-run > /dev/null 2>&1; then
    echo "✅ Rust-free requirements are installable"
else
    echo "❌ Package installation test failed"
    echo "Restoring backup..."
    cp requirements-backup.txt requirements.txt
    exit 1
fi

echo "🔄 Starting minimal server test..."
timeout 5s python server_minimal.py &
SERVER_PID=$!
sleep 2

# Test endpoints
if curl -f http://localhost:8001/api/health > /dev/null 2>&1; then
    echo "✅ Minimal server test passed"
    kill $SERVER_PID 2>/dev/null || true
else
    echo "❌ Minimal server test failed"
    kill $SERVER_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo "🎉 DEPLOYMENT FIX COMPLETE!"
echo ""
echo "Next steps:"
echo "1. Deploy with: python server_minimal.py"
echo "2. Or use Docker: docker build -f Dockerfile.rust-free ."
echo "3. Test with: curl http://your-domain/api/health"
echo ""
echo "Files created:"
echo "- requirements-rust-free.txt (minimal dependencies)"
echo "- server_minimal.py (deployment server)"
echo "- Dockerfile.rust-free (deployment Docker config)"
echo "- RUST_FREE_DEPLOYMENT.md (complete guide)"