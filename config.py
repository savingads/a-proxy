import json
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

# Region to language/geolocation/timezone mapping (externalized so regions can be
# added without a code change). Loaded eagerly; a missing/malformed file fails loud.
_REGIONS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "regions.json")
with open(_REGIONS_PATH, encoding="utf-8") as _regions_file:
    REGION_LANGUAGE_MAP = json.load(_regions_file)