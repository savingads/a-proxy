# API Endpoints

This reference documents the HTTP endpoints available in A-Proxy.

## Overview

A-Proxy exposes both web interface routes and API endpoints. Most routes serve HTML templates; those marked as API return JSON.

## Authentication

Authentication via session cookie is only enforced on the agent endpoints (`/agent`, `/agent/message`, `/direct-chat/<persona_id>` and its `/save` action, and the `/journey/<journey_id>/agent...` routes) and on `/logout`. The persona, journey, archive, browsing, and network endpoints are not protected by `@login_required` and are publicly accessible. Login through `/login` to establish a session for the protected agent endpoints.

## Home / Utility Endpoints

### Home

```
GET /
GET /home
```

Renders the home page (proxy/IP status and detected language).

### Dashboard

```
GET /dashboard
```

Renders the dashboard page.

### Geolocation Test

```
GET /geolocation-test
```

Renders the geolocation test page. Accepts optional `language` and `geolocation` query parameters.

### Get Headers (API)

```
GET /get-headers
```

Returns selected request headers as JSON.

**Response:**

```json
{
    "accept-language": "en-US"
}
```

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

Deletes the specified persona. `<persona_id>` must be an integer (Flask `<int:...>` converter); non-integer values return 404.

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
POST /journey/<journey_id>/add-waypoint
```

**Form Fields:**

| Field | Type | Description |
|-------|------|-------------|
| url | string | Waypoint URL |
| title | string | Page title |
| type | string | browse or agent |
| notes | string | Optional notes |

### Edit Journey

```
GET /journey/<journey_id>/edit
POST /journey/<journey_id>/edit
```

GET returns the journey edit form. POST updates the journey (`name`, `description`, `persona_id`, `journey_type`, `status`).

### Delete Journey

```
POST /journey/<journey_id>/delete
```

Deletes the journey and all of its waypoints, then redirects to the journey list.

### Browse Journey

```
GET /journey/<journey_id>/browse
```

Starts a browsing session for the journey's linked persona (redirects to `/direct-browse/<persona_id>`). If the journey has no linked persona, redirects back with a warning.

### Visualize Journey

```
GET /journey/<journey_id>/visualize
```

Renders the journey's waypoints as a timeline.

### Complete Journey

```
POST /journey/<journey_id>/complete
```

Marks the journey as completed.

### Edit Waypoint

```
POST /journey/waypoint/<waypoint_id>/edit
```

Updates a waypoint's `title` and `notes`. Returns JSON for AJAX requests; otherwise redirects with a flash message.

### Delete Waypoint

```
POST /journey/waypoint/<waypoint_id>/delete
```

Deletes a waypoint. Returns JSON for AJAX requests; otherwise redirects with a flash message.

### Save Page as Waypoint

```
POST /save-waypoint/<persona_id>
```

Saves a page from a direct browsing session as a waypoint, optionally creating a new journey or attaching to an existing one.

### Create Journey from Browse

```
POST /create-journey-from-browse/<persona_id>
```

Creates a journey from a direct browsing session, adding a waypoint for each visited URL.

**Form Fields:**

| Field | Type | Description |
|-------|------|-------------|
| name | string | Journey name |
| description | string | Optional description |
| journey_type | string | Journey type (default: research) |
| visited_urls | string | JSON array of visited URLs |
| current_url | string | Current page URL |

### Browse As (Legacy)

```
GET /browse-as
```

Legacy route that redirects to `/interact-as`.

## Archive Endpoints

### List Archives

```
GET /archives
```

Returns HTML page listing archived pages.

### View Archive

```
GET /archives/<archived_website_id>
```

Returns HTML page with archive details and content. Individual mementos are viewed at `GET /archives/<archived_website_id>/mementos/<memento_id>`.

### Delete Archive

```
POST /delete-archive/<archived_website_id>
```

Deletes an archived website and all of its associated mementos, then redirects to the archive list.

### Submit Memento to Internet Archive

```
POST /submit-to-internet-archive/<memento_id>
```

Submits the given memento's URL to the Internet Archive. Honors the rate limit configured in archive settings. Returns JSON when called with `X-Requested-With: XMLHttpRequest`; otherwise redirects with a flash message.

### Archive Settings

```
GET /settings
POST /settings
```

GET renders the archive settings page. POST updates the Internet Archive integration settings.

**POST Form Fields:**

| Field | Type | Description |
|-------|------|-------------|
| internet_archive_enabled | string | `on` to enable Internet Archive submissions |
| internet_archive_rate_limit | int | Daily submission limit (clamped to 1–100; defaults to 10) |

### Internet Archive Status (API)

```
GET /api/internet-archive-status
```

Returns Internet Archive integration status as JSON.

**Response:**

```json
{
    "enabled": true,
    "submissions_today": 0,
    "rate_limit": 10,
    "can_submit": true,
    "remaining": 10
}
```

## Agent Endpoints

All agent endpoints require authentication (`@login_required`).

### Agent Chat (Standalone UI)

```
GET /agent
```

Returns the standalone agent chat interface, listing the LLM models available based on the configured providers.

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

Returns HTML chat interface for persona conversations. Requires authentication.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| mode | string | with | Chat perspective: `with` (chat with the persona) or `as` (chat as the persona) |
| target_persona_id | int | — | Optional second persona for the conversation |
| journey_id | int | — | Link the chat to an existing journey |
| waypoint_id | int | — | Preload chat history from a saved waypoint |

### Save Direct Chat

```
POST /direct-chat/<persona_id>/save
```

Saves a direct chat as a waypoint, optionally creating a new journey or attaching to an existing one. Returns JSON for AJAX requests; otherwise redirects with a flash message.

### Journey Agent (UI)

```
GET /journey/<journey_id>/agent
```

Returns the agent interface for a specific journey.

### Journey Agent Message

```
POST /journey/<journey_id>/agent/message
```

Sends a message to the agent in the context of the given journey (its waypoints and associated persona).

**Request Body (JSON):**

```json
{
    "message": "User message text",
    "conversation_id": "optional-id"
}
```

### Save Journey Agent Conversation

```
POST /journey/<journey_id>/agent/save
```

Saves an agent conversation as a waypoint on the given journey.

**Request Body (JSON):**

```json
{
    "title": "Agent Conversation",
    "notes": "optional notes",
    "conversation_id": "optional-id",
    "conversation_history": []
}
```

## Browsing Endpoints

### Interact As

```
GET /interact-as
```

Returns HTML interface for browsing/chatting as a persona. This endpoint takes no query parameters.

### Direct Browse (Launch Page)

```
GET /direct-browse/<persona_id>
```

Returns the headful browsing launch/control page for a persona. Accepts optional `journey_id` query parameter to link waypoints to a specific journey. (This route is defined in the journey blueprint.)

### Test Geolocation

```
POST /test-geolocation
```

Stores the submitted `language` and `geolocation` in the session and redirects to the geolocation test page.

**Form Fields:**

| Field | Type | Description |
|-------|------|-------------|
| language | string | Locale (e.g., "en-US") |
| geolocation | string | "lat,lng" format |

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
GET /get-region-geolocation/<region_code>
```

Returns geolocation data for a region code. The code is upper-cased before lookup; unknown or invalid codes return 404 with `{"error": "Region not found"}`.

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
| username | string | User email (the form field is named `username` but holds the email value) |
| password | string | User password |

### Register

```
GET /register
POST /register
```

GET returns the registration form. POST creates a user account.

**POST Form Fields:**

| Field | Type | Description |
|-------|------|-------------|
| email | string | New user email |
| password | string | New user password |

### Logout

```
GET /logout
```

Ends the current session. Requires authentication.

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
