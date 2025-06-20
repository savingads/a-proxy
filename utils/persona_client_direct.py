"""
Direct database persona client - replaces the API client
"""
import logging
from database import get_all_personas, get_persona, save_persona, delete_persona

# Setup logging
logger = logging.getLogger(__name__)

class DirectPersonaClient:
    """Direct database client that replaces the API client"""
    
    def __init__(self):
        """Initialize the direct client"""
        pass
    
    def get_personas(self, page=1, per_page=100):
        """
        Get all personas with pagination
        
        Args:
            page: Page number (1-indexed)
            per_page: Number of personas per page
            
        Returns:
            dict: Contains 'personas' list and pagination info
        """
        try:
            return get_all_personas(page=page, per_page=per_page)
        except Exception as e:
            logger.error(f"Error getting personas: {str(e)}")
            raise
    
    def get_all_personas(self, page=1, per_page=100):
        """Alias for get_personas for backward compatibility"""
        return self.get_personas(page=page, per_page=per_page)
    
    def get_persona(self, persona_id):
        """
        Get a specific persona by ID
        
        Args:
            persona_id: The ID of the persona
            
        Returns:
            dict: Persona data or None if not found
        """
        try:
            return get_persona(persona_id)
        except Exception as e:
            logger.error(f"Error getting persona {persona_id}: {str(e)}")
            raise
    
    def create_persona(self, persona_data):
        """
        Create a new persona
        
        Args:
            persona_data: Dictionary containing persona information
            
        Returns:
            dict: Created persona with ID
        """
        try:
            # Remove ID if present for new persona
            if 'id' in persona_data:
                del persona_data['id']
            
            persona_id = save_persona(persona_data)
            return get_persona(persona_id)
        except Exception as e:
            logger.error(f"Error creating persona: {str(e)}")
            raise
    
    def update_persona(self, persona_id, persona_data):
        """
        Update an existing persona
        
        Args:
            persona_id: The ID of the persona to update
            persona_data: Dictionary containing updated persona information
            
        Returns:
            dict: Updated persona data
        """
        try:
            # Ensure ID is set
            persona_data['id'] = persona_id
            save_persona(persona_data)
            return get_persona(persona_id)
        except Exception as e:
            logger.error(f"Error updating persona {persona_id}: {str(e)}")
            raise
    
    def delete_persona(self, persona_id):
        """
        Delete a persona
        
        Args:
            persona_id: The ID of the persona to delete
            
        Returns:
            bool: True if successful
        """
        try:
            return delete_persona(persona_id)
        except Exception as e:
            logger.error(f"Error deleting persona {persona_id}: {str(e)}")
            raise
    
    def health_check(self):
        """
        Check if the service is healthy
        
        Returns:
            dict: Health status
        """
        try:
            # Try to get personas to test database connection
            get_all_personas(page=1, per_page=1)
            return {"status": "healthy", "message": "Database connection successful"}
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {"status": "unhealthy", "message": str(e)}

# Create a singleton instance for reuse
_direct_client = None

def get_direct_persona_client():
    """
    Get or create a singleton DirectPersonaClient instance
    
    Returns:
        DirectPersonaClient: Shared client instance
    """
    global _direct_client
    if _direct_client is None:
        _direct_client = DirectPersonaClient()
    return _direct_client