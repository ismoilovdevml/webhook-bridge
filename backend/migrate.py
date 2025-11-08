"""Simple migration script to add new columns."""

import sqlite3
from pathlib import Path
import sys

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

DB_PATH = Path("webhook_bridge.db")


def migrate():
    """Add filters column to providers table and update indexes."""
    # Initialize database tables first
    from app.database import init_db

    print("Initializing database tables...")
    init_db()
    print("  ✓ Tables created")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Running migrations...")

    # Check if filters column exists
    cursor.execute("PRAGMA table_info(providers)")
    columns = [col[1] for col in cursor.fetchall()]

    if "filters" not in columns:
        print("  - Adding 'filters' column to providers table")
        cursor.execute("ALTER TABLE providers ADD COLUMN filters TEXT")
        conn.commit()
        print("  ✓ Added filters column")
    else:
        print("  ✓ filters column already exists")

    # Create api_keys table if not exists
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used_at TIMESTAMP
        )
    """
    )
    conn.commit()
    print("  ✓ api_keys table created")

    # Create indexes for events table
    indexes_to_create = [
        ("idx_platform_event_type", "events", "platform, event_type"),
        ("idx_status_created_at", "events", "status, created_at"),
        ("idx_project_created_at", "events", "project, created_at"),
        ("idx_provider_status", "events", "provider_id, status"),
    ]

    for idx_name, table, columns in indexes_to_create:
        try:
            cursor.execute(
                f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({columns})"
            )
            print(f"  ✓ Created index {idx_name}")
        except sqlite3.OperationalError:
            print(f"  ✓ Index {idx_name} already exists")

    conn.commit()
    conn.close()

    print("✓ Migration completed successfully!")


if __name__ == "__main__":
    migrate()
