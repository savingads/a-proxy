import unittest
import tempfile
import os
import json
import sqlite3
import sys
from datetime import datetime

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
from database import connection as db_connection

class TestDatabase(unittest.TestCase):
    """Test cases for database operations"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create a temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp()

        # Save the original DB_PATH and replace it with our test database
        self.original_db_path = db_connection.DEFAULT_DB_PATH
        db_connection.DEFAULT_DB_PATH = self.db_path

        # Reset the global database instance to use new path
        db_connection._db_instance = None

        # Initialize the database
        database.init_db()
        database.create_persona_tables()

    def tearDown(self):
        """Clean up test fixtures after each test method"""
        # Reset the DB_PATH
        db_connection.DEFAULT_DB_PATH = self.original_db_path
        db_connection._db_instance = None

        # Close and remove the temporary database
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_init_db(self):
        """Test that database initialization creates the expected tables"""
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        # Query for all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Check that all expected tables exist
        expected_tables = [
            'personas', 
            'demographic_data', 
            'psychographic_data', 
            'behavioral_data', 
            'contextual_data',
            'archived_websites',
            'mementos'
        ]
        
        for table in expected_tables:
            self.assertIn(table, tables)
        
        conn.close()
    
    def test_save_and_get_persona(self):
        """Test saving a persona and then retrieving it"""
        # Create test persona data
        test_persona = {
            "name": "Test Persona",
            "demographic": {
                "geolocation": "40.7128, -74.0060",
                "language": "en-US",
                "country": "United States",
                "city": "New York",
                "region": "NY",
                "age": 30,
                "gender": "Female",
                "education": "Bachelor's",
                "income": "100000",
                "occupation": "Software Engineer"
            },
            "psychographic": {
                "interests": ["technology", "travel", "food"],
                "personal_values": ["privacy", "freedom", "innovation"],
                "attitudes": ["environmentally conscious"],
                "lifestyle": "Urban professional",
                "personality": "Analytical",
                "opinions": ["pro technology regulation"]
            },
            "behavioral": {
                "browsing_habits": ["news sites", "technology blogs"],
                "purchase_history": ["electronics", "books"],
                "brand_interactions": ["Apple", "Amazon"],
                "device_usage": {"mobile": 60, "desktop": 40},
                "social_media_activity": {"Twitter": "high", "Instagram": "medium"},
                "content_consumption": {"articles": "high", "videos": "medium"}
            },
            "contextual": {
                "time_of_day": "Morning",
                "day_of_week": "Weekday",
                "season": "Spring",
                "weather": "Sunny",
                "device_type": "Mobile",
                "browser_type": "Chrome",
                "screen_size": "Small",
                "connection_type": "Wifi"
            }
        }
        
        # Save the persona
        persona_id = database.save_persona(test_persona)
        
        # Get the saved persona
        saved_persona = database.get_persona(persona_id)
        
        # Check persona name
        self.assertEqual(saved_persona['name'], test_persona['name'])
        
        # Check demographic data
        self.assertEqual(saved_persona['demographic']['language'], test_persona['demographic']['language'])
        self.assertEqual(saved_persona['demographic']['country'], test_persona['demographic']['country'])
        self.assertEqual(saved_persona['demographic']['city'], test_persona['demographic']['city'])
        self.assertEqual(saved_persona['demographic']['region'], test_persona['demographic']['region'])
        self.assertEqual(saved_persona['demographic']['age'], test_persona['demographic']['age'])
        
        # Check latitude and longitude were correctly parsed from geolocation
        self.assertEqual(saved_persona['demographic']['latitude'], 40.7128)
        self.assertEqual(saved_persona['demographic']['longitude'], -74.0060)
        
        # Check psychographic data (lists are stored as JSON)
        self.assertEqual(saved_persona['psychographic']['interests'], test_persona['psychographic']['interests'])
        self.assertEqual(saved_persona['psychographic']['personal_values'], test_persona['psychographic']['personal_values'])
        
        # Check behavioral data (complex objects stored as JSON)
        self.assertEqual(saved_persona['behavioral']['device_usage'], test_persona['behavioral']['device_usage'])
        self.assertEqual(saved_persona['behavioral']['social_media_activity'], test_persona['behavioral']['social_media_activity'])
        
        # Check contextual data
        self.assertEqual(saved_persona['contextual']['time_of_day'], test_persona['contextual']['time_of_day'])
        self.assertEqual(saved_persona['contextual']['browser_type'], test_persona['contextual']['browser_type'])
    
    def test_delete_persona(self):
        """Test deleting a persona"""
        # Create a simple test persona
        test_persona = {
            "name": "Delete Test",
            "demographic": {
                "language": "en-US"
            }
        }
        
        # Save the persona
        persona_id = database.save_persona(test_persona)
        
        # Make sure it exists
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM personas WHERE id = ?", (persona_id,))
        self.assertIsNotNone(cursor.fetchone())
        
        # Delete the persona
        database.delete_persona(persona_id)
        
        # Make sure it's gone
        cursor.execute("SELECT id FROM personas WHERE id = ?", (persona_id,))
        self.assertIsNone(cursor.fetchone())
        
        conn.close()
    
    def test_get_all_personas(self):
        """Test retrieving all personas"""
        # Create a few test personas
        test_personas = [
            {"name": "Test 1", "demographic": {"language": "en-US"}},
            {"name": "Test 2", "demographic": {"language": "fr-FR"}},
            {"name": "Test 3", "demographic": {"language": "de-DE"}}
        ]

        # Save all personas
        for persona in test_personas:
            database.save_persona(persona)

        # Retrieve all personas (now returns dict with pagination)
        result = database.get_all_personas()
        all_personas = result.get('personas', [])

        # Check that we have at least 3 personas
        self.assertGreaterEqual(len(all_personas), 3)

        # Check that our test personas are in the result
        # (by checking for their names and languages)
        found_test_personas = 0
        for persona in all_personas:
            if persona['name'] in ["Test 1", "Test 2", "Test 3"]:
                found_test_personas += 1

        self.assertEqual(found_test_personas, 3)
    
    def test_archived_website_and_memento(self):
        """Test saving and retrieving archived websites and mementos"""
        # Create a test website archive
        url = "https://example.com"
        archive_type = "filesystem"
        archive_location = "archives/test_hash"
        
        # Save the archived website
        archived_website_id = database.save_archived_website(
            url=url,
            archive_type=archive_type,
            archive_location=archive_location
        )
        
        # Create a test memento
        memento_location = "archives/test_hash/20250330120000"
        http_status = 200
        content_type = "text/html"
        content_length = 12345
        headers = {"Content-Type": "text/html", "Server": "Test"}
        screenshot_path = "screenshots/test.png"
        
        # Save the memento
        memento_id = database.save_memento(
            archived_website_id=archived_website_id,
            memento_location=memento_location,
            http_status=http_status,
            content_type=content_type,
            content_length=content_length,
            headers=headers,
            screenshot_path=screenshot_path
        )
        
        # Retrieve the archived website
        website = database.get_archived_website(archived_website_id)
        
        # Check that it has the correct data
        self.assertEqual(website['uri_r'], url)
        self.assertEqual(website['archive_type'], archive_type)
        self.assertEqual(website['archive_location'], archive_location)
        
        # Retrieve the memento
        memento = database.get_memento(memento_id)
        
        # Check that it has the correct data
        self.assertEqual(memento['memento_location'], memento_location)
        self.assertEqual(memento['http_status'], http_status)
        self.assertEqual(memento['content_type'], content_type)
        self.assertEqual(memento['content_length'], content_length)
        self.assertEqual(memento['headers'], headers)
        self.assertEqual(memento['screenshot_path'], screenshot_path)
        
        # Check that the memento is related to the correct website
        self.assertEqual(memento['uri_r'], url)
        
    def test_delete_archived_website(self):
        """Test deleting an archived website and its associated mementos"""
        # Create a test website archive
        url = "https://example.com/delete-test"
        archive_type = "filesystem"
        archive_location = "archives/delete_test_hash"
        
        # Save the archived website
        archived_website_id = database.save_archived_website(
            url=url,
            archive_type=archive_type,
            archive_location=archive_location
        )
        
        # Create a test memento
        memento_location = "archives/delete_test_hash/20250330120000"
        memento_id = database.save_memento(
            archived_website_id=archived_website_id,
            memento_location=memento_location,
            http_status=200
        )
        
        # Verify the archived website and memento exist
        self.assertIsNotNone(database.get_archived_website(archived_website_id))
        self.assertIsNotNone(database.get_memento(memento_id))
        
        # Delete the archived website
        result = database.delete_archived_website(archived_website_id)
        self.assertTrue(result)
        
        # Verify the archived website no longer exists
        self.assertIsNone(database.get_archived_website(archived_website_id))
        
        # Verify the memento was also deleted (cascade delete)
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM mementos WHERE id = ?", (memento_id,))
        self.assertIsNone(cursor.fetchone())
        conn.close()

if __name__ == '__main__':
    unittest.main()
