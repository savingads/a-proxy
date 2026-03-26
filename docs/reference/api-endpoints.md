# API Endpoints

This reference documents the HTTP endpoints available in A-Proxy.

## Overview

A-Proxy exposes both web interface routes and API endpoints. Most routes serve HTML templates; those marked as API return JSON.

## Authentication

Most endpoints require authentication via session cookie. Login through `/login` to establish a session.

## Persona Endpoints

### List Personas

```
GET /personas
```

Returns HTML page listing all personas.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | int | 1 | Page number |
| per_page | int | 100 | Items per page |

### View Persona

```
GET /persona/<persona_id>
```

Returns HTML page with persona details.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| persona_id | int | Persona identifier |

### Create Persona

```
GET /create-persona
POST /create-persona
```

GET returns the creation form. POST creates a new persona.

**POST Form Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| persona_name | string | Yes | Persona display name |
| latitude | float | No | Geographic latitude |
| longitude | float | No | Geographic longitude |
| language | string | No | Language code (e.g., "en-US") |
| country | string | No | Country name |
| city | string | No | City name |
| age | int | No | Age in years |
| interests | string | No | Comma-separated interests |
| (additional fields) | various | No | See Persona Model |

### Edit Persona

```
GET /edit-persona/<persona_id>
POST /edit-persona/<persona_id>
```

GET returns the edit form. POST updates the persona.

### Delete Persona

```
POST /delete-persona/<persona_id>
```

Deletes the specified persona.

### Export Persona (JSON)

```
GET /persona/<persona_id>/export
```

Downloads the persona as a JSON file with all four attribute categories. Internal database fields (`id`, `persona_id`) are stripped from the export.

**Response:** JSON file download (`Content-Disposition: attachment`).

### Use Persona

```
GET /use-persona/<persona_id>
```

Sets the persona as active in the current session, storing geolocation and language for browsing.

### Field Configuration

```
GET /field-config
```

Returns persona field configuration as JSON (API endpoint).

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| category | string | Filter by category (psychographic, behavioral, contextual) |
| field | string | Filter by specific field name |

## Journey Endpoints

### List Journeys

```
GET /journeys
```

Returns HTML page listing all journeys.

### View Journey

```
GET /journey/<journey_id>
```

Returns HTML page with journey details and waypoints.

### Create Journey

```
GET /journey/create
POST /journey/create
```

**POST Form Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Journey name |
| description | string | No | Journey description |
| persona_id | int | Yes | Associated persona |
| journey_type | string | No | marketing, research, shopping, general |

**Response (AJAX):**

```json
{
    "success": true,
    "journey_id": 123,
    "message": "Journey created successfully"
}
```

### Add Waypoint

```
POST /journey/<journey_id>/waypoint
```

**Form Fields:**

| Field | Type | Description |
|-------|------|-------------|
| url | string | Waypoint URL |
| title | string | Page title |
| type | string | browse or agent |
| notes | string | Optional notes |

## Archive Endpoints

### List Archives

```
GET /archives
```

Returns HTML page listing archived pages.

### View Archive

```
GET /archive/<archive_id>
```

Returns HTML page with archive details and content.

## Agent Endpoints

### Send Message

```
POST /agent/message
```

Send a message to the configured LLM in persona context.

**Request Body (JSON):**

```json
{
    "message": "User message text",
    "persona_id": 1,
    "model": "optional-model-override",
    "system_prompt": "optional-custom-prompt",
    "chat_history": []
}
```

**Response:**

```json
{
    "success": true,
    "response": "LLM response text",
    "conversation_id": "uuid",
    "context_depth": {}
}
```

### Direct Chat

```
GET /direct-chat/<persona_id>
```

Returns HTML chat interface for persona conversations.

## Browsing Endpoints

### Interact As

```
GET /interact-as
```

Returns HTML interface for browsing/chatting as a persona.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| persona_id | int | Pre-select persona |
| mode | string | browse or chat |

### Direct Browse (Launch Page)

```
GET /direct-browse/<persona_id>
```

Returns the headful browsing launch/control page for a persona. Accepts optional `journey_id` query parameter to link waypoints to a specific journey.

### Headful Session Endpoints (API)

These JSON endpoints manage headful browsing sessions:

#### Start Session

```
POST /start-session
```

Launches a visible Chromium window configured with the persona's locale, geolocation, timezone, and proxy.

**Request Body (JSON):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| persona_id | int | Yes | Persona to browse as |
| start_url | string | No | Starting URL (default: google.com) |

**Response:**

```json
{"success": true, "persona_id": 1}
```

#### Session Status

```
GET /session-status
```

Returns the current browsing session state including URL and navigation history.

**Response:**

```json
{
    "active": true,
    "persona_id": 1,
    "current_url": "https://example.com",
    "current_title": "Example Domain",
    "history": [
        {"url": "https://google.com", "title": "Google", "timestamp": "..."},
        {"url": "https://example.com", "title": "Example Domain", "timestamp": "..."}
    ],
    "started_at": "2026-03-26T04:30:00"
}
```

#### Capture Page

```
POST /capture-page
```

Takes a screenshot of the current page in the active browsing session.

#### Archive Page from Session

```
POST /archive-page-from-session
```

Archives the current page from the active session (saves HTML, screenshot, and metadata).

#### Stop Session

```
POST /stop-session
```

Closes the headful browser and ends the session.

### Headless Browsing Endpoints

#### Visit Page

```
POST /visit-page
```

Visit a URL headlessly with persona settings. Used for programmatic automation.

**Form Fields:**

| Field | Type | Description |
|-------|------|-------------|
| url | string | Target URL |
| language | string | Locale (e.g., "en-US") |
| geolocation | string | "lat,lng" format |
| take_screenshot | string | "true" to capture screenshot |

#### Archive Page

```
POST /archive_page
```

Archive a URL headlessly (HTML, screenshot, metadata saved to filesystem and database).

**Form Fields:**

| Field | Type | Description |
|-------|------|-------------|
| url | string | Target URL |
| language | string | Locale |
| geolocation | string | "lat,lng" format |
| persona_id | int | Persona used for the archive |

## Network Endpoints

### Network Status

```
GET /network-status
```

Returns current proxy and IP information.

**Response:**

```json
{
    "proxy_configured": true,
    "proxy_url": "socks5://host:port",
    "ip_info": {
        "ip": "203.0.113.1",
        "city": "New York",
        "region": "NY",
        "country": "US"
    }
}
```

### Set Proxy

```
POST /set-proxy
```

Sets a proxy URL for the current session.

**Form Fields:**

| Field | Type | Description |
|-------|------|-------------|
| proxy_url | string | Proxy URL (e.g., socks5://host:port) |

### Clear Proxy

```
POST /clear-proxy
```

Removes the session proxy override.

### Get Region Geolocation

```
GET /get-region-geolocation/<code>
```

Returns geolocation data for a region code.

**Response:**

```json
{
    "geolocation": "37.7749,-122.4194",
    "language": "en-US",
    "name": "United States",
    "timezone": "America/New_York"
}
```

## Authentication Endpoints

### Login

```
GET /login
POST /login
```

**POST Form Fields:**

| Field | Type | Description |
|-------|------|-------------|
| email | string | User email |
| password | string | User password |

### Logout

```
GET /logout
```

Ends the current session.

## Error Responses

Standard error response format:

```json
{
    "success": false,
    "error": "Error description"
}
```

HTTP status codes:

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 500 | Server Error |

## Related Documentation

- [Database Schema](database-schema.md) - Data structures
- [System Architecture](architecture.md) - System design
