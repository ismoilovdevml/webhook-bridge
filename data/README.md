# Data Directory

This directory stores the SQLite database file.

**Important:**
- Database files are NOT tracked in git
- The database is automatically created on first startup
- Location: `data/webhook_bridge.db`

**Docker Setup:**
- This directory is mounted as a volume in docker-compose
- Ensures data persistence across container restarts

**Clean Setup:**
- Delete `webhook_bridge.db` to reset to clean state
- Run `docker-compose up -d` to recreate database
- Admin user will be auto-created from .env settings
