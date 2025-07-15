#!/bin/bash
# Railway Frontend Start Script

echo "Starting Flow Invest Frontend..."

# Install dependencies
npm install

# Build the application
npm run build

# Install serve globally
npm install -g serve

# Start the application
serve -s build -p $PORT