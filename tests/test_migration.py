import os
import unittest
import sqlite3
import tempfile
import shutil
from datetime import datetime
import sys

# Add parent directory to path to import from parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the migrate_database module
import migrate_database

class TestDatabaseMigration(unittest.TestCase):
    """Test the database migration functionality"""
    
    def setUp(self):
        """Create a temporary directory and database for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_db_path = migrate_database.DB_PATH
        
        # Create a test database path
        self.test_db_path = os.path.join(self.temp_dir, 'test_db.db')
        migrate_database.DB_PATH = self.test_db_path
        
        # Create archive directory
        self.archive_dir = os.path.join(self.temp_dir, 'archives')
        
    def tearDown(self):
        """Clean up temporary files and restore original settings"""
        migrate_database.DB_PATH = self.original_db_path
        shutil.rmtree(self.temp_dir)
    
    def test_schema_version_tracking(self):
        """Test that the schema version is properly tracked"""
        # Create a connection to the test database
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Initial version should be 0
        self.assertEqual(migrate_database.get_db_version(cursor), 0)
        
        # Create schema_version table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS schema_version (
            id INTEGER PRIMARY KEY,
            version INTEGER NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Set version to 1
        migrate_database.set_db_version(cursor, 1)
        conn.commit()
        
        # Version should now be 1
        self.assertEqual(migrate_database.get_db_version(cursor), 1)
        
        conn.close()
    
    def test_full_migration(self):
        """Test the full migration process on a new database"""
        # Create initial tables to simulate an application with version 0
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Create personas table (needed for foreign keys)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS personas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create demographic_data table with old schema (with geolocation field)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS demographic_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            persona_id INTEGER NOT NULL,
            geolocation TEXT,
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
        
        # Insert test data
        cursor.execute('''
        INSERT INTO personas (name, created_at, updated_at)
        VALUES (?, ?, ?)
        ''', ('Test Persona', datetime.now(), datetime.now()))
        
        persona_id = cursor.lastrowid
        
        cursor.execute('''
        INSERT INTO demographic_data 
        (persona_id, geolocation, language, country, city)
        VALUES (?, ?, ?, ?, ?)
        ''', (persona_id, '42.3601,-71.0589', 'en-US', 'US', 'Boston'))
        
        conn.commit()
        
        # Run the migration
        migrate_database.migrate_database()
        
        # Verify the migration was successful
        conn = sqlite3.connect(self.test_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check schema version
        cursor.execute("SELECT version FROM schema_version")
        version_row = cursor.fetchone()
        self.assertIsNotNone(version_row, "Schema version record should exist")
        version = version_row[0]
        self.assertEqual(version, migrate_database.CURRENT_DB_VERSION)
        
        # Check that the demographic_data table has latitude and longitude
        cursor.execute("PRAGMA table_info(demographic_data)")
        columns = [column[1] for column in cursor.fetchall()]
        self.assertIn('latitude', columns)
        self.assertIn('longitude', columns)
        self.assertNotIn('geolocation', columns)
        
        # Check that the data was migrated properly
        cursor.execute('''
        SELECT * FROM demographic_data WHERE persona_id = ?
        ''', (persona_id,))
        
        row = cursor.fetchone()
        self.assertEqual(row['persona_id'], persona_id)
        self.assertAlmostEqual(row['latitude'], 42.3601, places=4)
        self.assertAlmostEqual(row['longitude'], -71.0589, places=4)
        self.assertEqual(row['language'], 'en-US')
        self.assertEqual(row['country'], 'US')
        self.assertEqual(row['city'], 'Boston')
        
        # Check that the archive tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='archived_websites'")
        self.assertIsNotNone(cursor.fetchone())
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mementos'")
        self.assertIsNotNone(cursor.fetchone())
        
        conn.close()
    
    def test_idempotent_migration(self):
        """Test that running the migration multiple times is safe"""
        # Create the schema_version table directly so we can verify the migration behavior
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS schema_version (
            id INTEGER PRIMARY KEY,
            version INTEGER NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
        conn.close()
        
        # Run migration once
        migrate_database.migrate_database()
        
        # Get current version
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT version FROM schema_version")
        version_row = cursor.fetchone()
        self.assertIsNotNone(version_row, "Schema version record should exist after first migration")
        first_version = version_row[0]
        conn.close()
        
        # Run migration again
        migrate_database.migrate_database()
        
        # Get version after second migration
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT version FROM schema_version")
        version_row = cursor.fetchone()
        self.assertIsNotNone(version_row, "Schema version record should exist after second migration")
        second_version = version_row[0]
        conn.close()
        
        # Versions should match and equal the current version
        self.assertEqual(first_version, second_version)
        self.assertEqual(first_version, migrate_database.CURRENT_DB_VERSION)

if __name__ == '__main__':
    unittest.main()
