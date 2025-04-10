import sqlite3
import os
from datetime import datetime

DB_PATH = 'personas.db'
CURRENT_DB_VERSION = 2  # Increment this when adding new migrations

def get_db_version(cursor):
    """Get the current database version from the schema_version table"""
    try:
        cursor.execute("SELECT version FROM schema_version")
        version = cursor.fetchone()
        return version[0] if version else 0
    except sqlite3.OperationalError:
        # Table doesn't exist yet
        return 0

def set_db_version(cursor, version):
    """Update the database version in the schema_version table"""
    cursor.execute("INSERT OR REPLACE INTO schema_version (id, version, updated_at) VALUES (1, ?, ?)",
                  (version, datetime.now()))
    # Make sure the changes are committed before returning
    return True

def migrate_database():
    """
    Migrate the database to the latest schema:
    1. Separate latitude and longitude fields (version 1)
    2. Add archived_websites and mementos tables (version 2)
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Create schema_version table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS schema_version (
            id INTEGER PRIMARY KEY,
            version INTEGER NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Get current database version
        db_version = get_db_version(cursor)
        print(f"Current database version: {db_version}")
        
        # Run migrations only if needed
        if db_version >= CURRENT_DB_VERSION:
            print(f"Database is already at the latest version ({CURRENT_DB_VERSION})")
            return
        # Migration 1: Separate latitude and longitude fields
        if db_version < 1:
            print("Running migration 1: Separating latitude and longitude fields...")
            
            # Check if demographic_data table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='demographic_data'")
            demographic_table_exists = cursor.fetchone() is not None
            
            if demographic_table_exists:
                # Check if we need to migrate the geolocation field to latitude/longitude
                cursor.execute("PRAGMA table_info(demographic_data)")
                columns = [column[1] for column in cursor.fetchall()]
                
                if 'geolocation' in columns and 'latitude' not in columns:
                    print("Migrating demographic_data table to separate latitude and longitude fields...")
                    
                    # Step 1: Create a new table with the updated schema
                    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS demographic_data_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        persona_id INTEGER NOT NULL,
                        latitude REAL,
                        longitude REAL,
                        language TEXT,
                        country TEXT,
                        city TEXT,
                        region TEXT,
                        age INTEGER,
                        gender TEXT,
                        education TEXT,
                        income TEXT,
                        occupation TEXT,
                        FOREIGN KEY (persona_id) REFERENCES personas (id) ON DELETE CASCADE
                    )
                    ''')

                    # Step 2: Copy data from the old table to the new table
                    cursor.execute('SELECT * FROM demographic_data')
                    rows = cursor.fetchall()
                    for row in rows:
                        # Extract latitude and longitude from the geolocation field
                        geolocation = row[2]  # Assuming geolocation is the 3rd column
                        latitude, longitude = None, None
                        if geolocation:
                            try:
                                latitude, longitude = map(float, geolocation.split(','))
                            except ValueError:
                                pass  # Handle invalid geolocation format gracefully

                        # Insert data into the new table
                        cursor.execute('''
                        INSERT INTO demographic_data_new (
                            persona_id, latitude, longitude, language, country, city, region, age, gender, education, income, occupation
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            row[1],  # persona_id
                            latitude,
                            longitude,
                            row[3],  # language
                            row[4],  # country
                            row[5],  # city
                            row[6],  # region
                            row[7],  # age
                            row[8],  # gender
                            row[9],  # education
                            row[10], # income
                            row[11]  # occupation
                        ))

                    # Step 3: Drop the old table and rename the new table
                    cursor.execute('DROP TABLE demographic_data')
                    cursor.execute('ALTER TABLE demographic_data_new RENAME TO demographic_data')
                    print("Demographic data migration completed successfully.")
                else:
                    print("Demographic data table already has the latest schema.")
            else:
                print("Demographic data table doesn't exist yet. No migration needed.")
                
            # Update database version after successful migration
            set_db_version(cursor, 1)
            conn.commit()
            print("Database migrated to version 1 successfully.")
        
        # Migration 2: Add archive functionality tables
        if db_version < 2:
            print("Running migration 2: Adding archive functionality tables...")
            
            # Create archived_websites table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS archived_websites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uri_r TEXT NOT NULL,
                persona_id INTEGER,
                archive_type TEXT NOT NULL,
                archive_location TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (persona_id) REFERENCES personas (id) ON DELETE SET NULL
            )
            ''')
            
            # Create mementos table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS mementos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                archived_website_id INTEGER NOT NULL,
                memento_datetime TIMESTAMP NOT NULL,
                memento_location TEXT NOT NULL,
                http_status INTEGER,
                content_type TEXT,
                content_length INTEGER,
                headers TEXT,
                screenshot_path TEXT,
                internet_archive_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (archived_website_id) REFERENCES archived_websites (id) ON DELETE CASCADE
            )
            ''')

            # Create archives directory if it doesn't exist
            if not os.path.exists('archives'):
                os.makedirs('archives')
                print("Created archives directory")
                
            # Update database version after successful migration
            set_db_version(cursor, 2)
            conn.commit()
            print("Database migrated to version 2 successfully.")

        # Verify final database version
        final_version = get_db_version(cursor)
        if final_version == CURRENT_DB_VERSION:
            print(f"✅ Database migration completed successfully (now at version {final_version}).")
        else:
            print(f"⚠️ Database migration incomplete. Expected version {CURRENT_DB_VERSION}, but got {final_version}.")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error during migration: {e}")
        raise

    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
