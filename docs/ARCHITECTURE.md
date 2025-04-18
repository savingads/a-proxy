# A-Proxy Architecture

This document provides a comprehensive overview of the A-Proxy system architecture, focusing on the persona service, dynamic schema, and integration options.

---

## 1. Overview
A-Proxy separates persona management from web archival, allowing the persona system to be reused in other applications. Persona data is managed via a dynamic schema and can be accessed through a REST API, mock client, or direct database integration.

---

## 2. Components
- **Persona API Service (`persona-service/`)**: Standalone RESTful API for persona CRUD operations.
- **Persona Client Library (`persona-client/`)**: Python library for interacting with the Persona API.
- **Local Integration (`utils/`)**: Utilities for API, mock, or DB-backed persona management.
- **Flask Routes (`routes/`)**: Web routes for persona operations in the A-Proxy UI.
- **Web UI (`templates/`)**: Dynamic forms and views for persona data.
- **Field Configuration (`persona_field_config.py`)**: Defines persona attributes and categories.

---

## 3. Integration Options
A-Proxy supports three persona management modes:
- **API-Based**: Uses the external Persona API service (recommended for multi-app environments).
- **Mock**: In-memory, for development/testing.
- **Database**: Direct SQLite access, for simplicity.

Switch modes by configuring the startup script or using the appropriate client in your code.

---

## 4. Dynamic Persona Schema
- **Demographic data**: Fixed fields (location, language, etc.)
- **Dynamic attributes**: Psychographic, behavioral, contextual—stored as JSON blobs in the `persona_attributes` table.
- **Field configuration**: All available fields and types are defined in `persona_field_config.py` and can be customized.

### Example Field Configuration
```python
PERSONA_FIELD_CONFIG = {
    "psychographic": {
        "label": "Psychographic Data",
        "fields": [
            {"name": "interests", "type": "list", "label": "Interests"},
            # ...
        ]
    },
    # behavioral, contextual ...
}
```

---

## 5. Data Model
- **personas**: Core info (ID, name, timestamps)
- **demographic_data**: Fixed fields (lat/lon, language, etc.)
- **persona_attributes**: Dynamic JSON attributes, one row per category per persona

### Example Persona (API Response)
```json
{
  "id": 1,
  "name": "Example Persona",
  "demographic": {"latitude": 37.77, "language": "en-US", ...},
  "psychographic": {"interests": ["tech", "hiking"]},
  "behavioral": {"browsing_habits": ["news"]},
  "contextual": {"time_of_day": "morning"}
}
```

---

## 6. Customization & Extension
- Edit `persona_field_config.py` or load a custom JSON config for new fields/categories.
- No DB migration is needed for new fields—UI and API update automatically.
- Use the client library for API access, or direct DB/mock for testing.

---

## 7. Technical Implementation Details
- **Database**: SQLAlchemy ORM, JSON serialization for dynamic fields.
- **API**: RESTful endpoints for persona CRUD and field config.
- **UI**: Dynamic form rendering based on field config.
- **Configuration**: Set API base URL, version, and tokens in `persona_config.py`.

---

## 8. Example Usage
### API Client
```python
from personaclient import PersonaClient
client = PersonaClient(base_url="http://localhost:5050")
personas = client.get_all_personas()
```

### Mock/DB Client
```python
from utils.persona_client_mock import get_mock_persona_client
client = get_mock_persona_client()
```

---

## 9. Further Reading
- See [PERSONA_API.md](./PERSONA_API.md) for API details and endpoints.
- See [persona-client/README.md](../persona-client/README.md) for client usage.
- See [../persona_field_config.py](../persona_field_config.py) for field customization.
