# Docker Deployment Guide

## Quick Start

### 1. Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone <your-repo>
cd HappyRobot-FDE

# Set your FMCSA API key
export FMCSA_API_KEY=your_actual_fmcsa_api_key_here

# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f
```

### 2. Using Docker directly

```bash
# Build the image
docker build -t happyrobot-fde .

# Run the container
docker run -d \
  --name happyrobot-fde-api \
  -p 8000:8000 \
  -e FMCSA_API_KEY=your_actual_fmcsa_api_key_here \
  -v $(pwd)/temp:/app/temp \
  happyrobot-fde
```

## Environment Variables

### Required
- `FMCSA_API_KEY`: Your FMCSA API key for MC verification

### Optional
- `API_KEYS`: Custom API keys (default: demo keys)
- `DEBUG`: Enable debug mode (default: false)
- `APP_NAME`: Application name
- `APP_VERSION`: Application version

## Production Deployment

### 1. Security Considerations
- Change default API keys in production
- Use secrets management for sensitive data
- Configure proper firewall rules
- Use HTTPS with reverse proxy

### 2. Example production docker-compose.yml

```yaml
version: '3.8'
services:
  happyrobot-fde:
    build: .
    environment:
      - API_KEYS=prod-key-1:Production User 1,prod-key-2:Production User 2
      - FMCSA_API_KEY=${FMCSA_API_KEY}
      - DEBUG=false
    volumes:
      - /opt/happyrobot/data:/app/temp
    restart: unless-stopped
    networks:
      - internal

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl:ro
    depends_on:
      - happyrobot-fde
    networks:
      - internal

networks:
  internal:
    driver: bridge
```

### 3. Health Checks

The container includes health checks:
```bash
# Check container health
docker ps
docker inspect --format='{{.State.Health.Status}}' happyrobot-fde-api

# Manual health check
curl -f http://localhost:8000/health
```

## Data Persistence

Call data is stored in `/app/temp` directory. Mount a volume to persist data:
```bash
docker run -v $(pwd)/temp:/app/temp happyrobot-fde
```

## Scaling

For high-traffic deployments:
```bash
# Run multiple instances behind a load balancer
docker-compose up --scale happyrobot-fde=3
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Change port mapping
   docker run -p 8001:8000 happyrobot-fde
   ```

2. **FMCSA API key not working**
   ```bash
   # Check environment variable
   docker exec happyrobot-fde-api env | grep FMCSA
   ```

3. **Data not persisting**
   ```bash
   # Verify volume mount
   docker inspect happyrobot-fde-api | grep Mounts
   ```

### Logs

```bash
# View logs
docker logs happyrobot-fde-api

# Follow logs
docker logs -f happyrobot-fde-api

# With docker-compose
docker-compose logs -f
```

## API Documentation

Once running, access:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Alternative Docs: http://localhost:8000/redoc 