# A-Proxy

A Flask-based persona simulation and web interaction tracking system that models user personas across multiple dimensions and tracks their interactions through journeys.

## Quick Start

```bash
# Start the application
./start.sh

# Or with Docker
docker-compose up
```

Default login: `admin@example.com` / `password`

## Project Overview

A-Proxy enables:
- **Persona Management**: Create and manage detailed user personas with demographic, psychographic, behavioral, and contextual attributes
- **Journey Tracking**: Record sequences of web interactions as "journeys" with individual "waypoints"
- **Web Archiving**: Archive webpages with persona-specific context (language, geolocation)
- **AI Integration**: Chat with Claude AI as or about a persona
- **VPN Simulation**: Test from different geographic regions

## Architecture

```
a-proxy/
├── app.py                    # Flask application entry point
├── config.py                 # Configuration (API keys, settings)
├── database/                 # Database package (repository pattern)
│   ├── __init__.py          # Main exports + backward-compatible API
│   ├── connection.py        # SQLite connection management
│   ├── models/              # Dataclass domain models
│   └── repositories/        # Data access layer
│       ├── persona.py       # PersonaRepository
│       ├── journey.py       # JourneyRepository
│       ├── archive.py       # ArchiveRepository
│       ├── user.py          # UserRepository
│       └── settings.py      # SettingsRepository
├── routes/                   # Flask blueprints
│   ├── agent.py             # Claude AI integration
│   ├── persona_api_db.py    # Persona CRUD API
│   ├── journey.py           # Journey management
│   ├── browsing.py          # Web browsing/archiving
│   └── auth.py              # Authentication
├── services.py              # Context management for LLM
├── utils/                   # Utility modules
│   ├── agent.py            # AgentService wrapper
│   └── persona_client_db.py # Database persona client
├── templates/               # Jinja2 HTML templates
├── static/                  # CSS, JS, images
└── tests/                   # Test suite
```

## Key Concepts

### Persona Model (4 Dimensions)

```python
Persona
├── Demographic    # location, language, age, education, income, occupation
├── Psychographic  # interests, values, attitudes, lifestyle, personality
├── Behavioral     # browsing_habits, purchase_history, device_usage
└── Contextual     # time_of_day, device_type, browser_type, connection
```

### Journey & Waypoints

- **Journey**: Named collection of interactions linked to a persona
- **Waypoint**: Individual step (URL visit, agent conversation) with metadata

### Database Access

```python
# Repository pattern (recommended)
from database.repositories import PersonaRepository
repo = PersonaRepository()
persona = repo.get(1)

# Legacy function API (backward compatible)
from database import get_persona, save_persona
persona = get_persona(1)
```

## Configuration

Environment variables (`.env`):
```
ANTHROPIC_API_KEY=sk-ant-...   # Required for Claude AI features
SECRET_KEY=your_flask_secret   # Flask session security
DEBUG=True                     # Enable debug mode
```

## Key Files to Understand

| File | Purpose |
|------|---------|
| `database/__init__.py` | Database initialization + legacy API |
| `database/repositories/persona.py` | Persona CRUD operations |
| `services.py` | Context management for Claude prompts |
| `routes/agent.py` | Claude AI chat endpoints |
| `persona_field_config.py` | Dynamic field schema definitions |

## Testing

```bash
python tests/test_database.py
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/personas` | GET | List all personas |
| `/personas/<id>` | GET | Get persona details |
| `/personas/create` | POST | Create new persona |
| `/journeys` | GET | List all journeys |
| `/journey/<id>` | GET | Journey details with waypoints |
| `/agent/message` | POST | Send message to Claude |
| `/direct-chat/<persona_id>` | GET | Chat interface for persona |

## Integration Points

A-Proxy is designed to integrate with:
- **OntServe**: Ontology server for role definitions
- **Proethica**: Ethical decision-making framework

See `docs/INTEGRATION.md` for detailed integration plans.

## Development Notes

- SQLite database stored in `data/personas.db`
- Web archives stored in `archives/` directory
- Uses Selenium for browser automation (requires Chromium)
- Claude API calls are in `routes/agent.py` and `utils/agent.py`
