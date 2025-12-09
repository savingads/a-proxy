import unittest
import os
import sys
import tempfile
from bs4 import BeautifulSoup

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app
import database
from database.connection import DatabaseConnection

class TestTemplates(unittest.TestCase):
    """Test cases for the template structure and navigation consistency"""

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
    
    def test_home_page_extends_base_template(self):
        """Test that the home page extends the base template"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check that the response includes content from base.html
        self.assertIn(b'<div class="container-fluid">', response.data)
        
        # Check that it includes the sidebar
        self.assertIn(b'<div class="sidebar', response.data)
    
    def test_personas_page_extends_base_template(self):
        """Test that the personas page extends the base template"""
        response = self.client.get('/personas')
        self.assertEqual(response.status_code, 200)
        
        # Parse the HTML
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for sidebar navigation
        sidebar = soup.select('.sidebar')
        self.assertTrue(len(sidebar) > 0, "Sidebar not found in personas page")
        
        # Check for navigation links
        nav_links = soup.select('.sidebar .nav-link')
        self.assertTrue(len(nav_links) > 0, "Navigation links not found in sidebar")
    
    def test_persona_view_page_extends_base_template(self):
        """Test that the persona view page extends the base template"""
        response = self.client.get(f'/persona/{self.test_persona_id}')
        self.assertEqual(response.status_code, 200)

        # Parse the HTML
        soup = BeautifulSoup(response.data, 'html.parser')

        # Check for sidebar navigation
        sidebar = soup.select('.sidebar')
        self.assertTrue(len(sidebar) > 0, "Sidebar not found in persona view page")
    
    def test_persona_edit_page_extends_base_template(self):
        """Test that the persona edit page extends the base template"""
        response = self.client.get(f'/edit-persona/{self.test_persona_id}')
        self.assertEqual(response.status_code, 200)
        
        # Parse the HTML
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for sidebar navigation
        sidebar = soup.select('.sidebar')
        self.assertTrue(len(sidebar) > 0, "Sidebar not found in persona edit page")
    
    def test_journeys_page_extends_base_template(self):
        """Test that the journeys page extends the base template"""
        response = self.client.get('/journeys')
        self.assertEqual(response.status_code, 200)
        
        # Parse the HTML
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for sidebar navigation
        sidebar = soup.select('.sidebar')
        self.assertTrue(len(sidebar) > 0, "Sidebar not found in journeys page")
    
    def test_create_journey_page_extends_base_template(self):
        """Test that the create journey page extends the base template"""
        response = self.client.get('/journey/create')
        self.assertEqual(response.status_code, 200)
        
        # Parse the HTML
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for sidebar navigation
        sidebar = soup.select('.sidebar')
        self.assertTrue(len(sidebar) > 0, "Sidebar not found in create journey page")
    
    def test_edit_journey_page_extends_base_template(self):
        """Test that the edit journey page extends the base template"""
        # First create a journey to edit
        test_journey = {
            "name": "Test Journey", 
            "description": "Test journey description", 
            "journey_type": "research"
        }
        journey_id = database.create_journey(**test_journey)
        
        # Now try to access the edit page
        response = self.client.get(f'/journey/{journey_id}/edit')
        self.assertEqual(response.status_code, 200)
        
        # Parse the HTML
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for sidebar navigation
        sidebar = soup.select('.sidebar')
        self.assertTrue(len(sidebar) > 0, "Sidebar not found in edit journey page")
        
        # Check that form contains the journey data
        name_input = soup.select('input#name')
        self.assertTrue(len(name_input) > 0, "Journey name input not found")
        self.assertEqual(name_input[0].get('value'), "Test Journey")
        
        # Check for the Danger Zone section
        danger_zone = soup.select('.card.border-danger')
        self.assertTrue(len(danger_zone) > 0, "Danger zone card not found in edit journey page")
    
    def test_browse_as_page_extends_base_template(self):
        """Test that the browse-as (now interact-as) page extends the base template"""
        # /browse-as redirects to /interact-as, so follow redirects
        response = self.client.get('/interact-as')
        self.assertEqual(response.status_code, 200)

        # Parse the HTML
        soup = BeautifulSoup(response.data, 'html.parser')

        # Check for sidebar navigation
        sidebar = soup.select('.sidebar')
        self.assertTrue(len(sidebar) > 0, "Sidebar not found in interact-as page")
    
    def test_archives_page_extends_base_template(self):
        """Test that the archives page extends the base template"""
        response = self.client.get('/archives')
        self.assertEqual(response.status_code, 200)
        
        # Parse the HTML
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for sidebar navigation
        sidebar = soup.select('.sidebar')
        self.assertTrue(len(sidebar) > 0, "Sidebar not found in archives page")
    
    def test_consistent_navigation_links(self):
        """Test that all pages have the same navigation links in the sidebar"""
        # Note: /journey/create uses a different template with dropdowns, so exclude it
        pages = [
            '/',
            '/personas',
            '/interact-as',
            '/journeys',
            '/archives'
        ]
        
        # Get navigation links from the first page as a reference
        response = self.client.get(pages[0])
        soup = BeautifulSoup(response.data, 'html.parser')
        reference_links = [link.get('href') for link in soup.select('.sidebar .nav-link')]
        
        # Check that all other pages have the same navigation links
        for page in pages[1:]:
            response = self.client.get(page)
            soup = BeautifulSoup(response.data, 'html.parser')
            page_links = [link.get('href') for link in soup.select('.sidebar .nav-link')]
            self.assertEqual(reference_links, page_links, f"Navigation links on {page} don't match the reference")

if __name__ == '__main__':
    unittest.main()
