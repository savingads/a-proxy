import os

# Application configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Claude API configuration
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')  # Get API key from environment
CLAUDE_MODEL = 'claude-3-opus-20240229'  # Confirmed working model
CLAUDE_MAX_TOKENS = 4096

# Agent module configuration
AGENT_USE_CLAUDE = True
AGENT_REQUIRE_AUTH = False
AGENT_API_KEY = ANTHROPIC_API_KEY  # Use the same key for agent module

# Region to language mapping
REGION_LANGUAGE_MAP = {
    "US": {
        "name": "United States",
        "language": "en-US",
        "geolocation": "37.0902,-95.7129",
        "server": "us123.nordvpn.com.udp"
    },
    "BR": {
        "name": "Brazil",
        "language": "pt-BR",
        "geolocation": "-14.2350,-51.9253",
        "server": "br123.nordvpn.com.udp"
    },
    "DE": {
        "name": "Germany",
        "language": "de-DE",
        "geolocation": "51.1657,10.4515",
        "server": "de123.nordvpn.com.udp"
    },
    "JP": {
        "name": "Japan",
        "language": "ja-JP",
        "geolocation": "36.2048,138.2529",
        "server": "jp123.nordvpn.com.udp"
    },
    "ZA": {
        "name": "South Africa",
        "language": "af-ZA",
        "geolocation": "-30.5595,22.9375",
        "server": "za123.nordvpn.com.udp"
    }
}
