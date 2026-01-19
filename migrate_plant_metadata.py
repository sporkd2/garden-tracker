#!/usr/bin/env python3
"""
Database migration script to add plant metadata columns
Version: v3 - Add plant metadata support
"""
import sqlite3
import os

def migrate_db():
    db_path = os.environ.get('DATABASE_PATH', 'data/garden.db')

    # Ensure data directory exists
    os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else 'data', exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if metadata columns exist
    cursor.execute("PRAGMA table_info(plants)")
    columns = [col[1] for col in cursor.fetchall()]

    migrations_needed = []
    new_columns = {
        'scientific_name': 'TEXT',
        'sunlight': 'TEXT',
        'watering_needs': 'TEXT',
        'cycle': 'TEXT',
        'hardiness_zones': 'TEXT',
        'description': 'TEXT',
        'perenual_id': 'INTEGER'
    }

    for col_name, col_type in new_columns.items():
        if col_name not in columns:
            migrations_needed.append(f"ALTER TABLE plants ADD COLUMN {col_name} {col_type}")

    if migrations_needed:
        print("🌱 Applying database migrations...")
        for migration in migrations_needed:
            print(f"  - {migration}")
            cursor.execute(migration)
        conn.commit()
        print("✅ Database migrated successfully!")
    else:
        print("✅ Database is already up to date!")

    conn.close()

if __name__ == '__main__':
    migrate_db()
