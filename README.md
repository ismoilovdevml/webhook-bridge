# Webhook Bridge

Git webhook → Telegram/Slack/Discord/Mattermost/Email

**Supported Platforms:** GitLab, GitHub, Bitbucket
**Notification Channels:** Telegram, Slack, Discord, Mattermost, Email

## Quick Start

```bash
# 1. Clone repository
git clone https://github.com/yourusername/webhook-bridge.git
cd webhook-bridge

# 2. Run setup script
bash scripts/setup.sh

# 3. Start services
docker-compose up -d

# 4. Access dashboard
# Frontend: http://localhost:3000
# Login with credentials shown in setup output
```

## Manual Setup

If you prefer manual configuration:

```bash
# Generate secure keys
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Create .env file
cp backend/.env.example .env
# Edit .env and add your keys
```

## Setup

### 1. Login
- URL: http://localhost:3000/login
- Username: `admin`
- Password: Check setup script output or `cat .env | grep ADMIN_PASSWORD`

### 2. Add Provider
Dashboard → Channels → Click provider icon → Enter credentials → Test → Save

**Telegram:** Bot token + Chat ID
**Slack/Discord/Mattermost:** Webhook URL
**Email:** SMTP settings

### 3. Configure Git Webhook

**GitLab:**
```
Settings → Webhooks → Add webhook
URL: https://your-domain.com/api/webhook/git
Triggers: Push, Merge Request, Pipeline, etc.
```

**GitHub:**
```
Settings → Webhooks → Add webhook
Payload URL: https://your-domain.com/api/webhook/git
Content type: application/json
Events: Push, Pull requests, Issues, etc.
```

**Bitbucket:**
```
Repository Settings → Webhooks → Add webhook
URL: https://your-domain.com/api/webhook/git
Triggers: Push, Pull request, etc.
```

### 4. Test
Push a commit → Check History tab for events

## Production Deployment

```bash
# 1. Server setup (Ubuntu)
curl -fsSL https://get.docker.com | sh

# 2. Clone and setup
git clone <repo> /opt/webhook-bridge
cd /opt/webhook-bridge
bash scripts/setup.sh production

# 3. Start services
docker-compose up -d

# 4. Check logs
docker-compose logs -f
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Secure with SSL:
```bash
certbot --nginx -d your-domain.com
```

## Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Environment Variables

**Required:**
- `SECRET_KEY` - JWT token signing (auto-generated)
- `ENCRYPTION_KEY` - Provider data encryption (auto-generated)
- `ADMIN_PASSWORD` - Admin login (auto-generated)

**Optional:**
- `WEBHOOK_SECRET` - Git webhook signature validation
- `ADMIN_USERNAME` - Default: admin
- `ADMIN_EMAIL` - Default: admin@localhost

See `backend/.env.example` for full configuration options.

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   Git       │─────▶│  Webhook     │─────▶│  Notification   │
│   Platform  │      │  Bridge API  │      │  Providers      │
│             │      │              │      │                 │
│ GitLab      │      │ • Parse      │      │ • Telegram      │
│ GitHub      │      │ • Filter     │      │ • Slack         │
│ Bitbucket   │      │ • Transform  │      │ • Discord       │
│             │      │ • Route      │      │ • Mattermost    │
└─────────────┘      └──────────────┘      │ • Email         │
                              │             └─────────────────┘
                              │
                      ┌───────▼────────┐
                      │   Dashboard    │
                      │   (Vue 3)      │
                      │                │
                      │ • History      │
                      │ • Configure    │
                      │ • Monitor      │
                      └────────────────┘
```

## License

MIT
