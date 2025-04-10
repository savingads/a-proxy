# Persona API Client

A Python client library for interacting with the Persona API Service.

## Installation

```bash
pip install personaclient
```

Or install from the repository:

```bash
pip install -e .
```

## Usage

```python
from personaclient import PersonaClient
from personaclient.exceptions import PersonaNotFoundError, PersonaValidationError

# Initialize the client
client = PersonaClient(
    base_url="http://localhost:5050",  # Default URL if running locally
    api_version="v1",  # API version
    timeout=10,  # Request timeout in seconds
    auth_token=None  # JWT auth token if required
)

# Get all personas
personas = client.get_all_personas(page=1, per_page=20)
print(f"Total personas: {personas['total']}")
for persona in personas['personas']:
    print(f"Persona: {persona['name']}")

# Get a specific persona
try:
    persona = client.get_persona(persona_id=123)
    print(f"Found persona: {persona['name']}")
except PersonaNotFoundError:
    print("Persona not found")

# Create a new persona
try:
    new_persona = client.create_persona({
        "name": "John Doe",
        "demographic": {
            "language": "en-US",
            "country": "US",
            "city": "New York",
            "region": "NY",
            "geolocation": "40.7128,-74.0060"
        }
    })
    print(f"Created persona with ID: {new_persona['id']}")
except PersonaValidationError as e:
    print(f"Validation error: {e}")

# Update a persona
try:
    updated_persona = client.update_persona(123, {
        "name": "Jane Doe",
        "demographic": {
            "country": "CA"
        }
    })
    print(f"Updated persona: {updated_persona['name']}")
except PersonaNotFoundError:
    print("Persona not found")

# Delete a persona
try:
    result = client.delete_persona(123)
    print(f"Delete result: {result['message']}")
except PersonaNotFoundError:
    print("Persona not found")

# Working with specialized data components
try:
    # Get demographic data
    demographic = client.get_demographic_data(123)
    print(f"Demographic: {demographic}")
    
    # Update demographic data
    client.update_demographic_data(123, {
        "language": "fr-CA",
        "country": "CA"
    })
    
    # Similar methods exist for other data types
    psychographic = client.get_psychographic_data(123)
    behavioral = client.get_behavioral_data(123)
    contextual = client.get_contextual_data(123)
    
except PersonaNotFoundError:
    print("Persona not found")
```

## Error Handling

The client provides several exception classes for handling different types of errors:

- `PersonaClientError`: Base exception for all client errors
- `PersonaNotFoundError`: Raised when a persona is not found (404)
- `PersonaValidationError`: Raised when there's a validation error with the data (400)
- `PersonaAPIError`: Raised for other API errors

## Development

To install development dependencies:

```bash
pip install -e ".[dev]"
```

To run tests:

```bash
pytest
