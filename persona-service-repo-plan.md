# Persona Service Repository Migration Plan

## Repository Structure

```
persona-service/
├── app/                        # Main application package
│   ├── __init__.py             # App factory and setup
│   ├── config.py               # Configuration management
│   ├── models.py               # Database models
│   ├── routes.py               # API routes and endpoints
│   ├── schemas.py              # Data validation schemas
│   ├── services.py             # Business logic layer
│   └── utils/                  # Utility functions
├── data/                       # Data directory (git-ignored)
│   └── .gitkeep                # Placeholder to ensure directory exists
├── tests/                      # Test directory
│   ├── __init__.py
│   ├── conftest.py             # Test fixtures
│   └── test_*.py               # Test modules
├── .env.example                # Example environment variables
├── .gitignore                  # Git ignore file
├── Dockerfile                  # Docker configuration
├── LICENSE                     # License file
├── README.md                   # Project documentation
├── docker-compose.yml          # Docker Compose configuration
├── requirements.txt            # Python dependencies
└── run.py                      # Application entry point
```

## Files to Create or Update

### 1. README.md
A detailed README.md with:
- Project description
- Setup instructions
- Configuration guide
- API documentation
- Integration examples

### 2. .env.example
Sample environment variables file:
```
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
DATABASE_URI=sqlite:///data/persona_service.db
JWT_SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000,http://localhost:5000
LOG_LEVEL=INFO
```

### 3. .gitignore
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Flask
instance/
.webassets-cache

# Virtual Environment
venv/
ENV/

# Database
*.db
*.db-shm
*.db-wal
data/

# Environment variables
.env

# IDE
.idea/
.vscode/
*.swp
*.swo

# Logs
logs/
*.log
```

### 4. Fix run.py
Current run.py has syntax errors (missing commas). It should be:

```python
#!/usr/bin/env python3
"""
Entry point for running the Persona Service
"""
import argparse
from app import create_app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Persona Service API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=5050, help="Port to run the server on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")

    args = parser.parse_args()

    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)
```

### 5. Update app/config.py
Make sure it supports environment variables for all configuration:

```python
import os
from datetime import timedelta

# Database
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///data/persona_service.db")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_ACCESS_TOKEN_HOURS", "1")))
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_DAYS", "30")))

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
```

### 6. Sample docker-compose.yml
```yaml
version: '3.8'

services:
  persona-service:
    build: .
    ports:
      - "5050:5050"
    volumes:
      - ./data:/app/data
    environment:
      - FLASK_APP=run.py
      - FLASK_ENV=development
      - DATABASE_URI=sqlite:///data/persona_service.db
      - JWT_SECRET_KEY=your-secret-key
      - CORS_ORIGINS=http://localhost:3000,http://localhost:5000
    command: gunicorn --bind 0.0.0.0:5050 --workers 2 "app:create_app()"
```

## Documentation to Include

### 1. API Documentation
Document all available endpoints with:
- HTTP method
- URL path
- Request parameters
- Request body schema (if applicable)
- Response schema
- Authorization requirements
- Example requests and responses

### 2. Integration Guide
Document how to:
- Integrate the service via direct API calls
- Use the persona-client Python library
- Configure MCP integration (if applicable)
- Set up authentication
- Handle common errors

### 3. Configuration Reference
Document all configuration options:
- Environment variables
- Default values
- Valid value ranges
- Security considerations

## Dependency Updates

The current requirements.txt seems up-to-date but should be reviewed:
- Add flask-cors explicitly (it's used in __init__.py but not in requirements.txt)
- Consider adding pytest-flask for better testing
- Add python-dotenv for environment variable management

## Implementation Steps

1. Create a new GitHub repository
2. Set up the repository structure
3. Copy and adapt the existing persona-service code
4. Create the missing files (README.md, .env.example, etc.)
5. Fix any syntax or logical errors
6. Add comprehensive documentation
7. Test the standalone service
8. Publish the repository

## Usage Example Documentation

Add example code for consuming applications:

```python
import requests

# Example API usage
def get_personas(base_url="http://localhost:5050"):
    response = requests.get(f"{base_url}/api/v1/personas")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get personas: {response.text}")
```

Include sample MCP server implementation that connects to the persona-service.
