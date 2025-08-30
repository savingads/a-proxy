import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Additional Flask configuration
DEBUG = os.environ.get('FLASK_DEBUG', 'False') == 'True'

# Anthropic API configuration
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

# Region to language mapping
REGION_LANGUAGE_MAP = {
    "US": {"language": "en-US"},
    "GB": {"language": "en-GB"},
    "CA": {"language": "en-CA"},
    "AU": {"language": "en-AU"},
    "DE": {"language": "de-DE"},
    "FR": {"language": "fr-FR"},
    "ES": {"language": "es-ES"},
    "IT": {"language": "it-IT"},
    "JP": {"language": "ja-JP"},
    "CN": {"language": "zh-CN"},
    "IN": {"language": "hi-IN"},
    "BR": {"language": "pt-BR"},
    "MX": {"language": "es-MX"},
    "RU": {"language": "ru-RU"},
    "KR": {"language": "ko-KR"},
    # Add more mappings as needed
}