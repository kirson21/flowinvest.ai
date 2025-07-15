# Railway Deployment Scripts

# Frontend Build Script
echo "Building Flow Invest Frontend..."
cd frontend
yarn install --frozen-lockfile
yarn build
echo "Frontend build complete!"

# Backend Setup Script  
echo "Setting up Flow Invest Backend..."
cd ../backend
pip install -r requirements.txt
echo "Backend setup complete!"

# Start Backend Service
echo "Starting Flow Invest API..."
python server.py