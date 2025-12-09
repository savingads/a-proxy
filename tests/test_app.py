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
from database.connection import get_db, DatabaseConnection

class TestApp(unittest.TestCase):
    """Test cases for the Flask application"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create a temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp()

        # Save the original db instance and replace it with our test database
        import database.connection as conn_module
        self.original_db_instance = conn_module._db_instance
        conn_module._db_instance = DatabaseConnection(self.db_path)

        # Reset repository singletons to use new connection
        database._persona_repo = None
        database._journey_repo = None
        database._archive_repo = None
        database._user_repo = None
        database._settings_repo = None

        # Initialize the database
        database.init_db()
        database.create_persona_tables()
        database.init_settings_table()
        database.init_user_table()

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
        # Reset the db instance
        import database.connection as conn_module
        conn_module._db_instance = self.original_db_instance

        # Reset repository singletons
        database._persona_repo = None
        database._journey_repo = None
        database._archive_repo = None
        database._user_repo = None
        database._settings_repo = None

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
        response = self.client.get(f'/persona/{self.test_persona_id}')
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
        # Create form data for the update (new API uses latitude/longitude directly)
        form_data = {
            'persona_name': 'Updated Test Persona',
            'language': 'fr-FR',
            'country': 'France',
            'city': 'Paris',
            'region': 'Ile-de-France',
            'latitude': '48.8566',
            'longitude': '2.3522'
        }

        # Send a POST request to update the persona via edit-persona route
        response = self.client.post(f'/edit-persona/{self.test_persona_id}', data=form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

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
        # Create form data for the new persona (using new API field names)
        form_data = {
            'persona_name': 'New Test Persona',
            'language': 'es-ES',
            'country': 'Spain',
            'city': 'Madrid',
            'region': 'Madrid',
            'latitude': '40.4168',
            'longitude': '-3.7038'
        }

        # Check the number of personas before
        personas_before = len(database.get_all_personas())

        # Send a POST request to create the new persona via create-persona route
        response = self.client.post('/create-persona', data=form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

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

        # Get demographic data directly from the database
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
    
    def test_journey_browse_page(self):
        """Test that the journey browse page loads successfully"""
        # Create a test journey
        test_journey = {
            "name": "Test Browse Journey", 
            "description": "Test journey for browsing", 
            "journey_type": "research"
        }
        journey_id = database.create_journey(**test_journey)
        
        # Access the journey browse page
        response = self.client.get(f'/journey/{journey_id}/browse')
        self.assertEqual(response.status_code, 200)
        
        # Check that the page contains the journey name
        self.assertIn(b'Test Browse Journey', response.data)
        
        # Check that the page contains the browser iframe
        self.assertIn(b'<iframe name="browser-frame" id="browser-frame"', response.data)
    
    def test_journey_edit_page(self):
        """Test that the journey edit page loads successfully"""
        # Create a test journey
        test_journey = {
            "name": "Test Edit Journey", 
            "description": "Test journey for editing", 
            "journey_type": "research"
        }
        journey_id = database.create_journey(**test_journey)
        
        # Access the journey edit page
        response = self.client.get(f'/journey/{journey_id}/edit')
        self.assertEqual(response.status_code, 200)
        
        # Check that the page contains the journey name
        self.assertIn(b'Test Edit Journey', response.data)
        
        # Check that the form has the correct values
        self.assertIn(b'value="Test Edit Journey"', response.data)
        self.assertIn(b'Test journey for editing', response.data)

    def test_save_psychographic_data(self):
        """Test saving psychographic data for a persona"""
        # Create form data for the psychographic update (using new API field format)
        form_data = {
            'persona_name': 'Test Persona',
            'psychographic_interests': 'technology, travel, food',
            'psychographic_personal_values': 'privacy, freedom, innovation',
            'psychographic_attitudes': 'environmentally conscious',
            'psychographic_lifestyle': 'Urban professional',
            'psychographic_personality': 'Analytical',
            'psychographic_opinions': 'pro technology regulation'
        }

        # Send a POST request via edit-persona route
        response = self.client.post(f'/edit-persona/{self.test_persona_id}', data=form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check that the database was updated
        updated_persona = database.get_persona(self.test_persona_id)
        self.assertEqual(updated_persona['psychographic']['interests'], ['technology', 'travel', 'food'])
        self.assertEqual(updated_persona['psychographic']['personal_values'], ['privacy', 'freedom', 'innovation'])
        self.assertEqual(updated_persona['psychographic']['lifestyle'], 'Urban professional')

    def test_save_behavioral_data(self):
        """Test saving behavioral data for a persona"""
        # Create form data for the behavioral update (using new API field format)
        form_data = {
            'persona_name': 'Test Persona',
            'behavioral_browsing_habits': 'news sites, technology blogs',
            'behavioral_purchase_history': 'electronics, books',
            'behavioral_brand_interactions': 'Apple, Amazon',
            'behavioral_device_usage': '{"mobile": 60, "desktop": 40}',
            'behavioral_social_media_activity': '{"Twitter": "high", "Instagram": "medium"}',
            'behavioral_content_consumption': '{"articles": "high", "videos": "medium"}'
        }

        # Send a POST request via edit-persona route
        response = self.client.post(f'/edit-persona/{self.test_persona_id}', data=form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check that the database was updated
        updated_persona = database.get_persona(self.test_persona_id)
        self.assertEqual(updated_persona['behavioral']['browsing_habits'], ['news sites', 'technology blogs'])
        self.assertEqual(updated_persona['behavioral']['purchase_history'], ['electronics', 'books'])
        # device_usage is stored as a JSON dict
        self.assertIn('mobile', updated_persona['behavioral']['device_usage'])
        self.assertIn('desktop', updated_persona['behavioral']['device_usage'])

    def test_save_contextual_data(self):
        """Test saving contextual data for a persona"""
        # Create form data for the contextual update (using new API field format)
        form_data = {
            'persona_name': 'Test Persona',
            'contextual_time_of_day': 'Morning',
            'contextual_day_of_week': 'Weekday',
            'contextual_season': 'Spring',
            'contextual_weather': 'Sunny',
            'contextual_device_type': 'Mobile',
            'contextual_browser_type': 'Chrome',
            'contextual_screen_size': 'Small',
            'contextual_connection_type': 'Wifi'
        }

        # Send a POST request via edit-persona route
        response = self.client.post(f'/edit-persona/{self.test_persona_id}', data=form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check that the database was updated
        updated_persona = database.get_persona(self.test_persona_id)
        self.assertEqual(updated_persona['contextual']['time_of_day'], 'Morning')
        self.assertEqual(updated_persona['contextual']['day_of_week'], 'Weekday')
        self.assertEqual(updated_persona['contextual']['season'], 'Spring')
        self.assertEqual(updated_persona['contextual']['browser_type'], 'Chrome')
        self.assertEqual(updated_persona['contextual']['connection_type'], 'Wifi')

if __name__ == '__main__':
    unittest.main()
