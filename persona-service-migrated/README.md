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
