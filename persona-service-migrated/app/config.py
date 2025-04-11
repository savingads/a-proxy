"""
Configuration settings for the Persona API Service
"""
import os
from datetime import timedelta

# Database settings
# Use absolute path for SQLite default
data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
os.makedirs(data_dir, exist_ok=True)
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", f"sqlite:///{os.path.join(data_dir, 'persona_service.db')}")
SQLALCHEMY_TRACK_MODIFICATIONS = False

# API settings
API_VERSION = "v1"
API_TITLE = "Persona Service API"
API_DESCRIPTION = "API for managing user personas"

# JWT settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key")  # Change in production!
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

# Security settings
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
