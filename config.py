import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Additional Flask configuration
DEBUG = os.environ.get('FLASK_DEBUG', 'False') == 'True'

# Proxy configuration (replaces VPN)
PROXY_URL = os.environ.get('PROXY_URL')  # e.g. socks5://user:pass@host:port
BROWSER_HEADLESS = os.environ.get('BROWSER_HEADLESS', 'True') == 'True'

# LLM provider configuration
# Supported: "openai_compatible" (vLLM, Ollama, etc.), "anthropic", "openai"
LLM_PROVIDER = os.environ.get('LLM_PROVIDER')

# OpenAI-compatible endpoint (vLLM, Ollama, text-generation-webui, LiteLLM, etc.)
# This is the recommended setup for local/self-hosted models (e.g. Qwen on HPC)
OPENAI_COMPATIBLE_URL = os.environ.get('OPENAI_COMPATIBLE_URL')  # e.g. http://picotte-host:8000/v1
OPENAI_COMPATIBLE_MODEL = os.environ.get('OPENAI_COMPATIBLE_MODEL', 'Qwen/Qwen2.5-72B-Instruct')
OPENAI_COMPATIBLE_API_KEY = os.environ.get('OPENAI_COMPATIBLE_API_KEY', 'none')  # vLLM default

# Commercial API keys (optional)
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Default models
ANTHROPIC_MODEL = os.environ.get('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')

# Token limits
LLM_MAX_OUTPUT_TOKENS = int(os.environ.get('LLM_MAX_OUTPUT_TOKENS', '4096'))

# Region to language/geolocation/timezone mapping
REGION_LANGUAGE_MAP = {
    "US": {"language": "en-US", "geolocation": "37.7749,-122.4194", "name": "United States", "timezone": "America/New_York"},
    "GB": {"language": "en-GB", "geolocation": "51.5074,-0.1278", "name": "United Kingdom", "timezone": "Europe/London"},
    "CA": {"language": "en-CA", "geolocation": "43.6532,-79.3832", "name": "Canada", "timezone": "America/Toronto"},
    "AU": {"language": "en-AU", "geolocation": "-33.8688,151.2093", "name": "Australia", "timezone": "Australia/Sydney"},
    "DE": {"language": "de-DE", "geolocation": "52.5200,13.4050", "name": "Germany", "timezone": "Europe/Berlin"},
    "FR": {"language": "fr-FR", "geolocation": "48.8566,2.3522", "name": "France", "timezone": "Europe/Paris"},
    "ES": {"language": "es-ES", "geolocation": "40.4168,-3.7038", "name": "Spain", "timezone": "Europe/Madrid"},
    "IT": {"language": "it-IT", "geolocation": "41.9028,12.4964", "name": "Italy", "timezone": "Europe/Rome"},
    "JP": {"language": "ja-JP", "geolocation": "35.6762,139.6503", "name": "Japan", "timezone": "Asia/Tokyo"},
    "CN": {"language": "zh-CN", "geolocation": "39.9042,116.4074", "name": "China", "timezone": "Asia/Shanghai"},
    "IN": {"language": "hi-IN", "geolocation": "28.6139,77.2090", "name": "India", "timezone": "Asia/Kolkata"},
    "BR": {"language": "pt-BR", "geolocation": "-23.5505,-46.6333", "name": "Brazil", "timezone": "America/Sao_Paulo"},
    "MX": {"language": "es-MX", "geolocation": "19.4326,-99.1332", "name": "Mexico", "timezone": "America/Mexico_City"},
    "RU": {"language": "ru-RU", "geolocation": "55.7558,37.6173", "name": "Russia", "timezone": "Europe/Moscow"},
    "KR": {"language": "ko-KR", "geolocation": "37.5665,126.9780", "name": "South Korea", "timezone": "Asia/Seoul"},
    "ZA": {"language": "af-ZA", "geolocation": "-33.9249,18.4241", "name": "South Africa", "timezone": "Africa/Johannesburg"},
}