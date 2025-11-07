# Webhook Bridge

Git webhook → Telegram/Slack/Discord/Mattermost/Email

## Quick Start

```bash
docker-compose up -d

# Frontend: http://localhost:3000
# API: http://localhost:8000/docs
```

## Setup

### 1. Add Provider
Dashboard → Alerting → Click platform icon → Enter credentials → Test → Save

**Telegram**: Bot token + Chat ID
**Slack/Discord/Mattermost**: Webhook URL
**Email**: SMTP settings

### 2. Configure GitLab Webhook
Settings → Webhooks → Add webhook
```
URL: https://your-domain.com/webhook/git
Trigger: Push, MR, Issues, Pipeline
```

### 3. Test
Push a commit → Check dashboard for events

## Production

```bash
# Server setup (Ubuntu)
curl -fsSL https://get.docker.com | sh
git clone <repo> /opt/webhook-bridge
cd /opt/webhook-bridge
docker-compose up -d
```

**Nginx reverse proxy** (SSL with certbot):
```nginx
location / { proxy_pass http://localhost:3000; }
location /api/ { proxy_pass http://localhost:8000; }
location /webhook/ { proxy_pass http://localhost:8000; }
```
