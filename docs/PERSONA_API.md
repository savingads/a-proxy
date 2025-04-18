# Persona API Documentation

This document outlines the REST API endpoints, request/response formats, and integration options for the Persona Service used in A-Proxy.

## API Overview

The Persona API is a RESTful service that provides:
- CRUD operations for persona management
- Field configuration retrieval
- Support for dynamic persona attributes

## Base URL

```
http://localhost:5050/api/v1
```

You can configure this in `persona_config.py` or through environment variables.

## Authentication

The API is prepared for JWT-based authentication, though it is not enabled by default. When enabled, include the JWT token in the Authorization header:

```
Authorization: Bearer <your_token>
```

## API Endpoints

### Persona Management

#### Get All Personas

```
GET /personas
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Alex Johnson",
    "demographic": {
      "latitude": 37.77,
      "longitude": -122.41,
      "language": "en-US",
      "country": "United States",
      "city": "San Francisco"
    },
    "psychographic": {
      "interests": ["technology", "hiking", "photography"],
      "values": ["innovation", "privacy", "sustainability"]
    },
    "behavioral": {
      "browsing_habits": ["tech news", "product reviews", "developer forums"],
      "device_usage": ["smartphone", "laptop", "smartwatch"]
    },
    "contextual": {
      "time_of_day": "morning",
      "device_type": "desktop",
      "network_type": "broadband"
    }
  },
  // ...more personas
]
```

#### Get a Specific Persona

```
GET /personas/{persona_id}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Alex Johnson",
  "demographic": {
    "latitude": 37.77,
    "longitude": -122.41,
    "language": "en-US",
    "country": "United States",
    "city": "San Francisco"
  },
  "psychographic": {
    "interests": ["technology", "hiking", "photography"],
    "values": ["innovation", "privacy", "sustainability"]
  },
  "behavioral": {
    "browsing_habits": ["tech news", "product reviews", "developer forums"],
    "device_usage": ["smartphone", "laptop", "smartwatch"]
  },
  "contextual": {
    "time_of_day": "morning",
    "device_type": "desktop",
    "network_type": "broadband"
  }
}
```

#### Create a New Persona

```
POST /personas
```

**Request:**
```json
{
  "name": "New Persona",
  "demographic": {
    "latitude": 48.85,
    "longitude": 2.35,
    "language": "fr-FR",
    "country": "France",
    "city": "Paris"
  },
  "psychographic": {
    "interests": ["art", "cuisine", "literature"],
    "values": ["tradition", "culture", "family"]
  },
  "behavioral": {
    "browsing_habits": ["news", "recipes", "travel blogs"],
    "device_usage": ["tablet", "smartphone"]
  },
  "contextual": {
    "time_of_day": "evening",
    "device_type": "tablet",
    "network_type": "wifi"
  }
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "name": "New Persona",
  "demographic": {
    "latitude": 48.85,
    "longitude": 2.35,
    "language": "fr-FR",
    "country": "France",
    "city": "Paris"
  },
  "psychographic": {
    "interests": ["art", "cuisine", "literature"],
    "values": ["tradition", "culture", "family"]
  },
  "behavioral": {
    "browsing_habits": ["news", "recipes", "travel blogs"],
    "device_usage": ["tablet", "smartphone"]
  },
  "contextual": {
    "time_of_day": "evening",
    "device_type": "tablet",
    "network_type": "wifi"
  }
}
```

#### Update an Existing Persona

```
PUT /personas/{persona_id}
```

**Request:** Same format as POST

**Response (200 OK):** Updated persona data

#### Delete a Persona

```
DELETE /personas/{persona_id}
```

**Response (204 No Content)**

### Field Configuration

#### Get Field Configuration

```
GET /field_config
```

**Response (200 OK):**
```json
{
  "psychographic": {
    "label": "Psychographic Data",
    "fields": [
      {"name": "interests", "type": "list", "label": "Interests"},
      {"name": "values", "type": "list", "label": "Values"},
      {"name": "attitudes", "type": "list", "label": "Attitudes"}
    ]
  },
  "behavioral": {
    "label": "Behavioral Data",
    "fields": [
      {"name": "browsing_habits", "type": "list", "label": "Browsing Habits"},
      {"name": "device_usage", "type": "list", "label": "Device Usage"},
      {"name": "purchase_history", "type": "list", "label": "Purchase History"}
    ]
  },
  "contextual": {
    "label": "Contextual Data",
    "fields": [
      {"name": "time_of_day", "type": "string", "label": "Time of Day"},
      {"name": "device_type", "type": "string", "label": "Device Type"},
      {"name": "network_type", "type": "string", "label": "Network Type"}
    ]
  }
}
```

### Health Check

```
GET /health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.1.0",
  "database": "connected"
}
```

## Error Responses

The API returns appropriate HTTP status codes for errors:

- **400 Bad Request**: Invalid request data
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource already exists
- **500 Internal Server Error**: Server-side error

Error response format:
```json
{
  "error": "Error message",
  "details": "Additional error details"
}
```

## Using the API with the Client Library

The `personaclient` package provides a Python client for simplified API access:

```python
from personaclient import PersonaClient

# Initialize client
client = PersonaClient(base_url="http://localhost:5050/api/v1")

# Get all personas
personas = client.get_all_personas()

# Get a specific persona
persona = client.get_persona(1)

# Create a new persona
new_persona = {
  "name": "New Persona",
  "demographic": {...},
  "psychographic": {...},
  "behavioral": {...},
  "contextual": {...}
}
result = client.create_persona(new_persona)

# Update a persona
client.update_persona(1, updated_data)

# Delete a persona
client.delete_persona(1)

# Get field configuration
config = client.get_field_config()
```

## Using Mock or Direct DB Access

In addition to the REST API, the system supports mock or direct database access:

### Mock Client

```python
from utils.persona_client_mock import get_mock_persona_client

client = get_mock_persona_client()
# Use the same interface as the API client
```

### DB-Backed Client

```python
from utils.persona_client_db import get_db_persona_client

client = get_db_persona_client()
# Use the same interface as the API client
```

## MCP Server Integration

The Persona API is also accessible through the Model Context Protocol (MCP) server, allowing AI models to interact with personas directly.

See [MCP server documentation](persona-mcp-server/README.md) for details on MCP integration.

## Further Resources

- [ARCHITECTURE.md](ARCHITECTURE.md): System architecture
- [IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md): Implementation details
- [persona-client/README.md](../persona-client/README.md): Client library documentation
- [persona-mcp-server/README.md](../persona-mcp-server/README.md): MCP server documentation
