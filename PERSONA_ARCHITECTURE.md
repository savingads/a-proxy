# Persona Service Architecture

This document outlines the architecture of the persona service component and the dynamic schema implementation that separates it from the web archival component of A-Proxy.

## Overview

The application has been restructured to separate the persona management functionality from the web archival components. This separation allows the persona component to be used independently in other applications, while still maintaining compatibility with the existing A-Proxy system.

## Components

### 1. Persona API Service (persona-service/)

A standalone service that provides a RESTful API for managing personas. This service can be run independently and accessed by multiple client applications.

- Located in: `persona-service/`
- Main entry point: `persona-service/run.py`
- API routes: `persona-service/app/routes.py`
- Database models: `persona-service/app/models.py`
- Business logic: `persona-service/app/services.py`

### 2. Persona Client Library (persona-client/)

A Python client library that provides a convenient interface for interacting with the Persona API Service.

- Located in: `persona-client/`
- Main client class: `persona-client/personaclient/client.py`
- Installation: `pip install -e ./persona-client`

### 3. Local Integration (utils/)

Utilities for integrating the Persona Client Library into the A-Proxy application.

- API wrapper module: `utils/persona_client.py`
- Mock implementation: `utils/persona_client_mock.py`
- Database implementation: `utils/persona_client_db.py`

### 4. Flask Routes (routes/)

The Flask routes for interacting with personas in the A-Proxy web interface.

- API implementation: `routes/persona_api.py`
- Mock implementation: `routes/persona_api_mock.py`
- Database implementation: `routes/persona_api_db.py`

## Implementation Variants

The application can be run in three different modes:

### 1. API-Based Mode (requires running persona-service)

Uses the external Persona API service for all persona operations.

```bash
# Start the API service
cd persona-service
python run.py

# In another terminal, start the main application
python app.py
```

### 2. Mock Implementation (no API service required)

Uses an in-memory mock implementation. This is useful for testing or when you don't need to persist data between restarts.

```bash
python app_with_mock.py
```

### 3. Database Mode (direct database access)

Uses the existing SQLite database directly, without requiring the API service.

```bash
python app_with_db.py
```

## Unified Startup Script

For convenience, a unified startup script is provided that can run any of the three implementation variants:

```bash
# Start with database implementation (default)
./start_a_proxy_all.py

# Start with mock implementation
./start_a_proxy_all.py --implementation mock

# Start with API implementation (requires API service)
./start_a_proxy_all.py --implementation api

# Start only the API service
./start_a_proxy_all.py --implementation api --api-only
```

## Field Configuration

The persona system supports dynamic field configuration via the `persona_field_config.py` file. This allows for flexible persona data models with different field types:

- String fields
- List fields (comma-separated values)
- Dictionary fields (key-value pairs)

The field configuration is used by all three implementations (API, mock, and database) to ensure consistent data models.

## Client Implementation Details

All client implementations provide the same interface for working with personas:

- `get_all_personas()` / `get_personas()`: List all personas with pagination
- `get_persona(persona_id)`: Get a specific persona by ID
- `create_persona(persona_data)`: Create a new persona
- `update_persona(persona_id, persona_data)`: Update an existing persona
- `delete_persona(persona_id)`: Delete a persona

### API Client (`PersonaClient`)

Makes HTTP requests to the external Persona API service.

### Mock Client (`MockPersonaClient`)

Stores data in memory instead of making API requests or using a database.

### Database Client (`DatabasePersonaClient`)

Works directly with the SQLite database using the existing database module.

## Persona Data Structure

The persona data structure includes:

```json
{
  "id": 1,
  "name": "Sample Persona",
  "demographic": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "language": "en-US",
    "country": "United States",
    "city": "San Francisco",
    "region": "California",
    "age": 28,
    "gender": "male",
    "education": "Bachelor's degree",
    "income": "75000-100000",
    "occupation": "Software Developer"
  },
  "psychographic": {
    "interests": ["technology", "programming", "gaming"],
    "personal_values": ["innovation", "knowledge", "creativity"],
    "attitudes": ["early adopter", "tech optimist"],
    "lifestyle": "Digital nomad who works remotely",
    "personality": "Analytical, curious, and forward-thinking",
    "opinions": ["AI will transform society", "Open source is important"]
  },
  "behavioral": {
    "browsing_habits": ["tech news", "programming forums", "product reviews"],
    "purchase_history": ["electronics", "digital subscriptions", "tech gadgets"],
    "brand_interactions": ["Apple", "Google", "Microsoft", "Tesla"],
    "device_usage": {"smartphone": "heavy", "laptop": "heavy", "tablet": "moderate"},
    "social_media_activity": {"Twitter": "high", "LinkedIn": "medium", "Facebook": "low"},
    "content_consumption": {"tech blogs": "daily", "videos": "weekly", "podcasts": "daily"}
  },
  "contextual": {
    "time_of_day": "evening",
    "day_of_week": "weekday",
    "season": "all",
    "weather": "any",
    "device_type": "desktop",
    "browser_type": "chrome",
    "screen_size": "1920x1080",
    "connection_type": "wifi"
  }
}
```

## Using the Persona Service in Other Applications

To use the Persona Service in other applications:

### Option 1: API-based approach (using client library)
```python
from personaclient import PersonaClient

client = PersonaClient(base_url="http://localhost:5050", api_version="v1")
personas = client.get_all_personas()
```

### Option 2: Mock implementation (for testing)
```python
from utils.persona_client_mock import get_mock_persona_client

client = get_mock_persona_client()
personas = client.get_personas()
```

### Option 3: Database-backed approach
```python
from utils.persona_client_db import get_db_persona_client

client = get_db_persona_client()
personas = client.get_personas()
```

### Option 4: Direct REST API calls
   - `GET /api/v1/personas` - List all personas
   - `GET /api/v1/personas/{id}` - Get a specific persona
   - `POST /api/v1/personas` - Create a new persona
   - `PUT /api/v1/personas/{id}` - Update a persona
   - `DELETE /api/v1/personas/{id}` - Delete a persona

## Configuration

The Persona API Service can be configured via the `persona_config.py` file, which includes settings for:

- API base URL
- API version
- Timeout settings
- Authentication tokens

## Choosing an Implementation

Each implementation has its own advantages:

- **API Service** - Best for multi-application environments where multiple applications need to access the same persona data.
- **Mock Implementation** - Best for development and testing, or when you need temporary in-memory data.
- **Database Implementation** - Best for simplicity and when you don't need a separate service.

## Production Deployment

### Recommended Approach with Docker

The recommended approach for production deployment is to use the provided script:

```bash
./start-api-stack.sh
```

This script will:
- Create all necessary directories
- Generate a JWT secret key
- Build and start both A-Proxy and the Persona API service using Docker Compose
- Make the services available at:
  - Persona API: http://localhost:5050
  - A-Proxy Web UI: http://localhost:5002

If this is your first time running the stack, you'll need to migrate existing personas to the API:

```bash
python migrate_to_api.py
```

### Manual Docker Setup

For manual deployment with Docker, use the Docker Compose configuration in `docker-compose-api.yml`:

```bash
docker-compose -f docker-compose-api.yml up
```

This will start both the Persona API Service and the main A-Proxy application with proper networking.
