# Deployment Guide

This document provides instructions for deploying the LynrieScoop cinema application in different environments.

## Prerequisites

- Docker and Docker Compose
- PostgreSQL database server
- MQTT broker (Mosquitto)
- Domain name (for production)
- SSL certificate (for production)

## Local Development Deployment

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/lynriescoop.git
cd lynriescoop
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:

```conf
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/cinema

# JWT
JWT_SECRET=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=11520  # 8 days

# TMDB API
TMDB_API_KEY=your-tmdb-api-key

# MQTT
MQTT_BROKER=localhost
MQTT_PORT=1883

# CORS
CORS_ORIGINS=http://localhost:3000
ALLOWED_HOSTS=localhost,127.0.0.1

# Environment
ENVIRONMENT=development
```

Create a `.env` file in the frontend directory:

```conf
API_BASE_URL=http://localhost:8000
```

### 3. Start the MQTT Broker

```bash
docker-compose up -d mosquitto
```

### 4. Set Up the Database

```bash
# Create the database
createdb cinema

# Start the backend to run migrations
cd backend
pip install -r requirements.txt
python main.py
```

### 5. Start the Frontend Development Server

```bash
cd frontend
npm install
npm start
```

### 6. Access the Application

- Frontend: <http://localhost:3000>
- Backend API: <http://localhost:8000>
- API Documentation: <http://localhost:8000/api-docs>

## Docker Deployment

### 1. Build and Run with Docker Compose

```bash
docker-compose up -d
```

This will start:

- PostgreSQL database
- Mosquitto MQTT broker
- Backend API server
- Frontend web server (Nginx)

### 2. Access the Application

- Frontend: <http://localhost:3000>
- Backend API: <http://localhost:8000>
- API Documentation: <http://localhost:8000/api-docs>

## Production Deployment

### 1. Set Up Production Environment Variables

Create a `.env.production` file with secure settings:

```conf
# Database
DATABASE_URL=postgresql://user:password@db-host:5432/cinema

# JWT
JWT_SECRET=long-secure-random-string
ACCESS_TOKEN_EXPIRE_MINUTES=11520  # 8 days

# TMDB API
TMDB_API_KEY=your-tmdb-api-key

# MQTT
MQTT_BROKER=mqtt-host
MQTT_PORT=8883  # TLS port

# CORS
CORS_ORIGINS=https://cinema.example.com
ALLOWED_HOSTS=cinema.example.com

# Environment
ENVIRONMENT=production
```

### 2. Configure Nginx

Update `nginx.conf` for your domain:

```nginx
server {
    listen 80;
    server_name cinema.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name cinema.example.com;

    ssl_certificate /etc/letsencrypt/live/cinema.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cinema.example.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Deploy with Docker Compose

```bash
docker-compose -f docker-compose.production.yml up -d
```

### 4. Set Up SSL with Let's Encrypt

```bash
docker run -it --rm \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/lib/letsencrypt:/var/lib/letsencrypt \
  certbot/certbot certonly --webroot \
  --webroot-path=/usr/share/nginx/html \
  -d cinema.example.com
```

### 5. Configure Database Backups

```bash
# Create a backup script
mkdir -p /opt/cinema/backups
touch /opt/cinema/backup-db.sh
chmod +x /opt/cinema/backup-db.sh
```

Add the following content to `backup-db.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="/opt/cinema/backups"
BACKUP_FILE="$BACKUP_DIR/cinema_$DATE.sql"

docker exec -t cinema-db pg_dump -U postgres cinema > $BACKUP_FILE
gzip $BACKUP_FILE

# Keep only the last 7 days of backups
find $BACKUP_DIR -name "cinema_*.sql.gz" -type f -mtime +7 -delete
```

Add to crontab to run daily:

```text
0 2 * * * /opt/cinema/backup-db.sh
```

## Scaling

### Horizontal Scaling

For increased load, the application can be scaled by:

1. Adding multiple backend instances behind a load balancer
2. Deploying a clustered MQTT broker (e.g., HiveMQ or EMQ)
3. Using a managed PostgreSQL service with read replicas

```yaml
version: '3.8'

services:
  loadbalancer:
    image: nginx:alpine
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend1
      - backend2

  backend1:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/cinema
    
  backend2:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/cinema
```

## Monitoring and Logging

### Setup Prometheus and Grafana

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus

volumes:
  grafana_data:
```

### Add Logging with ELK Stack

```yaml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.14.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
    
  logstash:
    image: docker.elastic.co/logstash/logstash:7.14.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch
    
  kibana:
    image: docker.elastic.co/kibana/kibana:7.14.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

## Updating the Application

### Backend Updates

```bash
# Pull latest changes
git pull

# Update dependencies
pip install -r backend/requirements.txt

# Restart the service
docker-compose restart backend
```

### Frontend Updates

```bash
# Pull latest changes
git pull

# Update dependencies
cd frontend
npm install

# Build production assets
npm run build

# Deploy to production
rsync -avz _site/ user@server:/path/to/deployment/
```

## Troubleshooting

### Database Connection Issues

Check the database connection:

```bash
docker-compose exec backend python -c "from app.db.session import get_db; print('Database connection successful')"
```

### MQTT Connectivity

Check MQTT broker status:

```bash
docker-compose exec mosquitto mosquitto_sub -t "test" -C 1 -v
```

### JWT Authentication Issues

Verify JWT configuration:

```bash
docker-compose exec backend python -c "from app.core.security import create_access_token; print(create_access_token('test', 'Test User', 'user'))"
```
