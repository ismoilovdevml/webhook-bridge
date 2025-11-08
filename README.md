# Webhook Bridge

Git webhook → Telegram/Slack/Discord/Mattermost/Email

**Supported Platforms:** GitLab, GitHub, Bitbucket
**Notification Channels:** Telegram, Slack, Discord, Mattermost, Email

## Quick Start

### Local Development
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

### 2. Configure Git Webhook

**GitLab:**
Settings → Webhooks → Add webhook
```
URL: https://your-domain.com/api/webhook
Triggers: Push, Tag, Merge Request, Issues, Comments, Pipeline, Wiki, Deployment, Release
```

**GitHub:**
Settings → Webhooks → Add webhook
```
Payload URL: https://your-domain.com/api/webhook
Content type: application/json
Events: Push, Pull requests, Issues, Releases, Workflow runs
```

**Bitbucket:**
Repository Settings → Webhooks → Add webhook
```
URL: https://your-domain.com/api/webhook
Triggers: Push, Pull request, Pipeline, Issue
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

After setup, secure with SSL:
```bash
certbot --nginx -d your-domain.com
```
