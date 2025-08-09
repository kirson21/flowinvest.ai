#!/bin/bash
# Build script for deployment platforms - RUST-FREE

set -e
echo "🔧 Building Flow Invest Backend (Rust-Free Mode)"

# Navigate to backend directory
if [[ -d "backend" ]]; then
    cd backend
fi

# Upgrade pip
pip install --upgrade pip

# Install rust-free requirements
if [[ -f "requirements-rust-free.txt" ]]; then
    echo "📦 Installing rust-free requirements..."
    pip install --no-cache-dir -r requirements-rust-free.txt
elif [[ -f "requirements-deploy.txt" ]]; then
    echo "📦 Installing deployment requirements..."
    pip install --no-cache-dir -r requirements-deploy.txt
else
    echo "⚠️ Creating minimal requirements on the fly..."
    cat > requirements-auto.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
python-dotenv==1.0.0
requests==2.31.0
EOF
    pip install --no-cache-dir -r requirements-auto.txt
fi

echo "✅ Build completed successfully!"