"""
Mock implementation of the Persona Client for testing without the API service
"""
import logging
import json
import os
from datetime import datetime
from utils.persona_client import ExtendedPersonaClient

# Setup logging
logger = logging.getLogger(__name__)

class MockPersonaClient(ExtendedPersonaClient):
    """Mock client that doesn't require an actual API connection"""
    
    def __init__(self, *args, **kwargs):
        """Initialize with sample data rather than connection params"""
        # Skip parent initialization to avoid connection attempts
        self.personas = {}
        self.next_id = 1
        
        # Add some sample personas if specified
        if kwargs.get('use_samples', True):
            self._add_sample_personas()
    
    def _add_sample_personas(self):
        """Add some sample personas for testing"""
        samples = [
            {
                "name": "Tech Enthusiast",
                "demographic": {
                    "latitude": 37.7749,
                    "longitude": -122.4194,
                    "language": "en-US",
                    "country": "United States",
                    "city": "San Francisco",
                    "region": "California",
                    "age": 28,
                    "gender": "male",
                    "education": "Bachelor's degree",
                    "income": "75000-100000",
                    "occupation": "Software Developer"
                },
                "psychographic": {
                    "interests": ["technology", "programming", "gaming", "science fiction"],
                    "personal_values": ["innovation", "knowledge", "creativity"],
                    "attitudes": ["early adopter", "tech optimist"],
                    "lifestyle": "Digital nomad who works remotely",
                    "personality": "Analytical, curious, and forward-thinking",
                    "opinions": ["AI will transform society", "Open source is important"]
                },
                "behavioral": {
                    "browsing_habits": ["tech news", "programming forums", "product reviews"],
                    "purchase_history": ["electronics", "digital subscriptions", "tech gadgets"],
                    "brand_interactions": ["Apple", "Google", "Microsoft", "Tesla"],
                    "device_usage": {"smartphone": "heavy", "laptop": "heavy", "tablet": "moderate"},
                    "social_media_activity": {"Twitter": "high", "LinkedIn": "medium", "Facebook": "low"},
                    "content_consumption": {"tech blogs": "daily", "videos": "weekly", "podcasts": "daily"}
                },
                "contextual": {
                    "time_of_day": "evening",
                    "day_of_week": "weekday",
                    "season": "all",
                    "weather": "any",
                    "device_type": "desktop",
                    "browser_type": "chrome",
                    "screen_size": "1920x1080",
                    "connection_type": "wifi"
                }
            },
            {
                "name": "Health Conscious Parent",
                "demographic": {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "language": "en-US",
                    "country": "United States", 
                    "city": "New York",
                    "region": "New York",
                    "age": 35,
                    "gender": "female",
                    "education": "Master's degree",
                    "income": "100000-150000", 
                    "occupation": "Marketing Manager"
                },
                "psychographic": {
                    "interests": ["health", "nutrition", "parenting", "yoga", "sustainable living"],
                    "personal_values": ["family", "health", "sustainability"],
                    "attitudes": ["health conscious", "environmentally aware"],
                    "lifestyle": "Busy professional balancing career and family",
                    "personality": "Organized, nurturing, and health-oriented",
                    "opinions": ["Organic is better", "Work-life balance is essential"]
                },
                "behavioral": {
                    "browsing_habits": ["parenting blogs", "health sites", "recipe pages"],
                    "purchase_history": ["organic food", "children's products", "fitness items"],
                    "brand_interactions": ["Whole Foods", "Lululemon", "Peloton"],
                    "device_usage": {"smartphone": "heavy", "laptop": "moderate", "tablet": "light"},
                    "social_media_activity": {"Instagram": "high", "Pinterest": "high", "Facebook": "medium"},
                    "content_consumption": {"parenting articles": "daily", "health podcasts": "weekly"}
                },
                "contextual": {
                    "time_of_day": "morning",
                    "day_of_week": "weekend",
                    "season": "all",
                    "weather": "any",
                    "device_type": "mobile",
                    "browser_type": "safari",
                    "screen_size": "375x812",
                    "connection_type": "4g"
                }
            }
        ]
        
        # Add samples with IDs
        for sample in samples:
            self.personas[self.next_id] = {
                "id": self.next_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                **sample
            }
            self.next_id += 1
    
    def get_personas(self, page=1, per_page=20):
        """Get all personas with pagination"""
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        personas_list = list(self.personas.values())
        paginated_personas = personas_list[start_idx:end_idx]
        
        return {
            "personas": paginated_personas,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": len(personas_list),
                "total_pages": (len(personas_list) + per_page - 1) // per_page
            }
        }
    
    def get_all_personas(self, page=1, per_page=20):
        """Alias for get_personas (for compatibility)"""
        return self.get_personas(page=page, per_page=per_page)
    
    def get_persona(self, persona_id):
        """Get a specific persona by ID"""
        persona = self.personas.get(persona_id)
        if not persona:
            raise Exception(f"Persona not found with ID: {persona_id}")
        return persona
    
    def create_persona(self, persona_data):
        """Create a new persona"""
        persona_id = self.next_id
        self.next_id += 1
        
        persona = {
            "id": persona_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            **persona_data
        }
        
        self.personas[persona_id] = persona
        return persona
    
    def update_persona(self, persona_id, persona_data):
        """Update an existing persona"""
        if persona_id not in self.personas:
            raise Exception(f"Persona not found with ID: {persona_id}")
        
        # Keep ID and created_at, update all other fields
        persona = {
            "id": persona_id,
            "created_at": self.personas[persona_id]["created_at"],
            "updated_at": datetime.now().isoformat(),
            **persona_data
        }
        
        self.personas[persona_id] = persona
        return persona
    
    def delete_persona(self, persona_id):
        """Delete a persona"""
        if persona_id not in self.personas:
            raise Exception(f"Persona not found with ID: {persona_id}")
        
        del self.personas[persona_id]
        return {"message": f"Persona {persona_id} deleted successfully"}

# Create singleton instance
_persona_client = None

def get_mock_persona_client():
    """
    Get or create a singleton mock persona client instance
    
    Returns:
        MockPersonaClient: Shared client instance
    """
    global _persona_client
    if _persona_client is None:
        _persona_client = MockPersonaClient()
    return _persona_client
