# Persona Service

A standalone API service for managing user personas with demographic, psychographic, behavioral, and contextual attributes.

## Overview

The Persona Service provides a flexible and powerful API for creating and managing user personas. It supports a dynamic schema that allows for a wide range of persona attributes without requiring database schema changes.

### Features

- **Dynamic Schema**: Add fields without database migrations
- **Rich Persona Data**: Support for demographic, psychographic, behavioral, and contextual attributes
- **RESTful API**: Clean API endpoints for CRUD operations
- **Flexible Integration**: Use directly via API or with the included client library
- **Docker Support**: Easy deployment with Docker

## Quick Start

### Using Docker

```bash
# Clone the repository
git clone https://github.com/yourusername/persona-service.git
cd persona-service

# Copy example environment file
cp .env.example .env

# Start the service with Docker Compose
docker-compose up -d
```

### Without Docker

```bash
# Clone the repository
git clone https://github.com/yourusername/persona-service.git
cd persona-service

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy example environment file
cp .env.example .env

# Run the service
python run.py
```

The service will be available at `http://localhost:5050`.

## Configuration

The Persona Service is configured through environment variables, which can be set in a `.env` file.

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URI` | Database connection string | `sqlite:///data/persona_service.db` |
| `JWT_SECRET_KEY` | Secret key for JWT token signing | `dev-secret-key` (change in production!) |
| `JWT_ACCESS_TOKEN_HOURS` | Access token expiration in hours | 1 |
| `JWT_REFRESH_TOKEN_DAYS` | Refresh token expiration in days | 30 |
| `CORS_ORIGINS` | Comma-separated list of allowed origins | `*` |
| `LOG_LEVEL` | Logging level | `INFO` |

## API Reference

The Persona Service exposes a RESTful API with the following endpoints:

### Authentication

- `POST /api/v1/auth/login`: Authenticate and get access token
- `POST /api/v1/auth/refresh`: Refresh access token
- `POST /api/v1/auth/logout`: Invalidate tokens

### Personas

- `GET /api/v1/personas`: List all personas with pagination
- `POST /api/v1/personas`: Create a new persona
- `GET /api/v1/personas/{id}`: Get a specific persona
- `PUT /api/v1/personas/{id}`: Update a persona
- `DELETE /api/v1/personas/{id}`: Delete a persona

### Persona Attributes

- `GET /api/v1/personas/{id}/demographic`: Get demographic data
- `PUT /api/v1/personas/{id}/demographic`: Update demographic data
- `GET /api/v1/personas/{id}/psychographic`: Get psychographic data
- `PUT /api/v1/personas/{id}/psychographic`: Update psychographic data
- `GET /api/v1/personas/{id}/behavioral`: Get behavioral data
- `PUT /api/v1/personas/{id}/behavioral`: Update behavioral data
- `GET /api/v1/personas/{id}/contextual`: Get contextual data
- `PUT /api/v1/personas/{id}/contextual`: Update contextual data

### Health Check

- `GET /health`: Service health check

## Data Structure

The persona data structure follows this format:

```json
{
  "id": 1,
  "name": "Example Persona",
  "demographic": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "language": "en-US",
    "country": "US",
    "city": "San Francisco",
    "region": "California"
  },
  "psychographic": {
    "interests": ["technology", "hiking", "photography"],
    "personal_values": ["innovation", "sustainability", "creativity"]
  },
  "behavioral": {
    "browsing_habits": ["technology news", "social media"],
    "device_usage": {
      "mobile": "4 hours/day",
      "desktop": "8 hours/day"
    }
  },
  "contextual": {
    "time_of_day": "morning",
    "device_type": "desktop",
    "browser_type": "chrome"
  }
}
```

## Integration Options

### Direct API Integration

For simple integration, you can make direct HTTP requests to the API:

```python
import requests

def get_personas(base_url="http://localhost:5050"):
    response = requests.get(f"{base_url}/api/v1/personas")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get personas: {response.text}")
```

### Python Client Library

For Python applications, use the persona-client library:

```bash
pip install persona-client
```

```python
from personaclient import PersonaClient

client = PersonaClient(base_url="http://localhost:5050", api_version="v1")
personas = client.get_all_personas()
```

### MCP Integration

For AI assistant integration, you can create an MCP server that connects to the Persona Service:

1. Create an MCP server that implements the MCP protocol
2. Create tools and resources that fetch data from the Persona Service
3. Use the MCP server to provide persona context to AI assistants

An example MCP server implementation is provided in the `examples/mcp-server` directory.

## Development

### Running Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run tests
pytest
```

### Database Migrations

The service uses SQLAlchemy with a dynamic schema, so most changes won't require migrations. If you need to modify the base schema:

1. Update models in `app/models.py`
2. Run the application to automatically apply changes to SQLite database

## Deployment

### Docker Deployment

The included Docker configuration provides an easy way to deploy the service:

```bash
docker-compose up -d
```

### Standalone Deployment

For production deployment, we recommend using Gunicorn:

```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:5050 --workers 4 "app:create_app()"
```

### Using with a Web Server

For production, we recommend using Nginx as a reverse proxy:

```nginx
server {
    listen 80;
    server_name persona-api.example.com;

    location / {
        proxy_pass http://localhost:5050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
