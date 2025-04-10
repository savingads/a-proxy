"""
Configuration for the Persona API Service integration
"""
import os

# Persona API configuration
PERSONA_API_BASE_URL = os.environ.get("PERSONA_API_URL", "http://localhost:5050")
PERSONA_API_VERSION = os.environ.get("PERSONA_API_VERSION", "v1")
PERSONA_API_TIMEOUT = int(os.environ.get("PERSONA_API_TIMEOUT", "10"))
PERSONA_API_AUTH_TOKEN = os.environ.get("PERSONA_API_AUTH_TOKEN")
