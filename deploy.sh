#!/bin/bash
# Deployment script for Government AI API

set -e

echo "🚀 Starting deployment of Government AI API..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with your credentials"
    exit 1
fi

# Pull latest changes (if using git)
if [ -d .git ]; then
    echo "📥 Pulling latest changes..."
    git pull origin main || true
fi

# Build and deploy with Docker Compose
echo "🐳 Building Docker images..."
docker compose build

echo "🔄 Stopping old containers..."
docker compose down

echo "🚀 Starting new containers..."
docker compose up -d

# Wait for health check
echo "⏳ Waiting for service to be healthy..."
sleep 10

# Check if service is running
if docker compose ps | grep -q "Up"; then
    echo "✅ Deployment successful!"
    echo "📊 Service status:"
    docker compose ps
    
    # Test health endpoint
    echo "🏥 Testing health endpoint..."
    curl -s http://localhost:8000/health | python3 -m json.tool || echo "⚠️ Health check failed"
else
    echo "❌ Deployment failed!"
    echo "📋 Logs:"
    docker compose logs --tail=50
    exit 1
fi

echo "🎉 Deployment complete!"
echo "📚 API documentation available at: http://localhost:8000/docs"