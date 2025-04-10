"""
Database-backed implementation of the Persona Client
"""
import logging
import json
import os
from datetime import datetime
import database

# Setup logging
logger = logging.getLogger(__name__)

class DatabasePersonaClient:
    """Database-backed client implementation that reads from the existing database"""
    
    def __init__(self, *args, **kwargs):
        """Initialize client without API connection"""
        # Nothing to initialize - we'll just use the database module
        logger.info("Initializing database-backed persona client")
        
    def get_personas(self, page=1, per_page=20):
        """Get all personas with pagination"""
        logger.info(f"Getting personas from database with page={page}, per_page={per_page}")
        
        try:
            # Get all personas from the database
            personas_list = database.get_all_personas()
            
            # Apply pagination
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_personas = personas_list[start_idx:end_idx]
            
            # Format personas correctly - convert database format to API format
            formatted_personas = []
            for persona in paginated_personas:
                formatted = self._format_persona(persona)
                formatted_personas.append(formatted)
            
            return {
                "personas": formatted_personas,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": len(personas_list),
                    "total_pages": (len(personas_list) + per_page - 1) // per_page
                }
            }
        except Exception as e:
            logger.error(f"Error getting personas from database: {str(e)}")
            raise
    
    def get_all_personas(self, page=1, per_page=20):
        """Alias for get_personas (for compatibility)"""
        return self.get_personas(page=page, per_page=per_page)
    
    def get_persona(self, persona_id):
        """Get a specific persona by ID"""
        logger.info(f"Getting persona {persona_id} from database")
        
        try:
            # Get persona from database
            persona = database.get_persona(persona_id)
            
            if not persona:
                raise Exception(f"Persona not found with ID: {persona_id}")
                
            # Format persona to match API format
            formatted = self._format_persona(persona)
            return formatted
        except Exception as e:
            logger.error(f"Error getting persona {persona_id} from database: {str(e)}")
            raise
    
    def create_persona(self, persona_data):
        """Create a new persona"""
        logger.info(f"Creating new persona in database: {persona_data.get('name', 'Unnamed')}")
        
        try:
            # Save persona to database
            persona_id = database.save_persona(persona_data)
            
            # Get the newly created persona
            persona = database.get_persona(persona_id)
            
            # Format persona to match API format
            formatted = self._format_persona(persona)
            return formatted
        except Exception as e:
            logger.error(f"Error creating persona in database: {str(e)}")
            raise
    
    def update_persona(self, persona_id, persona_data):
        """Update an existing persona"""
        logger.info(f"Updating persona {persona_id} in database")
        
        try:
            # First check if persona exists
            existing = database.get_persona(persona_id)
            if not existing:
                raise Exception(f"Persona not found with ID: {persona_id}")
            
            # Delete the existing persona
            database.delete_persona(persona_id)
            
            # Create a new persona with the same ID
            # Note: This is a hack because our database module doesn't have a proper update function
            # that preserves the ID. In a real implementation, we would update the persona in-place.
            persona_data_with_id = persona_data.copy()
            persona_data_with_id['id'] = persona_id
            new_id = database.save_persona(persona_data_with_id)
            
            # Get the updated persona
            updated = database.get_persona(new_id)
            
            # Format persona to match API format
            formatted = self._format_persona(updated)
            return formatted
        except Exception as e:
            logger.error(f"Error updating persona {persona_id} in database: {str(e)}")
            raise
    
    def delete_persona(self, persona_id):
        """Delete a persona"""
        logger.info(f"Deleting persona {persona_id} from database")
        
        try:
            # Check if persona exists
            existing = database.get_persona(persona_id)
            if not existing:
                raise Exception(f"Persona not found with ID: {persona_id}")
            
            # Delete the persona
            database.delete_persona(persona_id)
            
            return {"message": f"Persona {persona_id} deleted successfully"}
        except Exception as e:
            logger.error(f"Error deleting persona {persona_id} from database: {str(e)}")
            raise
    
    def _format_persona(self, db_persona):
        """
        Format a database persona to match the API format
        
        Args:
            db_persona: Persona from database
            
        Returns:
            Formatted persona dict
        """
        formatted = {
            "id": db_persona['id'],
            "name": db_persona['name'],
            "created_at": db_persona.get('created_at', datetime.now().isoformat()),
            "updated_at": db_persona.get('updated_at', datetime.now().isoformat())
        }
        
        # Format demographic data
        if 'demographic' in db_persona:
            demographic = db_persona['demographic']
            
            # Remove persona_id if present
            if 'persona_id' in demographic:
                del demographic['persona_id']
            
            # Remove id if present
            if 'id' in demographic:
                del demographic['id']
                
            formatted['demographic'] = demographic
        
        # Format psychographic data
        if 'psychographic' in db_persona:
            psychographic = db_persona['psychographic']
            
            # Remove persona_id and id if present
            if 'persona_id' in psychographic:
                del psychographic['persona_id']
            if 'id' in psychographic:
                del psychographic['id']
                
            formatted['psychographic'] = psychographic
        
        # Format behavioral data
        if 'behavioral' in db_persona:
            behavioral = db_persona['behavioral']
            
            # Remove persona_id and id if present
            if 'persona_id' in behavioral:
                del behavioral['persona_id']
            if 'id' in behavioral:
                del behavioral['id']
                
            formatted['behavioral'] = behavioral
        
        # Format contextual data
        if 'contextual' in db_persona:
            contextual = db_persona['contextual']
            
            # Remove persona_id and id if present
            if 'persona_id' in contextual:
                del contextual['persona_id']
            if 'id' in contextual:
                del contextual['id']
                
            formatted['contextual'] = contextual
            
        return formatted

# Create singleton instance
_db_persona_client = None

def get_db_persona_client():
    """
    Get or create a singleton database-backed persona client instance
    
    Returns:
        DatabasePersonaClient: Shared client instance
    """
    global _db_persona_client
    if _db_persona_client is None:
        _db_persona_client = DatabasePersonaClient()
    return _db_persona_client
