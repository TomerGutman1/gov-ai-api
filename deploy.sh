#!/bin/bash

# Government AI API Deployment Script
# This script deploys the latest changes to the DigitalOcean droplet

echo "🚀 Starting deployment of Government AI API..."

# Server details
SERVER_IP="178.62.39.248"
SERVER_USER="root"

echo "📦 Committing and pushing changes to GitHub..."
git add .
git commit -m "Fix: Update table name to decision_summaries and fix cache directory issues"
git push origin master || git push origin main

echo "🔄 Connecting to server and updating..."
ssh ${SERVER_USER}@${SERVER_IP} << 'EOF'
    echo "📂 Navigating to project directory..."
    cd /root/gov-ai-api
    
    echo "🔄 Pulling latest changes..."
    git pull
    
    echo "🛑 Stopping current containers..."
    docker compose down
    
    echo "🏗️ Building new image..."
    docker compose build
    
    echo "🚀 Starting services..."
    docker compose up -d
    
    echo "⏳ Waiting for service to start..."
    sleep 10
    
    echo "✅ Checking service health..."
    curl -s http://localhost:8000/health | jq .
    
    echo "📊 Checking data stats..."
    curl -s http://localhost:8000/stats | jq .
    
    echo "📋 Viewing recent logs..."
    docker compose logs --tail=50
EOF

echo "✅ Deployment complete!"
echo "🌐 API is available at: http://${SERVER_IP}:8000"
echo "📚 Documentation: http://${SERVER_IP}:8000/docs"
