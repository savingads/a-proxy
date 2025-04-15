"""
Utility module for interacting with the Persona API Service
"""
import logging
import time
import requests
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

class ResilientPersonaClient(PersonaClient):
    """Extended client with additional methods and resilient connection handling"""
    
    def __init__(self, base_url, api_version="v1", timeout=10, auth_token=None, max_retries=3, retry_delay=1):
        """Initialize with retry parameters"""
        super().__init__(base_url, api_version, timeout, auth_token)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def get_personas(self, page=1, per_page=20):
        """Alias for get_all_personas for backward compatibility"""
        return self.get_all_personas(page=page, per_page=per_page)
    
    def _make_request(self, method, endpoint, **kwargs):
        """Override to add retry logic for resilience"""
        retries = 0
        last_error = None
        
        while retries < self.max_retries:
            try:
                # Check if API is up before making the request
                if method != "GET" or endpoint != "health":  # Don't check health before health check
                    self._check_api_health()
                
                return super()._make_request(method, endpoint, **kwargs)
            except (requests.ConnectionError, requests.Timeout) as e:
                retries += 1
                last_error = e
                logger.warning(f"Connection error on attempt {retries}/{self.max_retries}: {str(e)}")
                
                if retries < self.max_retries:
                    time.sleep(self.retry_delay)
                    # Increase delay for next retry (exponential backoff)
                    self.retry_delay *= 1.5
            except Exception as e:
                # For other exceptions, just raise them
                logger.error(f"Error during API request: {str(e)}")
                raise
        
        # If we got here, all retries failed
        logger.error(f"All {self.max_retries} connection attempts failed")
        raise last_error
    
    def _check_api_health(self):
        """Check if the API is up and running"""
        try:
            # Use low timeout for health check
            response = requests.get(f"{self.base_url}/health", timeout=2)
            if not response.ok:
                logger.warning(f"API health check failed with status {response.status_code}")
                return False
            return True
        except (requests.ConnectionError, requests.Timeout) as e:
            logger.warning(f"API health check failed: {str(e)}")
            return False
        
def get_persona_client():
    """
    Get a configured Persona API client instance
    
    Returns:
        ResilientPersonaClient: Configured client instance
    """
    return ResilientPersonaClient(
        base_url=PERSONA_API_BASE_URL,
        api_version=PERSONA_API_VERSION,
        timeout=PERSONA_API_TIMEOUT,
        auth_token=PERSONA_API_AUTH_TOKEN,
        max_retries=3,
        retry_delay=1
    )

# Create a singleton instance for reuse
_persona_client = None

def get_client():
    """
    Get or create a singleton Persona client instance
    
    Returns:
        ResilientPersonaClient: Shared client instance
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
