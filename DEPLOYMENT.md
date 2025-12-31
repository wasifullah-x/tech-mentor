# Deployment Guide

## Production Deployment Options

### Option 1: Docker Deployment (Recommended)

#### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Domain name (optional)
- SSL certificate (recommended)

#### Steps

1. **Prepare Environment**

```bash
# Clone repository
git clone <repository-url>
cd "AI Project"

# Create production environment file
cp .env.example .env
```

2. **Configure Environment Variables**
   Edit `.env`:

```bash
# Production settings
OPENAI_API_KEY=your_production_key
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-3.5-turbo
ENVIRONMENT=production
LOG_LEVEL=INFO

# Security
RATE_LIMIT_PER_MINUTE=30
ENABLE_SAFETY_CHECKS=True
```

3. **Build and Deploy**

```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

4. **Verify Deployment**

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost/
```

### Option 2: Cloud Platform Deployment

#### AWS Deployment

**Using EC2:**

1. **Launch EC2 Instance**

   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t3.medium (minimum)
   - Security Group: Allow ports 80, 443, 8000

2. **Install Dependencies**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y
```

3. **Deploy Application**

```bash
# Clone repository
git clone <repository-url>
cd "AI Project"

# Set up environment
cp .env.example .env
# Edit .env with production values

# Start services
sudo docker-compose up -d
```

4. **Configure Nginx Reverse Proxy**

```bash
sudo apt install nginx -y

# Create nginx config
sudo nano /etc/nginx/sites-available/it-support
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/it-support /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

5. **SSL with Let's Encrypt**

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

#### Google Cloud Platform (GCP)

**Using Cloud Run:**

1. **Build Container Images**

```bash
# Backend
cd backend
gcloud builds submit --tag gcr.io/PROJECT_ID/it-support-backend

# Frontend
cd ../frontend
gcloud builds submit --tag gcr.io/PROJECT_ID/it-support-frontend
```

2. **Deploy to Cloud Run**

```bash
# Backend
gcloud run deploy it-support-backend \
  --image gcr.io/PROJECT_ID/it-support-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your_key

# Frontend
gcloud run deploy it-support-frontend \
  --image gcr.io/PROJECT_ID/it-support-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure Deployment

**Using Azure Container Instances:**

```bash
# Create resource group
az group create --name it-support-rg --location eastus

# Deploy backend
az container create \
  --resource-group it-support-rg \
  --name it-support-backend \
  --image your-registry/it-support-backend:latest \
  --dns-name-label it-support-backend \
  --ports 8000 \
  --environment-variables OPENAI_API_KEY=your_key

# Deploy frontend
az container create \
  --resource-group it-support-rg \
  --name it-support-frontend \
  --image your-registry/it-support-frontend:latest \
  --dns-name-label it-support-frontend \
  --ports 80
```

### Option 3: Traditional Server Deployment

#### Prerequisites

- Ubuntu 22.04 or similar
- Python 3.11+
- Node.js 18+
- Nginx

#### Backend Deployment

1. **Install System Dependencies**

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv nginx -y
```

2. **Set Up Application**

```bash
# Create application directory
sudo mkdir -p /opt/it-support
cd /opt/it-support

# Clone repository
git clone <repository-url> .

# Set up Python environment
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with production values
```

3. **Create Systemd Service**

```bash
sudo nano /etc/systemd/system/it-support-backend.service
```

```ini
[Unit]
Description=IT Support Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/it-support/backend
Environment="PATH=/opt/it-support/backend/venv/bin"
ExecStart=/opt/it-support/backend/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable it-support-backend
sudo systemctl start it-support-backend
sudo systemctl status it-support-backend
```

#### Frontend Deployment

1. **Build Frontend**

```bash
cd /opt/it-support/frontend
npm install
npm run build
```

2. **Configure Nginx**

```bash
sudo nano /etc/nginx/sites-available/it-support
```

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /opt/it-support/frontend/dist;
    index index.html;

    # Frontend
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/it-support /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Environment Configuration

### Production Environment Variables

**Backend (.env):**

```bash
# API Configuration
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=False

# LLM Keys (REQUIRED)
OPENAI_API_KEY=your_production_key
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-3.5-turbo

# Database
CHROMA_PERSIST_DIRECTORY=/app/data/chroma_db

# Security
ENABLE_SAFETY_CHECKS=True
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_PER_HOUR=500

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log

# CORS
CORS_ORIGINS=https://your-domain.com
```

## Monitoring

### Health Checks

**Backend:**

```bash
curl http://localhost:8000/health
```

**Expected Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "vector_db_status": "operational",
  "llm_status": "operational",
  "uptime_seconds": 12345.67
}
```

### Logging

**View Backend Logs:**

```bash
# Docker
docker-compose logs -f backend

# Systemd
sudo journalctl -u it-support-backend -f

# Log file
tail -f /opt/it-support/backend/logs/app.log
```

### Prometheus Metrics (Optional)

Add to `backend/api/main.py`:

```python
from prometheus_client import Counter, Histogram, make_asgi_app

# Metrics
request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

# Mount metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

## Backup and Recovery

### Backup Vector Database

```bash
# Create backup
tar -czf chroma_backup_$(date +%Y%m%d).tar.gz backend/data/chroma_db/

# Upload to S3 (optional)
aws s3 cp chroma_backup_*.tar.gz s3://your-bucket/backups/
```

### Restore from Backup

```bash
# Stop services
docker-compose down

# Restore data
tar -xzf chroma_backup_20240101.tar.gz -C backend/data/

# Restart services
docker-compose up -d
```

## Security Best Practices

1. **Use HTTPS**: Always use SSL certificates in production
2. **Secure API Keys**: Use environment variables, never commit keys
3. **Rate Limiting**: Configure appropriate rate limits
4. **CORS**: Restrict allowed origins
5. **Input Validation**: All requests validated by Pydantic
6. **Update Dependencies**: Regularly update packages
7. **Monitor Logs**: Set up log aggregation and alerts

## Scaling

### Horizontal Scaling

**Using Docker Swarm:**

```bash
docker swarm init
docker stack deploy -c docker-compose.yml it-support
docker service scale it-support_backend=3
```

**Using Kubernetes:**
See `kubernetes/` directory for deployment manifests.

### Vertical Scaling

**Increase Resources:**

- Backend: Increase CPU/RAM for faster LLM inference
- ChromaDB: More memory for larger knowledge bases

## Troubleshooting

### Common Issues

**Backend won't start:**

```bash
# Check logs
docker-compose logs backend

# Verify environment
docker-compose exec backend env | grep API_KEY

# Test manually
docker-compose exec backend python -c "from api.main import app; print('OK')"
```

**High latency:**

- Check LLM API status
- Increase RAG cache size
- Use faster embedding model
- Scale backend horizontally

**Out of memory:**

- Increase container memory limits
- Reduce batch sizes
- Use smaller embedding model

## Maintenance

### Update Deployment

```bash
# Pull latest code
git pull origin main

# Rebuild containers
docker-compose build

# Restart services (zero-downtime)
docker-compose up -d --no-deps --build backend
docker-compose up -d --no-deps --build frontend
```

### Database Maintenance

```bash
# Vacuum ChromaDB (if needed)
docker-compose exec backend python -c "from services.rag_service import RAGService; import asyncio; s = RAGService(); asyncio.run(s.initialize())"
```

## Cost Optimization

1. **Use gpt-3.5-turbo** instead of GPT-4 (10x cheaper)
2. **Cache common queries** to reduce LLM calls
3. **Use spot instances** for non-critical workloads
4. **Optimize vector DB** with smaller embeddings
5. **Set up autoscaling** based on traffic

## Support

For deployment issues:

- Check logs first
- Review this guide
- Open GitHub issue with logs
- Email: devops@itsupport-ai.com
