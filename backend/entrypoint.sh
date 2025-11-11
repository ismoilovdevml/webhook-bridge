#!/bin/bash
# Docker entrypoint script for backend
# Handles database initialization and migrations automatically

set -e

echo "🚀 Starting Webhook Bridge Backend..."

# Wait for database file to be ready (if using SQLite)
if [[ "$DATABASE_URL" == *"sqlite"* ]]; then
    echo "📦 Using SQLite database"

    # Create data directory if doesn't exist
    DB_DIR=$(dirname "${DATABASE_URL#sqlite:///}")
    if [ "$DB_DIR" != "." ] && [ ! -d "$DB_DIR" ]; then
        mkdir -p "$DB_DIR"
        echo "   ✓ Created database directory: $DB_DIR"
    fi
fi

# Run database initialization/migrations
echo "🗄️  Initializing database..."
python3 -c "
from app.database import init_db
from app.utils.logger import get_logger

logger = get_logger('entrypoint')
try:
    init_db()
    logger.info('Database initialized successfully')
except Exception as e:
    logger.error(f'Failed to initialize database: {e}')
    raise
"

echo "   ✓ Database ready"

# Initialize admin user
echo "👤 Checking admin user..."
python3 -c "
from app.database import SessionLocal
from app.utils.init_admin import init_admin_user
from app.utils.logger import get_logger

logger = get_logger('entrypoint')
try:
    db = SessionLocal()
    init_admin_user(db)
    db.close()
    logger.info('Admin user initialized')
except Exception as e:
    logger.error(f'Failed to initialize admin user: {e}')
"

echo "   ✓ Admin user ready"

echo ""
echo "✨ Backend initialization complete!"
echo ""

# Start the application
exec "$@"
