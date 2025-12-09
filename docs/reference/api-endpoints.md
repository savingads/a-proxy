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

Send a message to Claude AI in persona context.

**Request Body (JSON):**

```json
{
    "message": "User message text",
    "persona_id": 1,
    "conversation_history": []
}
```

**Response:**

```json
{
    "response": "Claude's response text",
    "conversation_id": "uuid"
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

### Browse Page

```
POST /browse
```

Navigate to a URL as the selected persona.

**Form Fields:**

| Field | Type | Description |
|-------|------|-------------|
| url | string | Target URL |
| persona_id | int | Persona to use |

## VPN Endpoints

### VPN Status

```
GET /vpn/status
```

Returns current VPN connection status.

**Response:**

```json
{
    "connected": true,
    "server": "us1234.nordvpn.com",
    "region": "US",
    "ip": "xxx.xxx.xxx.xxx"
}
```

### Connect VPN

```
POST /vpn/connect
```

**Form Fields:**

| Field | Type | Description |
|-------|------|-------------|
| server | string | Server identifier |
| protocol | string | udp or tcp |

### Disconnect VPN

```
POST /vpn/disconnect
```

Terminates VPN connection.

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
