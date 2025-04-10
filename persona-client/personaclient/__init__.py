"""
Persona API Client - A Python client for interacting with the Persona API service
"""
from personaclient.client import PersonaClient
from personaclient.exceptions import (
    PersonaClientError,
    PersonaNotFoundError,
    PersonaValidationError,
    PersonaAPIError
)

__version__ = "0.1.0"
