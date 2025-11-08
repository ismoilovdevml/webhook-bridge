# Production Deployment Guide

## Quick Setup

### 1. Add GitHub Secrets

Go to: `Settings > Secrets and variables > Actions > New repository secret`

Add these 3 secrets:

| Secret Name | Value | Description |
|------------|-------|-------------|
| `SERVER_IP` | `your.server.ip` | Production server IP or domain |
| `SERVER_USERNAME` | `root` | SSH username |
| `SSH_PRIVATE_KEY` | `-----BEGIN OPENSSH PRIVATE KEY-----...` | SSH private key content |

### 2. Generate SSH Key

```bash
# Generate new SSH key
ssh-keygen -t ed25519 -C "github-actions-webhook-bridge" -f ~/.ssh/webhook-deploy

# Copy public key to server
ssh-copy-id -i ~/.ssh/webhook-deploy.pub root@YOUR_SERVER_IP

# Get private key for GitHub Secret
cat ~/.ssh/webhook-deploy
# Copy entire output including BEGIN and END lines
```

### 3. Server Setup (One-time)

SSH to your server and run:

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker --now

# Install Docker Compose plugin
apt-get update
apt-get install -y docker-compose-plugin

# Create app directory
mkdir -p /opt/webhook-bridge
cd /opt/webhook-bridge

# Verify Docker works
docker --version
docker compose version
```

### 4. Setup Nginx + SSL (Recommended)

```bash
# Install Nginx and Certbot
apt-get install -y nginx certbot python3-certbot-nginx

# Create Nginx config
cat > /etc/nginx/sites-available/webhook-bridge << 'EOF'
server {
    listen 80;
    server_name alert.helm.uz;

    client_max_body_size 10M;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/webhook-bridge /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# Get SSL certificate
certbot --nginx -d alert.helm.uz --non-interactive --agree-tos -m your@email.com
```

### 5. Deploy!

Just push to main branch:

```bash
git add .
git commit -m "Setup CI/CD deployment"
git push origin main
```

GitHub Actions will automatically:
1. ✅ Run linting and tests
2. ✅ Build Docker images
3. ✅ Push to GitHub Container Registry
4. ✅ Deploy to your server via SSH
5. ✅ Restart containers

## Monitoring

### Watch Deployment
- Go to GitHub → Actions tab
- Click on latest workflow run
- Watch progress of each job

### Check Server Status

```bash
# SSH to server
ssh root@YOUR_SERVER_IP

# Check running containers
cd /opt/webhook-bridge
docker compose ps

# View logs
docker compose logs -f

# Check specific service
docker logs webhook-bridge-backend -f
docker logs webhook-bridge-frontend -f
```

### Access Application

After deployment:
- Frontend: `https://alert.helm.uz`
- API Docs: `https://alert.helm.uz/api/docs`
- Health: `https://alert.helm.uz/api/health`

## Troubleshooting

### Deployment Failed

**Check GitHub Actions logs:**
```
GitHub → Actions → Click failed workflow → View logs
```

**Common issues:**

1. **SSH Connection Failed**
   - Verify `SERVER_IP` secret is correct
   - Check firewall allows SSH (port 22)
   - Test SSH manually: `ssh -i ~/.ssh/webhook-deploy root@SERVER_IP`

2. **Docker Pull Failed**
   - Server needs internet access
   - Check GHCR authentication
   - Verify images exist: https://github.com/USERNAME/REPO/pkgs/container/webhook-bridge

3. **Containers Won't Start**
   ```bash
   # SSH to server
   cd /opt/webhook-bridge
   docker compose logs
   docker compose down
   docker compose up -d
   ```

4. **Port Already in Use**
   ```bash
   # Find what's using port 3000
   netstat -tlnp | grep 3000
   # Kill the process or change port in docker-compose.yml
   ```

### Manual Deployment

If GitHub Actions fails, deploy manually:

```bash
# SSH to server
ssh root@YOUR_SERVER_IP
cd /opt/webhook-bridge

# Login to GHCR
echo "YOUR_GITHUB_TOKEN" | docker login ghcr.io -u USERNAME --password-stdin

# Pull images
docker pull ghcr.io/USERNAME/webhook-bridge/backend:latest
docker pull ghcr.io/USERNAME/webhook-bridge/frontend:latest

# Restart
docker compose down
docker compose up -d

# Check
docker compose ps
docker compose logs -f
```

### Rollback to Previous Version

```bash
# SSH to server
cd /opt/webhook-bridge

# List available image tags
docker images | grep webhook-bridge

# Edit docker-compose.yml
# Change :latest to :main-COMMIT_SHA

# Restart
docker compose down
docker compose up -d
```

## Maintenance

### View Logs
```bash
docker compose logs -f
docker compose logs -f backend
docker compose logs -f frontend
```

### Restart Services
```bash
docker compose restart
docker compose restart backend
docker compose restart frontend
```

### Update Images
```bash
docker pull ghcr.io/USERNAME/webhook-bridge/backend:latest
docker pull ghcr.io/USERNAME/webhook-bridge/frontend:latest
docker compose up -d
```

### Clean Old Images
```bash
docker image prune -af
```

### Backup Database
```bash
# Database is in volume: webhook-data
docker compose down
docker run --rm -v webhook-bridge_webhook-data:/data -v $(pwd):/backup alpine tar czf /backup/webhook-backup-$(date +%Y%m%d).tar.gz /data
docker compose up -d
```

### Restore Database
```bash
docker compose down
docker run --rm -v webhook-bridge_webhook-data:/data -v $(pwd):/backup alpine tar xzf /backup/webhook-backup-YYYYMMDD.tar.gz -C /
docker compose up -d
```

## Security

### Firewall Setup
```bash
# Allow SSH, HTTP, HTTPS
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### Regular Updates
```bash
# Update system
apt-get update && apt-get upgrade -y

# Update Docker
curl -fsSL https://get.docker.com | sh
```

### SSL Certificate Renewal
Certbot automatically renews certificates. Test renewal:
```bash
certbot renew --dry-run
```
