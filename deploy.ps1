# Government AI API - Deployment Script (PowerShell)
# This script deploys the latest changes to the DigitalOcean droplet

Write-Host "Starting deployment of Government AI API..." -ForegroundColor Green

# Server details
$SERVER_IP = "178.62.39.248"
$SERVER_USER = "root"

Write-Host "Committing and pushing changes to GitHub..." -ForegroundColor Yellow
git add .
git commit -m "Fix: Update table name to decision_summaries and fix cache directory issues"
git push origin master

Write-Host "Connecting to server and updating..." -ForegroundColor Yellow

# Execute on remote server
ssh root@178.62.39.248 @'
echo "Navigating to project directory..."
cd /root/gov-ai-api

echo "Pulling latest changes..."
git pull

echo "Stopping current containers..."
docker compose down

echo "Building new image..."
docker compose build

echo "Starting services..."
docker compose up -d

echo "Waiting for service to start..."
sleep 10

echo "Checking service health..."
curl -s http://localhost:8000/health

echo "Checking data stats..."
curl -s http://localhost:8000/stats

echo "Viewing recent logs..."
docker compose logs --tail=50
'@

Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "API is available at: http://178.62.39.248:8000" -ForegroundColor Cyan
Write-Host "Documentation: http://178.62.39.248:8000/docs" -ForegroundColor Cyan
