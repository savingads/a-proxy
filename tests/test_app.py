import unittest
import os
import sys
import tempfile
import json
from flask import session

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app
import database

class TestApp(unittest.TestCase):
    """Test cases for the Flask application"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create a temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        # Save the original DB_PATH and replace it with our test database
        self.original_db_path = database.DB_PATH
        database.DB_PATH = self.db_path
        
        # Initialize the database
        database.init_db()
        
        # Create the Flask test client
        self.app = app.create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Create a test persona to use in tests
        self.test_persona = {
            "name": "Test Persona",
            "demographic": {
                "geolocation": "40.7128, -74.0060",
                "language": "en-US",
                "country": "United States",
                "city": "New York",
                "region": "NY"
            }
        }
        self.test_persona_id = database.save_persona(self.test_persona)
    
    def tearDown(self):
        """Clean up test fixtures after each test method"""
        # Reset the DB_PATH
        database.DB_PATH = self.original_db_path
        
        # Close and remove the temporary database
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_home_page(self):
        """Test that the home page loads successfully"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_page(self):
        """Test that the dashboard page loads successfully"""
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
    
    def test_personas_list_page(self):
        """Test that the personas list page loads successfully"""
        response = self.client.get('/personas')
        self.assertEqual(response.status_code, 200)
        # Check that the test persona is in the response
        self.assertIn(b'Test Persona', response.data)
    
    def test_view_persona(self):
        """Test viewing a persona"""
        response = self.client.get(f'/view-persona/{self.test_persona_id}')
        self.assertEqual(response.status_code, 200)
        # Check that the test persona name is in the response
        self.assertIn(b'Test Persona', response.data)
        # Check that the expected data is displayed
        self.assertIn(b'United States', response.data)
        self.assertIn(b'New York', response.data)
    
    def test_edit_persona(self):
        """Test the edit persona page loads correctly"""
        response = self.client.get(f'/edit-persona/{self.test_persona_id}')
        self.assertEqual(response.status_code, 200)
        # Check that the form has the correct values
        self.assertIn(b'Test Persona', response.data)
        self.assertIn(b'United States', response.data)
        self.assertIn(b'New York', response.data)
    
    def test_update_persona(self):
        """Test updating a persona"""
        # Create form data for the update
        form_data = {
            'persona_id': self.test_persona_id,
            'persona_name': 'Updated Test Persona',
            'language': 'fr-FR',
            'country': 'France',
            'city': 'Paris',
            'region': 'Île-de-France',
            'geolocation': '48.8566, 2.3522'
        }
        
        # Send a POST request to update the persona
        response = self.client.post('/update_persona', data=form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify that the database was updated correctly rather than checking for a message
        
        # Check that the database was updated
        updated_persona = database.get_persona(self.test_persona_id)
        self.assertEqual(updated_persona['name'], 'Updated Test Persona')
        self.assertEqual(updated_persona['demographic']['language'], 'fr-FR')
        self.assertEqual(updated_persona['demographic']['country'], 'France')
        self.assertEqual(updated_persona['demographic']['city'], 'Paris')
        self.assertEqual(updated_persona['demographic']['latitude'], 48.8566)
        self.assertEqual(updated_persona['demographic']['longitude'], 2.3522)
    
    def test_save_persona(self):
        """Test saving a new persona"""
        # Create form data for the new persona
        form_data = {
            'persona_name': 'New Test Persona',
            'language': 'es-ES',
            'country': 'Spain',
            'city': 'Madrid',
            'region': 'Madrid',
            'geolocation': '40.4168, -3.7038'
        }
        
        # Check the number of personas before
        personas_before = len(database.get_all_personas())
        
        # Send a POST request to save the new persona
        response = self.client.post('/save-persona', data=form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify that a new persona was added to the database rather than checking for a message
        
        # Check that a new persona was added to the database
        personas_after = len(database.get_all_personas())
        self.assertEqual(personas_after, personas_before + 1)
        
        # Find the new persona in the database
        new_persona = None
        for persona in database.get_all_personas():
            if persona['name'] == 'New Test Persona':
                new_persona = persona
                break
        
        # Check that the new persona has the correct data
        self.assertIsNotNone(new_persona)
        
        # Get demographic data - it might be in a different format
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT language, country, city FROM demographic_data WHERE persona_id = ?",
            (new_persona['id'],)
        )
        demo_data = cursor.fetchone()
        conn.close()
        
        # Now check the values directly from the database
        self.assertEqual(demo_data[0], 'es-ES')  # language
        self.assertEqual(demo_data[1], 'Spain')  # country
        self.assertEqual(demo_data[2], 'Madrid') # city
    
    def test_delete_persona(self):
        """Test deleting a persona"""
        # Create a persona to delete
        temp_persona = {
            "name": "Persona to Delete",
            "demographic": {
                "language": "en-US"
            }
        }
        temp_persona_id = database.save_persona(temp_persona)
        
        # Check the number of personas before
        personas_before = len(database.get_all_personas())
        
        # Send a POST request to delete the persona
        response = self.client.post(f'/delete-persona/{temp_persona_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Check that the success message is in the response
        self.assertIn(b'deleted successfully', response.data)
        
        # Check that a persona was removed from the database
        personas_after = len(database.get_all_personas())
        self.assertEqual(personas_after, personas_before - 1)
        
        # Check that the deleted persona is no longer in the database
        for persona in database.get_all_personas():
            self.assertNotEqual(persona['id'], temp_persona_id)

    def test_save_psychographic_data(self):
        """Test saving psychographic data for a persona"""
        # Create form data for the psychographic update
        form_data = {
            'persona_id': self.test_persona_id,
            'interests': 'technology,travel,food',
            'personal_values': 'privacy,freedom,innovation',
            'attitudes': 'environmentally conscious',
            'lifestyle': 'Urban professional',
            'personality': 'Analytical',
            'opinions': 'pro technology regulation'
        }
        
        # Send a POST request to save the psychographic data
        response = self.client.post('/save_psychographic_data', data=form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify the database was updated correctly rather than checking for a message
        
        # Check that the database was updated
        updated_persona = database.get_persona(self.test_persona_id)
        self.assertEqual(updated_persona['psychographic']['interests'], ['technology', 'travel', 'food'])
        self.assertEqual(updated_persona['psychographic']['personal_values'], ['privacy', 'freedom', 'innovation'])
        self.assertEqual(updated_persona['psychographic']['lifestyle'], 'Urban professional')

    def test_save_behavioral_data(self):
        """Test saving behavioral data for a persona"""
        # Create form data for the behavioral update
        form_data = {
            'persona_id': self.test_persona_id,
            'browsing_habits': 'news sites,technology blogs',
            'purchase_history': 'electronics,books',
            'brand_interactions': 'Apple,Amazon',
            'device_usage': '{"mobile": 60, "desktop": 40}',
            'social_media_activity': '{"Twitter": "high", "Instagram": "medium"}',
            'content_consumption': '{"articles": "high", "videos": "medium"}'
        }
        
        # Send a POST request to save the behavioral data
        response = self.client.post('/save_behavioral_data', data=form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify the database was updated correctly rather than checking for a message
        
        # Check that the database was updated
        updated_persona = database.get_persona(self.test_persona_id)
        self.assertEqual(updated_persona['behavioral']['browsing_habits'], ['news sites', 'technology blogs'])
        self.assertEqual(updated_persona['behavioral']['purchase_history'], ['electronics', 'books'])
        # Since device_usage is stored as a JSON string in the form but parsed in the DB
        self.assertIn('mobile', updated_persona['behavioral']['device_usage'])
        self.assertIn('desktop', updated_persona['behavioral']['device_usage'])

    def test_save_contextual_data(self):
        """Test saving contextual data for a persona"""
        # Create form data for the contextual update
        form_data = {
            'persona_id': self.test_persona_id,
            'time_of_day': 'Morning',
            'day_of_week': 'Weekday',
            'season': 'Spring',
            'weather': 'Sunny',
            'device_type': 'Mobile',
            'browser_type': 'Chrome',
            'screen_size': 'Small',
            'connection_type': 'Wifi'
        }
        
        # Send a POST request to save the contextual data
        response = self.client.post('/save_contextual_data', data=form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify the database was updated correctly rather than checking for a message
        
        # Check that the database was updated
        updated_persona = database.get_persona(self.test_persona_id)
        self.assertEqual(updated_persona['contextual']['time_of_day'], 'Morning')
        self.assertEqual(updated_persona['contextual']['day_of_week'], 'Weekday')
        self.assertEqual(updated_persona['contextual']['season'], 'Spring')
        self.assertEqual(updated_persona['contextual']['browser_type'], 'Chrome')
        self.assertEqual(updated_persona['contextual']['connection_type'], 'Wifi')

if __name__ == '__main__':
    unittest.main()
