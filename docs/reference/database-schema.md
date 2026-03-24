# Database Schema

A-Proxy uses SQLite for data storage. This document describes the database schema and relationships.

## Database Location

```
data/personas.db
```

## Entity Relationship Diagram

```
+-------------+       +-------------------+
|   personas  |------>| demographic_data  |
+-------------+       +-------------------+
      |
      +-------------->+-------------------+
      |               | psychographic_data|
      |               +-------------------+
      |
      +-------------->+-------------------+
      |               | behavioral_data   |
      |               +-------------------+
      |
      +-------------->+-------------------+
      |               | contextual_data   |
      |               +-------------------+
      |
      +-------------->+-------------------+
                      |     journeys      |
                      +-------------------+
                             |
                             v
                      +-------------------+
                      |    waypoints      |
                      +-------------------+

+-------------------+       +-------------------+
| archived_websites |------>|     mementos      |
+-------------------+       +-------------------+

+-------------------+       +-------------------+
|      users        |       |     settings      |
+-------------------+       +-------------------+
```

## Tables

### personas

Core persona identity records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| name | TEXT | NOT NULL | Persona display name |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last modification |

### demographic_data

Geographic and demographic attributes.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| persona_id | INTEGER | NOT NULL, FK | Reference to personas |
| latitude | REAL | | Geographic latitude |
| longitude | REAL | | Geographic longitude |
| language | TEXT | | Language code (e.g., "en-US") |
| country | TEXT | | Country name |
| city | TEXT | | City name |
| region | TEXT | | State/province/region |
| age | INTEGER | | Age in years |
| gender | TEXT | | Gender identity |
| education | TEXT | | Education level |
| income | TEXT | | Income bracket |
| occupation | TEXT | | Profession |

**Foreign Keys:** `persona_id` references `personas(id)` ON DELETE CASCADE

### psychographic_data

Psychological and value-based attributes.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| persona_id | INTEGER | NOT NULL, FK | Reference to personas |
| interests | TEXT | | JSON array of interests |
| personal_values | TEXT | | JSON array of values |
| attitudes | TEXT | | JSON array of attitudes |
| lifestyle | TEXT | | Lifestyle description |
| personality | TEXT | | Personality description |
| opinions | TEXT | | JSON array of opinions |

**Note:** List fields stored as JSON strings.

**Foreign Keys:** `persona_id` references `personas(id)` ON DELETE CASCADE

### behavioral_data

Online behavior and usage patterns.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| persona_id | INTEGER | NOT NULL, FK | Reference to personas |
| browsing_habits | TEXT | | JSON array of habits |
| purchase_history | TEXT | | JSON array of purchases |
| brand_interactions | TEXT | | JSON array of brands |
| device_usage | TEXT | | JSON object of device patterns |
| social_media_activity | TEXT | | JSON object of social activity |
| content_consumption | TEXT | | JSON object of consumption patterns |

**Note:** List fields stored as JSON arrays, object fields as JSON objects.

**Foreign Keys:** `persona_id` references `personas(id)` ON DELETE CASCADE

### contextual_data

Situational and environmental context.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| persona_id | INTEGER | NOT NULL, FK | Reference to personas |
| time_of_day | TEXT | | Activity time preference |
| day_of_week | TEXT | | Day preference |
| season | TEXT | | Seasonal context |
| weather | TEXT | | Weather conditions |
| device_type | TEXT | | Primary device |
| browser_type | TEXT | | Primary browser |
| screen_size | TEXT | | Display resolution |
| connection_type | TEXT | | Network connection |

**Foreign Keys:** `persona_id` references `personas(id)` ON DELETE CASCADE

### journeys

Interaction session records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| name | TEXT | NOT NULL | Journey name |
| description | TEXT | | Detailed description |
| persona_id | INTEGER | | Associated persona |
| journey_type | TEXT | DEFAULT 'marketing' | Type classification |
| status | TEXT | DEFAULT 'active' | Current status |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last modification |

### waypoints

Individual interaction records within journeys.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| journey_id | INTEGER | NOT NULL, FK | Parent journey |
| url | TEXT | NOT NULL | URL or reference |
| title | TEXT | | Page/waypoint title |
| notes | TEXT | | User notes |
| screenshot_path | TEXT | | Path to screenshot |
| timestamp | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Waypoint time |
| sequence_number | INTEGER | | Order in journey |
| metadata | TEXT | | JSON additional data |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation |
| type | TEXT | DEFAULT 'browse' | browse or agent |
| agent_data | TEXT | | JSON conversation data |

**Foreign Keys:** `journey_id` references `journeys(id)` ON DELETE CASCADE

### archived_websites

Web archive target records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| uri_r | TEXT | NOT NULL | Target URI |
| persona_id | INTEGER | | Capture persona |
| archive_type | TEXT | NOT NULL | filesystem, etc. |
| archive_location | TEXT | NOT NULL | Storage path |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

### mementos

Individual archive captures.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| archived_website_id | INTEGER | NOT NULL, FK | Parent archive |
| memento_datetime | TIMESTAMP | NOT NULL | Capture timestamp |
| memento_location | TEXT | NOT NULL | Storage location |
| http_status | INTEGER | | HTTP response code |
| content_type | TEXT | | MIME type |
| content_length | INTEGER | | Content size |
| headers | TEXT | | JSON response headers |
| screenshot_path | TEXT | | Screenshot location |
| internet_archive_id | TEXT | | IA submission ID |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation |

**Foreign Keys:** `archived_website_id` references `archived_websites(id)` ON DELETE CASCADE

### users

Authentication records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| email | TEXT | UNIQUE NOT NULL | User email |
| password_hash | TEXT | NOT NULL | Hashed password |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation |

### settings

Application configuration.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| key | TEXT | PRIMARY KEY | Setting identifier |
| value | TEXT | | Setting value |
| description | TEXT | | Human-readable description |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last modification |

## Data Access Patterns

### Repository Pattern

```python
from database.repositories import PersonaRepository

repo = PersonaRepository()
persona = repo.get(1)
personas = repo.get_all()
persona_id = repo.save(data)
repo.delete(1)
```

### Legacy Function API

```python
from database import get_persona, save_persona, delete_persona

persona = get_persona(1)
persona_id = save_persona(data)
delete_persona(1)
```

## Initialization

Database tables are created on first run:

```python
from database import initialize_database
initialize_database()
```

## Backup and Recovery

### Backup

```bash
cp data/personas.db data/personas_backup.db
```

### Reset

```bash
rm data/personas.db
python -c "from database import initialize_database; initialize_database()"
```

## Related Documentation

- [System Architecture](architecture.md) - Overall system design
- [Persona Model](../concepts/persona-model.md) - Persona data model
- [API Endpoints](api-endpoints.md) - HTTP interface
