"""Database initialization script.

Run this script to create the database schema:
    python -m downloader.db_init
"""

import sys
from downloader.database import engine
from downloader.models import Base


def init_db():
    """Create all database tables."""
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ Database initialized successfully")
        print("✓ Table 'downloads' created in schema")
        return True
    except Exception as e:
        print(f"✗ Error initializing database: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    success = init_db()
    sys.exit(0 if success else 1)
