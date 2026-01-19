#!/usr/bin/env python3
"""
Database Migration Script for Garden Tracker
Current Version: v2 (2024-01-19)

MIGRATION HISTORY:
- v1: Initial schema (name, type, planted_date, location, watering_frequency, last_watered)
- v2: Added bed_row, bed_col, planting_area columns for visual garden layout
"""

import sqlite3
import sys
import os

CURRENT_VERSION = 2

def get_db_path():
    """Get database path from environment or default location"""
    return os.environ.get('DATABASE_PATH', 'data/garden.db')

def check_column_exists(cursor, table, column):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns

def get_schema_version(cursor):
    """Get current schema version"""
    try:
        cursor.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
        result = cursor.fetchone()
        return result[0] if result else 0
    except sqlite3.OperationalError:
        # schema_version table doesn't exist yet
        return 0

def set_schema_version(cursor, version):
    """Set schema version"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('INSERT INTO schema_version (version) VALUES (?)', (version,))

def migrate():
    """Run database migrations"""
    db_path = get_db_path()
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("   Run the app first to create the database, then run migrations.")
        sys.exit(1)
    
    print(f"🔄 Starting migration on {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    current_version = get_schema_version(cursor)
    print(f"   Current database version: v{current_version}")
    print(f"   Target version: v{CURRENT_VERSION}")
    
    if current_version >= CURRENT_VERSION:
        print("\n✅ Database is up to date! No migrations needed.")
        conn.close()
        return
    
    migrations_applied = 0
    
    # Migration to v1: Ensure base schema exists
    if current_version < 1:
        print("\n📦 Applying v1 migrations (base schema)...")
        # Base schema is created by app.py init_db(), just mark as done
        set_schema_version(cursor, 1)
        migrations_applied += 1
        print("  ✓ Base schema confirmed")
    
    # Migration to v2: Add garden bed layout columns
    if current_version < 2:
        print("\n📦 Applying v2 migrations (garden bed layout)...")
        
        if not check_column_exists(cursor, 'plants', 'bed_row'):
            print("  ➜ Adding bed_row column...")
            cursor.execute('ALTER TABLE plants ADD COLUMN bed_row INTEGER')
        else:
            print("  ✓ bed_row column already exists")
        
        if not check_column_exists(cursor, 'plants', 'bed_col'):
            print("  ➜ Adding bed_col column...")
            cursor.execute('ALTER TABLE plants ADD COLUMN bed_col INTEGER')
        else:
            print("  ✓ bed_col column already exists")
        
        if not check_column_exists(cursor, 'plants', 'planting_area'):
            print("  ➜ Adding planting_area column...")
            cursor.execute('ALTER TABLE plants ADD COLUMN planting_area TEXT')
        else:
            print("  ✓ planting_area column already exists")
        
        set_schema_version(cursor, 2)
        migrations_applied += 1
        print("  ✓ Garden bed layout features added")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Migration complete! Applied {migrations_applied} version(s).")
    print(f"   Database is now at v{CURRENT_VERSION}")
    print("\n📌 Next steps:")
    print("   1. Restart your Docker container: docker-compose restart")
    print("   2. Or if you updated app.py: docker-compose down && docker-compose up -d --build")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
