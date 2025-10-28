#!/bin/bash
set -e

echo "Installing Python dependencies..."
cd backend && pip install -r requirements.txt

echo "Building frontend..."
cd ../frontend && npm install && npm run build

echo "Build complete!"

