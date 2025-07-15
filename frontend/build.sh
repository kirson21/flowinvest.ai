#!/bin/bash

# Flow Invest Frontend Production Build Script

echo "🚀 Building Flow Invest Frontend for Production..."

# Set environment variables for production
export NODE_ENV=production
export REACT_APP_BACKEND_URL=https://your-backend-service.railway.app
export REACT_APP_SUPABASE_URL=https://pmfwqmaykidbvjhcqjrr.supabase.co
export REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBtZndxbWF5a2lkYnZqaGNxanJyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI0MDk2MjUsImV4cCI6MjA2Nzk4NTYyNX0.BsJ0128ME7WhH-CBRb3_LTV5NvsDkVev07SzOalAb-E

# Install dependencies
echo "📦 Installing dependencies..."
yarn install --frozen-lockfile

# Build the application
echo "🔨 Building application..."
yarn build

# Check if build was successful
if [ -d "build" ]; then
    echo "✅ Build completed successfully!"
    echo "📁 Build output available in ./build directory"
    echo "🌐 Ready for deployment to Railway"
else
    echo "❌ Build failed!"
    exit 1
fi