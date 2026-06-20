# System Architecture

This document describes the technical architecture of A-Proxy.

## Overview

A-Proxy is a Flask-based web application that combines persona management, web browsing simulation, and LLM integration for archival research purposes.

## System Diagram

```
+-------------------+     +-------------------+
|   Web Browser     |     |   LLM Provider    |
|   (User)          |     | (Local/Cloud API) |
+--------+----------+     +--------+----------+
         |                         |
         v                         v
+--------+-------------------------+----------+
|                Flask Application            |
|  +-------------+  +-------------+           |
|  |   Routes    |  |  Services   |           |
|  | - persona   |  | - llm_client|           |
|  | - journey   |  | - agent     |           |
|  | - archives  |  | - browsing  |           |
|  | - agent     |  +-------------+           |
|  | - network   |                            |
|  +------+------+                            |
|         |                                   |
|  +------v------+  +-------------+           |
|  | Database    |  | Playwright  |           |
|  | Repository  |  | BrowserMgr  |           |
|  +------+------+  +------+------+           |
+---------+----------------+------------------+
          |                |
          v                v
   +------+------+  +------+------+
   |   SQLite    |  |  Chromium   |
   |   Database  |  |  Browser    |
   +-------------+  +------+------+
                           |
                    +------v------+
                    | SOCKS5/HTTP |
                    |    Proxy    |
                    | (optional)  |
                    +-------------+
```

## Components

### Flask Application

The core web application built on Flask:

| Component | File | Purpose |
|-----------|------|---------|
| Entry Point | `app.py` | Application initialization |
| Configuration | `config.py` | Settings and environment |
| Routes | `routes/` | HTTP endpoint handlers |
| Templates | `templates/` | Jinja2 HTML templates |
| Static | `static/` | CSS, JavaScript, images |

### Database Layer

Repository pattern implementation for data access:

```
database/
├── __init__.py          # Main exports, backward compatibility
├── connection.py        # SQLite connection management
├── models/              # Domain model dataclasses
└── repositories/        # Data access classes
    ├── persona.py       # PersonaRepository
    ├── journey.py       # JourneyRepository
    ├── archive.py       # ArchiveRepository
    ├── user.py          # UserRepository
    └── settings.py      # SettingsRepository
```

### Browser Automation

Playwright controls Chromium in two modes: headless ephemeral contexts for visit/archive, and persistent headful sessions for interactive persona browsing:

| Component | Purpose |
|-----------|---------|
| Playwright | Browser automation framework (sync API) |
| BrowserManager | Singleton manager in `utils/browser.py` |
| BrowserContext | Per-request isolated context for visit/archive (locale, geolocation, timezone, proxy) |
| BrowsingSession | Persistent, persona-scoped headful session (dataclass tracking page + navigation history) |
| Chromium | Runs headless for `visit_page`/`archive_page`; headful (`headless=False`) for interactive persona sessions |

#### Headful Browsing Sessions

In addition to the ephemeral per-request contexts, `BrowserManager.start_session()` launches a separate headful Chromium and holds a single active `BrowsingSession` tied to a persona. Unlike the per-request contexts, this session is persistent and persona-scoped; it survives across requests until stopped. `routes/browsing.py` exposes these endpoints:

| Endpoint | Purpose |
|----------|---------|
| `POST /start-session` | Launch a headful session for a persona (optional start URL) |
| `GET /session-status` | Report the active session (persona, current URL/title, history) |
| `POST /capture-page` | Screenshot the active session page |
| `POST /archive-page-from-session` | Archive the current session page as a memento |
| `POST /stop-session` | Close the active session |

### Network / Proxy

Optional proxy support for geographic simulation:

| Component | Purpose |
|-----------|---------|
| Proxy config | `utils/network.py` -- proxy URL, IP info |
| Network routes | `routes/network.py` -- status, set/clear proxy |
| Per-context proxy | Playwright routes each context through configured proxy |

### LLM Integration

Provider-agnostic LLM client supporting local and cloud models:

| Component | File | Purpose |
|-----------|------|---------|
| LLM Client | `utils/llm_client.py` | Multi-provider adapter (local, Anthropic, OpenAI) |
| Agent Service | `utils/agent.py` | High-level chat service |
| Agent Routes | `routes/agent.py` | Chat endpoints |

## Data Flow

### Persona Browsing Flow

```
1. User selects persona
2. System configures Playwright browser context:
   - locale based on language
   - geolocation based on lat/lng
   - timezone based on region
3. If proxy configured:
   - Route context through proxy
   - Verify exit IP
4. Navigate to URL via Playwright
5. Capture page content and screenshot
6. Return rendered page to user
```

The plain `visit-page` / `archive_page` endpoints do not record waypoints;
waypoints are created only when browsing within a journey/agent context.

### Chat Flow

```
1. User sends message
2. System builds context:
   - Persona attributes (system prompt)
   - Conversation history
3. Send to LLM via LLMClient (auto-detects provider)
4. Receive response
5. Create waypoint record (type: `agent` when chatting *with* the persona, `persona` when chatting *as* the persona)
6. Return response to user
```

## Directory Structure

```
a-proxy/
├── app.py                    # Application entry
├── config.py                 # Configuration
├── regions.json              # Region presets (language/geolocation/timezone)
├── database/                 # Data layer (repository pattern; connection context managers)
├── routes/                   # HTTP handlers
│   ├── agent.py             # LLM chat integration
│   ├── persona_api.py       # Persona CRUD
│   ├── journey.py           # Journey management
│   ├── browsing.py          # Web browsing (Playwright)
│   ├── archives.py          # Archive management
│   ├── network.py           # Proxy/network control
│   └── auth.py              # Authentication
├── services/                # Business logic (context mgmt, persona attributes)
├── utils/                   # Utilities
│   ├── browser.py           # Playwright BrowserManager
│   ├── persona_browser.py   # Persona → browser-context mapping
│   ├── geo.py               # Timezone/geolocation inference (single source)
│   ├── network.py           # Proxy config, IP info
│   ├── agent.py             # Agent service (LLM chat)
│   ├── llm_client.py        # Multi-provider LLM client
│   └── persona_client.py    # DB client adapter
├── templates/               # HTML templates
├── static/                  # Static assets
├── data/                    # SQLite database (runtime volume)
├── archives/                # Archived pages
└── tests/                   # Test suite
```

## Deployment Models

### Local Development

```
Python 3.10+ → Flask dev server → SQLite
                    ↓
              Playwright + Chromium
                    ↓ (optional)
              SOCKS5/HTTP Proxy
```

### Docker Deployment

```
Docker Container
├── Flask Application
├── Playwright + Chromium
└── SQLite Database
    ↓
Volume Mounts:
├── ./data → /app/data
└── ./archives → /app/archives
```

## Security Considerations

### Authentication

- Session-based authentication via Flask-Login
- Password hashing with Werkzeug security
- Session cookies with configurable security

### Data Storage

- SQLite database in `data/` directory
- No encryption at rest (local deployment assumption)

### Network

- Proxy traffic routed through Playwright per-context
- API keys stored in environment variables
- HTTPS recommended for production deployment

## Extensibility

### Adding New Routes

1. Create blueprint in `routes/`
2. Register in `app.py`
3. Add templates in `templates/`

### Adding New Repositories

1. Create class in `database/repositories/`
2. Export from `database/__init__.py`
3. Add backward-compatible functions if needed

### Adding New LLM Providers

1. Create adapter class in `utils/llm_client.py` extending `BaseAdapter`
2. Add provider detection in `LLMClient._initialize_adapter()` and `_auto_detect_provider()`
3. Add config variables in `config.py`

## Related Documentation

- [API Endpoints](api-endpoints.md) - HTTP interface
- [Database Schema](database-schema.md) - Data structures
- [Installation](../getting-started/installation.md) - Setup guide
