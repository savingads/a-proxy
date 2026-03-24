# Journeys and Waypoints

Journeys and waypoints provide the mechanism for recording and organizing persona interactions over time.

## Concepts

### Journey

A **journey** is a named collection of interactions linked to a specific persona. Each journey represents a session or series of sessions where the persona engages with the web or an AI agent.

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique identifier |
| `name` | string | Descriptive name for the journey |
| `description` | string | Optional detailed description |
| `persona_id` | integer | Link to the associated persona |
| `journey_type` | string | Type of journey (e.g., "marketing", "research") |
| `status` | string | Current status ("active", "completed", etc.) |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last modification timestamp |

### Waypoint

A **waypoint** is an individual step within a journey. Each waypoint records a discrete interaction such as visiting a URL or having a conversation with an AI agent.

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique identifier |
| `journey_id` | integer | Link to parent journey |
| `url` | string | URL visited or context reference |
| `title` | string | Page title or waypoint label |
| `notes` | string | User-added notes |
| `screenshot_path` | string | Path to captured screenshot |
| `timestamp` | datetime | When the waypoint was created |
| `sequence_number` | integer | Order within the journey |
| `type` | string | "browse" or "agent" |
| `agent_data` | JSON | Conversation data (for agent waypoints) |
| `metadata` | JSON | Additional context information |

## Waypoint Types

### Browse Waypoints

Created when navigating the web as a persona. Captures:

- URL visited
- Page title
- Screenshot of the page
- Browser context (cookies, headers)

### Agent Waypoints

Created during conversations with Claude AI. Captures:

- Conversation history
- Persona context provided to the AI
- Any persona attribute updates derived from the conversation

## Journey Types

| Type | Description | Use Case |
|------|-------------|----------|
| `marketing` | Consumer-focused browsing | Capturing ad experiences |
| `research` | Information-seeking behavior | Academic or professional research patterns |
| `shopping` | E-commerce interactions | Purchase journey analysis |
| `general` | Unspecified browsing | General web exploration |

## Data Flow

```
Journey Creation
      |
      v
+------------------+
|    Journey       |
|  - name          |
|  - persona_id    |
|  - journey_type  |
+------------------+
      |
      +-----> Waypoint 1 (browse)
      |         - url: https://example.com
      |         - screenshot: path/to/img.png
      |
      +-----> Waypoint 2 (agent)
      |         - conversation data
      |         - persona updates
      |
      +-----> Waypoint 3 (browse)
                - url: https://example.com/page2
                - screenshot: path/to/img2.png
```

## Example Journey

```python
# Journey structure
{
    "id": 1,
    "name": "Morning Coffee Shopping",
    "description": "Researching coffee equipment as Brooklyn chef persona",
    "persona_id": 1,
    "journey_type": "shopping",
    "status": "active",
    "waypoints": [
        {
            "id": 1,
            "sequence_number": 1,
            "type": "browse",
            "url": "https://www.coffee-gear.com",
            "title": "Coffee Equipment | Home",
            "timestamp": "2024-12-09T08:30:00Z"
        },
        {
            "id": 2,
            "sequence_number": 2,
            "type": "agent",
            "url": "agent://conversation",
            "title": "Discussion about espresso machines",
            "agent_data": {
                "messages": [
                    {"role": "user", "content": "What espresso machine would you recommend for a small restaurant?"},
                    {"role": "assistant", "content": "For a small restaurant, I'd suggest..."}
                ]
            },
            "timestamp": "2024-12-09T08:35:00Z"
        },
        {
            "id": 3,
            "sequence_number": 3,
            "type": "browse",
            "url": "https://www.coffee-gear.com/commercial/espresso",
            "title": "Commercial Espresso Machines",
            "timestamp": "2024-12-09T08:40:00Z"
        }
    ]
}
```

## Archival Value

Journeys and waypoints serve dual purposes:

### Web Archiving

- Record the sequence of pages visited
- Capture page content from the persona's perspective
- Document navigation patterns and user flows

### LLM Research

- Preserve conversations between personas and AI
- Track how AI responses evolve with increasing persona context
- Document persona development through chat interactions

## Metadata Capture

Waypoints can include rich metadata:

```python
{
    "metadata": {
        "browser": {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
            "viewport": "1920x1080",
            "language": "en-US"
        },
        "network": {
            "ip_region": "US-NY",
            "connection_type": "wifi"
        },
        "timing": {
            "load_time_ms": 1234,
            "time_on_page_ms": 45000
        }
    }
}
```

## Related Concepts

- [Persona Model](persona-model.md) - The 4-dimensional attribute framework
- [Archival Goals](archival-goals.md) - How journeys support archival research
- [Manage Journeys](../how-to/manage-journeys.md) - Working with journeys in the interface
