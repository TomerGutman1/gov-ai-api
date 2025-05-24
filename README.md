# Government AI API

AI-powered API for analyzing Israeli government decisions using PandasAI and OpenAI.

## 🚀 Features

- **AI-Powered Analysis**: Use natural language to query government decisions data
- **Hebrew Support**: Full support for Hebrew questions and answers
- **RESTful API**: Easy-to-use endpoints with automatic documentation
- **Real-time Data**: Connected to Supabase for up-to-date information
- **Semantic Search**: Advanced embedding-based search capabilities
- **Docker Ready**: Containerized for easy deployment

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized deployment)
- Supabase account with `israeli_government_decisions` table
- OpenAI API key

## 🛠️ Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/your-org/gov-ai-api.git
cd gov-ai-api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r app/requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

5. Run the application:
```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment

1. Build and run with Docker Compose:
```bash
docker compose up -d --build
```

2. Check logs:
```bash
docker compose logs -f
```

3. Stop the service:
```bash
docker compose down
```

## 📡 API Endpoints

### Health Check
```
GET /
GET /health
```

### Ask Questions
```
POST /ask
Content-Type: application/json

{
    "question": "כמה החלטות התקבלו בשנת 2023?"
}
```

### Get Statistics
```
GET /stats
```

### Reload Data
```
POST /reload
```

## 🌊 DigitalOcean Deployment

1. **Create a Droplet**:
   - Ubuntu 22.04
   - At least 2GB RAM (recommended for AI workloads)
   - Enable monitoring and backups

2. **Initial Setup**:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER && newgrp docker

# Install Docker Compose
sudo apt-get install docker-compose-plugin -y

# Configure firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000
sudo ufw enable
```

3. **Deploy Application**:
```bash
# Clone repository
git clone https://github.com/your-org/gov-ai-api.git
cd gov-ai-api

# Create .env file
nano .env  # Add your credentials

# Run with Docker Compose
docker compose up -d --build

# Check status
docker compose ps
docker compose logs -f
```

4. **Configure Nginx (Optional)**:
```bash
# Install Nginx
sudo apt install nginx -y

# Create configuration
sudo nano /etc/nginx/sites-available/gov-ai

# Add proxy configuration:
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/gov-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Setup SSL with Certbot
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.yourdomain.com
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `ALLOWED_ORIGIN` | CORS allowed origin | No |
| `APP_ENV` | Application environment | No |
| `LOG_LEVEL` | Logging level | No |

### Supabase Table Schema

Ensure your `israeli_government_decisions` table has appropriate columns for government decisions data. The API will automatically detect and work with your schema.

## 🧪 Testing

### Using curl:
```bash
# Health check
curl http://localhost:8000/health

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What decisions were made in 2023?"}'

# Get statistics
curl http://localhost:8000/stats
```

### Using the built-in docs:
Navigate to `http://localhost:8000/docs` for interactive API documentation.

## 🔍 Monitoring

### Docker logs:
```bash
docker compose logs -f api
```

### DigitalOcean monitoring:
- Enable droplet monitoring in the DigitalOcean dashboard
- Set up alerts for CPU, memory, and disk usage

### Application metrics:
- Check `/health` endpoint for service status
- Monitor `/stats` for data availability

## 🚨 Troubleshooting

### Common Issues:

1. **Connection refused**:
   - Check if the service is running: `docker compose ps`
   - Verify port 8000 is open: `sudo ufw status`

2. **Database errors**:
   - Verify Supabase credentials in `.env`
   - Check table exists and has data

3. **AI service errors**:
   - Verify OpenAI API key is valid
   - Check API rate limits

4. **Memory issues**:
   - Increase droplet size or add swap:
   ```bash
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📧 Support

For issues and questions, please open an issue on GitHub or contact the development team.