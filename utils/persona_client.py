"""
Utility module for interacting with the Persona API Service
"""
import logging
from personaclient import PersonaClient
from personaclient.exceptions import (
    PersonaClientError,
    PersonaNotFoundError,
    PersonaValidationError,
    PersonaAPIError
)
from persona_config import (
    PERSONA_API_BASE_URL,
    PERSONA_API_VERSION,
    PERSONA_API_TIMEOUT,
    PERSONA_API_AUTH_TOKEN
)

# Setup logging
logger = logging.getLogger(__name__)

def get_persona_client():
    """
    Get a configured Persona API client instance
    
    Returns:
        PersonaClient: Configured client instance
    """
    return PersonaClient(
        base_url=PERSONA_API_BASE_URL,
        api_version=PERSONA_API_VERSION,
        timeout=PERSONA_API_TIMEOUT,
        auth_token=PERSONA_API_AUTH_TOKEN
    )

# Create a singleton instance for reuse
_persona_client = None

def get_client():
    """
    Get or create a singleton Persona client instance
    
    Returns:
        PersonaClient: Shared client instance
    """
    global _persona_client
    if _persona_client is None:
        _persona_client = get_persona_client()
    return _persona_client

# Exception handling utility
def handle_persona_api_error(e, operation="API operation"):
    """
    Handle and log Persona API errors
    
    Args:
        e: The exception that occurred
        operation: Description of the operation for logging
        
    Returns:
        tuple: (success, error_message)
    """
    if isinstance(e, PersonaNotFoundError):
        logger.warning(f"Persona not found: {e}")
        return False, f"Persona not found: {e.persona_id}"
    elif isinstance(e, PersonaValidationError):
        logger.warning(f"Validation error: {e}")
        return False, f"Validation error: {e}"
    elif isinstance(e, PersonaAPIError):
        logger.error(f"Persona API error during {operation}: {e}")
        return False, f"API error: {e.message}"
    elif isinstance(e, PersonaClientError):
        logger.error(f"Persona client error during {operation}: {e}")
        return False, f"Client error: {str(e)}"
    else:
        logger.error(f"Unexpected error during {operation}: {str(e)}")
        return False, f"Unexpected error: {str(e)}"
