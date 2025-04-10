# Dynamic Persona Schema Implementation

This document explains the dynamic schema approach used for personas in A-Proxy.

## Overview

The persona system in A-Proxy uses a dynamic schema that allows for flexible data structures without requiring database schema changes when adding or modifying fields. This is achieved through a combination of:

1. A fixed schema for essential demographic information
2. A flexible JSON-based storage for all other persona attributes
3. A configuration-driven approach for defining field structure

## Database Schema

### Core Tables

The persona database includes the following tables:

- **personas**: Stores core persona information (ID, name, timestamps)
- **demographic_data**: Stores fixed demographic fields (coordinates, language, location)
- **persona_attributes**: Stores dynamic attributes as JSON data

### Dynamic Attributes Schema

The `persona_attributes` table uses a three-column approach:

| Column | Description |
|--------|-------------|
| persona_id | Foreign key to persona |
| category | Category of the attribute ("psychographic", "behavioral", or "contextual") |
| data | JSON data containing all fields for that category |

This approach allows for:
- Adding new fields without schema changes
- Storing complex nested data structures
- Different field sets for different personas

## Field Configuration

The field configuration is defined in `persona_field_config.py` and determines what fields are available in each category. This configuration is used by:

1. The API layer to validate and transform data
2. The database layer to store and retrieve data
3. The UI layer to render forms and views dynamically

### Configuration Structure

```python
PERSONA_FIELD_CONFIG = {
    "psychographic": {
        "label": "Psychographic Data",
        "description": "Information about personality, values, opinions, interests, lifestyle, etc.",
        "fields": [
            {
                "name": "interests",
                "type": "list",
                "label": "Interests",
                "description": "Activities, topics, or subjects the persona is interested in"
            },
            # More fields here...
        ]
    },
    # "behavioral" and "contextual" categories follow the same pattern
}
```

### Field Types

The system supports three field types:

1. **string**: Simple text fields (may include options for predefined values)
2. **list**: Array of values stored as JSON arrays
3. **dict**: Key-value pairs stored as JSON objects

## How it Works

### Data Storage

When a persona is created or updated:

1. Basic information is stored in the `personas` table
2. Demographic data is stored in the `demographic_data` table
3. For each category (psychographic, behavioral, contextual):
   - The data is validated against the field configuration
   - It's converted to a JSON structure
   - Stored in the `persona_attributes` table with the appropriate category

### Data Retrieval

When retrieving a persona:

1. Basic data is fetched from the `personas` table
2. Demographic data is fetched from the `demographic_data` table
3. Dynamic attributes are fetched from the `persona_attributes` table
4. The data is restructured into a unified JSON object that includes all attributes

### Example Response

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

## Customizing the Schema

To customize the fields available in your personas:

1. Edit `persona_field_config.py` to modify the `PERSONA_FIELD_CONFIG` dictionary
2. Restart the application

No database migration is required because the schema is flexible. New fields will appear in the UI and API automatically.

## Benefits

This dynamic schema approach provides several advantages:

1. **Flexibility**: Add or modify fields without database migrations
2. **Customization**: Different applications can use different field sets
3. **Evolution**: The schema can evolve over time without breaking changes
4. **Compatibility**: Works with all implementation methods (API, mock, direct DB)

## Technical Implementation Details

### Database Layer

The dynamic schema is implemented in the database layer by:

- Using SQLAlchemy ORM with the `persona_attributes` model
- JSON serialization/deserialization when storing/retrieving data
- Field validation against the configuration

### API Layer

The API endpoints handle the dynamic schema by:

- Validating incoming data against the field configuration
- Converting between flat and nested structures as needed
- Building the combined response from multiple database entities

### UI Layer

The UI templates render dynamically based on:

- Field configuration to generate form inputs
- Data type to determine appropriate UI controls
- Nested structure to display hierarchical data
