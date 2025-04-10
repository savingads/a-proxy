# Dynamic Persona API System

The A-Proxy system uses a dynamic schema approach for persona management, separating the persona database and profiling from the web archival portion. This allows the persona component to be reused with other applications. The system renders persona attributes dynamically based on a configuration file, providing flexibility without requiring database schema changes.

## Key Features

- **API-Driven Architecture**: Persona data is now served through a RESTful API
- **Configurable Fields**: Psychographic, Behavioral, and Contextual attributes are fully configurable
- **Dynamic UI**: Forms and views render dynamically based on field configuration
- **JSON-based Storage**: Attribute data is stored as JSON blobs, allowing for flexible schema evolution
- **Easy Customization**: Different field sets can be defined for different use cases

## Architecture

### Components

1. **Persona Service API**: Standalone service that manages persona data
   - Located in `persona-service/`
   - Exposes RESTful endpoints for CRUD operations

2. **Persona Client**: Library for interacting with the Persona Service API
   - Located in `persona-client/`
   - Provides a clean abstraction for API calls

3. **Web UI**: Dynamic templates for viewing and editing personas
   - Located in `templates/`
   - Renders fields based on configuration

4. **Field Configuration**: Definition of persona attribute fields
   - Located in `persona_field_config.py`
   - Can be customized or replaced

### Data Model

The new schema uses a flexible approach where attribute data is stored in a `persona_attributes` table with three categories:

- **psychographic**: Psychological attributes, interests, values
- **behavioral**: Online behavior and usage patterns
- **contextual**: Situational and environmental factors

Each entry in this table stores its data as a JSON blob, allowing for schema flexibility without requiring database migrations when fields change.

## API Endpoints

The Persona Service API provides the following endpoints:

- `GET /api/v1/personas`: List all personas with pagination
- `GET /api/v1/personas/{id}`: Get a specific persona
- `POST /api/v1/personas`: Create a new persona
- `PUT/PATCH /api/v1/personas/{id}`: Update a persona
- `DELETE /api/v1/personas/{id}`: Delete a persona
- `GET /api/v1/field-config`: Get field configuration
- `GET /api/v1/personas/{id}/attributes/{category}`: Get attributes for a specific category
- `PUT/PATCH /api/v1/personas/{id}/attributes/{category}`: Update attributes for a specific category

## Using the System

### Recommended Way to Run the Complete Stack

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

If this is your first time running the stack, you'll need to migrate existing personas to the API:

```bash
python migrate_to_api.py
```

### Running the Implementation

To implement the dynamic persona field system:

```bash
# Standard implementation with file backups
python implement_dynamic_personas.py

# Implementation with migration
python implement_dynamic_personas.py --migrate

# Implementation without backups
python implement_dynamic_personas.py --no-backup

# Dry run migration only
python implement_dynamic_personas.py --migrate --dry-run
```

### Customizing Fields

The field configuration defines what attributes are available for personas. You can customize this in two ways:

1. **Edit `persona_field_config.py` directly**: Modify the `PERSONA_FIELD_CONFIG` dictionary
2. **Use a custom JSON configuration file**:

```python
import persona_field_config

# Load a custom configuration
custom_config = persona_field_config.load_custom_config('path/to/config.json')

# Use it in your app
app.config['PERSONA_FIELD_CONFIG'] = custom_config
```

## Custom Configuration Example

A sample custom configuration for marketing use cases is provided in `sample_custom_field_config.json`. To use it:

```python
import persona_field_config
import json

# In your app initialization
with open('sample_custom_field_config.json', 'r') as f:
    app.config['PERSONA_FIELD_CONFIG'] = json.load(f)
```

## Field Configuration Format

Each field configuration must follow this structure:

```json
{
  "category_name": {
    "label": "Display Name",
    "description": "Category description",
    "fields": [
      {
        "name": "field_name",
        "type": "string|list|dict",
        "label": "Field Display Name",
        "description": "Field description",
        "options": ["option1", "option2"]  // Optional for string fields
      }
    ]
  }
}
```

The configuration must include the three categories: "psychographic", "behavioral", and "contextual".

## Integration with Other Applications

To integrate the Persona API with other applications:

1. **Install the client library**:
   ```bash
   pip install -e ./persona-client
   ```

2. **Use the client in your application**:
   ```python
   from personaclient import PersonaClient
   
   client = PersonaClient(base_url="http://localhost:5050")
   personas = client.get_personas()
   ```

## Troubleshooting

- **Database Migration Errors**: If you encounter errors during migration, try running the migration with the `--dry-run` flag to check for issues.
- **API Connection Issues**: Ensure the Persona Service is running and the `PERSONA_API_BASE_URL` is correctly set in `persona_config.py`.
- **UI Rendering Issues**: Check that the field configuration structure matches what the templates expect.
