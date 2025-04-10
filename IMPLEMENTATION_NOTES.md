# Implementation Notes: Dynamic Persona System

## Overview

This document explains the dynamic persona field configuration system used in A-Proxy, which separates the persona database functionality from the web archival portion.

## Key Features

### Dynamic Field Configuration

The system uses a configurable field definition (persona_field_config.py) that allows:
- Custom field definitions for different types of data
- Dynamic rendering of forms based on configuration
- Easy extension with new field types

### Database Schema Design

- Uses a flexible attribute storage model with JSON data
- Reduces the tight coupling between database schema and UI
- Makes it easier to extend persona attributes without schema changes

### API & Client Integration

- Routes work with the dynamic fields
- Client library supports the flexible data structure
- The system is composable for use with other applications

## Architecture Components

### 1. Configuration

The field configuration (`persona_field_config.py`) defines all available attributes across three categories:
- Psychographic data (interests, values, attitudes)
- Behavioral data (habits, usage, interactions)
- Contextual data (situational factors)

### 2. Database Models

The persona data is stored using three main models:
- `Persona`: Core persona information (name, timestamps)
- `DemographicData`: Fixed demographic fields (location, language)
- `PersonaAttributes`: Dynamic JSON attributes (all other data)

### 3. Service Layer

The service layer processes data between the API and database:
- Validates field data against the configuration
- Transforms between flat and nested structures
- Handles serialization/deserialization

### 4. API Layer

The API exposes RESTful endpoints for CRUD operations:
- GET/POST/PUT/DELETE operations for personas
- Field validation based on configuration
- Consistent response format

## How to Use

### Customizing Fields

To customize the fields, you can:

1. Edit `persona_field_config.py` directly
2. Create a custom JSON configuration file and load it using:

```python
custom_config = persona_field_config.load_custom_config('path/to/config.json')
```

### Running the Complete Stack

The simplest way to run the complete A-Proxy with the Persona API service is using the provided script:

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

### Creating Sample Data

To create sample personas with the dynamic schema:

```bash
python create_sample_personas_api.py
```

This script creates several sample personas with full attribute sets across all categories.

## Implementation Details

### Field Type Support

The system supports three field types:
1. **string**: Simple text values
2. **list**: Arrays of strings
3. **dict**: Key-value pairs

Each field type is handled differently in validation, storage, and rendering.

### JSON Storage

The `PersonaAttributes` model stores attributes as JSON blobs, with:
- `persona_id`: Foreign key to the persona
- `category`: One of "psychographic", "behavioral", or "contextual"
- `data`: The JSON data for all fields in that category

### Template Rendering

Templates dynamically render forms based on the field configuration:
- Input types are determined by field type
- Field labels and descriptions come from configuration
- Complex fields use special input components

## Future Considerations

1. **API Versioning**: Consider implementing API versioning for better compatibility.
2. **Caching**: Add caching for field configurations to improve performance.
3. **Validation Extensions**: Extend validation to support more complex field types and rules.
4. **UI Improvements**: Add more sophisticated field editors for complex data types.
