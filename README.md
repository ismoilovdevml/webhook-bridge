# Webhook Bridge - Universal Git Notification System

A powerful, production-ready webhook bridge that forwards events from any Git platform (GitLab, GitHub, Bitbucket) to any notification platform (Telegram, Slack, Mattermost, Discord) with beautiful formatting and a modern web dashboard.

## Features

### Core Features
- **Universal Git Platform Support**: GitLab, GitHub, Bitbucket
- **Multiple Notification Providers**: Telegram, Slack, Mattermost, Discord
- **Beautiful Message Formatting**: Custom formatters for each platform (HTML, Markdown, Slack Blocks)
- **Web Dashboard**: Modern Vue.js 3 interface for managing providers and viewing events
- **Event Logging**: Track all webhooks with detailed logs and statistics
- **Provider Management**: Easy CRUD operations for notification providers
- **Docker Ready**: Full containerized setup with docker-compose
- **Production Grade**: Clean architecture, error handling, logging, health checks

### Event Support
- Push events (commits, branches)
- Merge/Pull Request events (opened, merged, closed, updated)
- Pipeline/Workflow events (success, failed, running)
- Issue events (opened, closed, updated)
- Comment/Note events
- Tag push events
- Release events
- Wiki page events

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd webhook-bridge
```

2. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start the services:
```bash
docker-compose up -d
```

4. Access the dashboard:
```
http://localhost:3000
```

The API will be available at `http://localhost:8000`

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     GIT PLATFORMS                              │
│  GitLab  │  GitHub  │  Bitbucket  │  Gitea  │  ...            │
└────────────┬───────────────────────────────────────────────────┘
             │ Webhooks (POST /api/webhook/git)
             ▼
┌────────────────────────────────────────────────────────────────┐
│                   WEBHOOK BRIDGE BACKEND                       │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  FastAPI Application                                     │ │
│  │  • Parsers (GitLab, GitHub, Bitbucket)                   │ │
│  │  • Formatters (HTML, Markdown, Slack Blocks)             │ │
│  │  • Providers (Telegram, Slack, Mattermost, Discord)      │ │
│  │  • Database (SQLite)                                     │ │
│  │  • RESTful API                                           │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────┬───────────────────────────────────────────────────┘
             │
             ├──────────────┬─────────────┐
             ▼              ▼             ▼
┌───────────────┐  ┌──────────────┐  ┌────────────┐
│   Frontend    │  │ Notifications│  │  Database  │
│   (Vue.js)    │  │  Providers   │  │  (SQLite)  │
│  Dashboard    │  │  Messages    │  │   Logs     │
└───────────────┘  └──────────────┘  └────────────┘
```

## Project Structure

```
webhook-bridge/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   │   ├── webhooks.py    # Webhook receiver
│   │   │   ├── providers.py   # Provider CRUD
│   │   │   ├── events.py      # Event logs
│   │   │   └── dashboard.py   # Statistics
│   │   ├── models/            # Database models
│   │   ├── parsers/           # Git platform parsers
│   │   ├── providers/         # Notification providers
│   │   ├── formatters/        # Message formatters
│   │   ├── utils/             # Utilities
│   │   ├── config.py          # Configuration
│   │   ├── database.py        # Database setup
│   │   └── main.py            # Application entry
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # Vue.js 3 frontend
│   ├── src/
│   │   ├── views/             # Page components
│   │   ├── components/        # Reusable components
│   │   ├── stores/            # Pinia stores
│   │   ├── router/            # Vue Router
│   │   ├── services/          # API client
│   │   └── assets/            # Static assets
│   ├── package.json
│   ├── vite.config.js
│   ├── Dockerfile
│   └── nginx.conf
│
├── docker-compose.yml          # Full stack setup
├── .env.example                # Environment template
└── README.md                   # This file
```

## Usage

### Adding a Provider

1. Open the dashboard at http://localhost:3000
2. Navigate to "Providers" page
3. Click "+ Add Provider"
4. Fill in the details:

**Telegram:**
```json
{
  "name": "Main Telegram",
  "type": "telegram",
  "config": {
    "bot_token": "123456:ABC-DEF...",
    "chat_id": "-1001234567890",
    "thread_id": 2  // Optional
  }
}
```

**Slack:**
```json
{
  "name": "Main Slack",
  "type": "slack",
  "config": {
    "webhook_url": "https://hooks.slack.com/services/...",
    "channel": "#deployments",  // Optional
    "username": "Git Bot"       // Optional
  }
}
```

**Mattermost:**
```json
{
  "name": "Main Mattermost",
  "type": "mattermost",
  "config": {
    "webhook_url": "https://mattermost.example.com/hooks/...",
    "channel": "devops",    // Optional
    "username": "Git Bot"   // Optional
  }
}
```

**Discord:**
```json
{
  "name": "Main Discord",
  "type": "discord",
  "config": {
    "webhook_url": "https://discord.com/api/webhooks/...",
    "username": "Git Bot",      // Optional
    "avatar_url": "https://..."  // Optional
  }
}
```

### Configuring Git Webhooks

1. Go to Settings page in the dashboard
2. Copy the webhook URL
3. In your Git platform (GitLab/GitHub/Bitbucket):
   - Navigate to Repository Settings → Webhooks
   - Paste the webhook URL
   - Select events to receive
   - Save

**Webhook URL:** `http://your-server:8000/api/webhook/git`

### API Endpoints

**Webhooks:**
- `POST /api/webhook/git` - Receive webhooks from Git platforms
- `GET /api/webhook/test` - Test webhook service

**Providers:**
- `GET /api/providers` - List all providers
- `POST /api/providers` - Create new provider
- `GET /api/providers/{id}` - Get provider details
- `PUT /api/providers/{id}` - Update provider
- `DELETE /api/providers/{id}` - Delete provider
- `POST /api/providers/{id}/test` - Test provider connection

**Events:**
- `GET /api/events` - List events (with filters)
- `GET /api/events/stats` - Get event statistics
- `DELETE /api/events` - Clear events

**Dashboard:**
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/recent-events` - Get recent events
- `GET /api/dashboard/activity-timeline` - Get activity timeline

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## Configuration

All configuration is done via environment variables. See `.env.example` for available options.

### Key Settings

- `ENVIRONMENT` - development/production
- `DATABASE_URL` - SQLite database path
- `LOG_LEVEL` - DEBUG/INFO/WARNING/ERROR
- `CORS_ORIGINS_STR` - Allowed CORS origins

## Deployment

### Production Deployment with Docker

1. Update `.env` for production
2. Build and start:
```bash
docker-compose up -d
```

3. Check logs:
```bash
docker-compose logs -f
```

4. Access services:
   - Frontend: http://your-server:3000
   - Backend: http://your-server:8000
   - API Docs: http://your-server:8000/docs

### Scaling

For high-volume deployments:
- Use PostgreSQL instead of SQLite
- Deploy multiple backend replicas
- Add a reverse proxy (Nginx, Traefik)
- Use Redis for caching
- Implement message queue (Celery, RabbitMQ)

## Troubleshooting

### Webhooks not received
- Check firewall settings
- Verify webhook URL is accessible from Git platform
- Check backend logs: `docker-compose logs backend`

### Messages not sent
- Test provider connection in dashboard
- Check provider configuration
- Review event logs in Events page

### Database issues
- Backup: `cp data/webhook_bridge.db data/webhook_bridge.db.backup`
- Reset: `rm data/webhook_bridge.db && docker-compose restart backend`

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License

## Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Documentation: See `/docs` folder

---

Built with ❤️ using FastAPI, Vue.js 3, and modern web technologies
