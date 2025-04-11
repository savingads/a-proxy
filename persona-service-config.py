"""
Configuration for the Persona Service API
"""
import os
from datetime import timedelta

# Environment-based configuration
ENV = os.getenv("FLASK_ENV", "development")
DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

# Database URI
# Default SQLite database path
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "persona_service.db")
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", f"sqlite:///{DEFAULT_DB_PATH}")

# Print the database URI for debugging during startup
print(f"Using database URI: {SQLALCHEMY_DATABASE_URI}")

# JWT Authentication settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_ACCESS_TOKEN_HOURS", "1")))
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_DAYS", "30")))

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# API Version
API_VERSION = "v1"

# Pagination defaults
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Field configuration
# This can be overridden by a custom field configuration file
DEFAULT_FIELD_CONFIG = {
    "demographic": {
        "label": "Demographic Data",
        "description": "Basic demographic information about the persona",
        "fields": [
            {
                "name": "language",
                "type": "string",
                "label": "Language",
                "description": "Primary language of the persona (e.g., en-US)"
            },
            {
                "name": "country",
                "type": "string",
                "label": "Country",
                "description": "Country of residence (e.g., US)"
            },
            {
                "name": "city",
                "type": "string",
                "label": "City",
                "description": "City of residence (e.g., San Francisco)"
            },
            {
                "name": "region",
                "type": "string",
                "label": "Region",
                "description": "State, province, or region (e.g., California)"
            },
            {
                "name": "latitude",
                "type": "float",
                "label": "Latitude",
                "description": "Geographic latitude"
            },
            {
                "name": "longitude",
                "type": "float",
                "label": "Longitude",
                "description": "Geographic longitude"
            }
        ]
    },
    "psychographic": {
        "label": "Psychographic Data",
        "description": "Information about personality, values, opinions, interests, lifestyle, etc.",
        "fields": [
            {
                "name": "interests",
                "type": "list",
                "label": "Interests",
                "description": "Activities, topics, or subjects the persona is interested in"
            },
            {
                "name": "personal_values",
                "type": "list",
                "label": "Personal Values",
                "description": "Core values that guide the persona's decisions and behaviors"
            },
            {
                "name": "lifestyle",
                "type": "string",
                "label": "Lifestyle",
                "description": "General lifestyle description"
            },
            {
                "name": "personality_traits",
                "type": "list",
                "label": "Personality Traits",
                "description": "Key personality characteristics"
            }
        ]
    },
    "behavioral": {
        "label": "Behavioral Data",
        "description": "Information about behaviors, habits, and actions",
        "fields": [
            {
                "name": "browsing_habits",
                "type": "list",
                "label": "Browsing Habits",
                "description": "Typical web browsing patterns and preferences"
            },
            {
                "name": "shopping_preferences",
                "type": "list",
                "label": "Shopping Preferences",
                "description": "Shopping behaviors and preferences"
            },
            {
                "name": "device_usage",
                "type": "dict",
                "label": "Device Usage",
                "description": "How and when different devices are used"
            }
        ]
    },
    "contextual": {
        "label": "Contextual Data",
        "description": "Situational and environmental information",
        "fields": [
            {
                "name": "time_of_day",
                "type": "string",
                "label": "Time of Day",
                "description": "Current time period (morning, afternoon, evening)"
            },
            {
                "name": "device_type",
                "type": "string",
                "label": "Device Type",
                "description": "Type of device being used (desktop, mobile, tablet)"
            },
            {
                "name": "browser_type",
                "type": "string",
                "label": "Browser Type",
                "description": "Web browser being used"
            },
            {
                "name": "connection_type",
                "type": "string",
                "label": "Connection Type",
                "description": "Internet connection type (wifi, cellular, etc.)"
            }
        ]
    }
}

# Path to custom field configuration file
FIELD_CONFIG_PATH = os.getenv("FIELD_CONFIG_PATH", None)

# Function to load field configuration from file if it exists
def load_field_config():
    """Load field configuration from file if available"""
    if FIELD_CONFIG_PATH and os.path.exists(FIELD_CONFIG_PATH):
        try:
            import json
            with open(FIELD_CONFIG_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading field configuration: {e}")
            return DEFAULT_FIELD_CONFIG
    return DEFAULT_FIELD_CONFIG

# Field configuration to use
PERSONA_FIELD_CONFIG = load_field_config()
