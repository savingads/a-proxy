# System Architecture

This document describes the technical architecture of A-Proxy.

## Overview

A-Proxy is a Flask-based web application that combines persona management, web browsing simulation, and LLM integration for archival research purposes.

## System Diagram

```
+-------------------+     +-------------------+
|   Web Browser     |     |   Claude API      |
|   (User)          |     |   (Anthropic)     |
+--------+----------+     +--------+----------+
         |                         |
         v                         v
+--------+-------------------------+----------+
|                Flask Application            |
|  +-------------+  +-------------+           |
|  |   Routes    |  |  Services   |           |
|  | - persona   |  | - agent     |           |
|  | - journey   |  | - browsing  |           |
|  | - archives  |  | - vpn       |           |
|  | - agent     |  +-------------+           |
|  +------+------+                            |
|         |                                   |
|  +------v------+  +-------------+           |
|  | Database    |  |  Selenium   |           |
|  | Repository  |  |  WebDriver  |           |
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
                    |   OpenVPN   |
                    |   (NordVPN) |
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

Selenium WebDriver controls Chromium for web browsing:

| Component | Purpose |
|-----------|---------|
| Selenium | Browser automation framework |
| Chromium | Headless browser execution |
| WebDriver | Browser control interface |

### VPN Integration

OpenVPN client for geographic simulation:

| Component | Purpose |
|-----------|---------|
| OpenVPN | VPN client |
| NordVPN configs | Server configuration files |
| VPN routes | Connection management endpoints |

### LLM Integration

Claude API integration for persona conversations:

| Component | File | Purpose |
|-----------|------|---------|
| Agent Routes | `routes/agent.py` | Chat endpoints |
| Agent Service | `utils/agent.py` | API wrapper |

## Data Flow

### Persona Browsing Flow

```
1. User selects persona
2. System configures browser context:
   - User-Agent based on device_type
   - Accept-Language based on language
   - Viewport based on screen_size
3. If VPN enabled:
   - Connect to regional server
   - Verify exit IP
4. Navigate to URL via Selenium
5. Capture page content
6. Create waypoint record
7. Return rendered page to user
```

### Chat Flow

```
1. User sends message
2. System builds context:
   - Persona attributes
   - Conversation history
3. Send to Claude API
4. Receive response
5. Create waypoint record (type: agent)
6. Return response to user
```

## Directory Structure

```
a-proxy/
├── app.py                    # Application entry
├── config.py                 # Configuration
├── database/                 # Data layer
├── routes/                   # HTTP handlers
│   ├── agent.py             # Claude integration
│   ├── persona_api_db.py    # Persona CRUD
│   ├── journey.py           # Journey management
│   ├── browsing.py          # Web browsing
│   ├── archives.py          # Archive management
│   ├── vpn.py               # VPN control
│   └── auth.py              # Authentication
├── services.py              # Business logic
├── utils/                   # Utilities
│   ├── agent.py            # Agent service wrapper
│   └── persona_client_db.py # DB client adapter
├── templates/               # HTML templates
├── static/                  # Static assets
├── data/                    # SQLite database
├── archives/                # Archived pages
├── nordvpn/                 # VPN configuration
└── tests/                   # Test suite
```

## Deployment Models

### Local Development

```
Python 3.8+ → Flask dev server → SQLite
                    ↓
              Chromium (local)
```

### Docker Deployment

```
Docker Container
├── Flask Application
├── Chromium Browser
├── OpenVPN Client
└── SQLite Database
    ↓
Volume Mounts:
├── ./data → /app/data
├── ./archives → /app/archives
└── ./nordvpn → /app/nordvpn
```

## Security Considerations

### Authentication

- Session-based authentication via Flask-Login
- Password hashing with Werkzeug security
- Session cookies with configurable security

### Data Storage

- SQLite database in `data/` directory
- VPN credentials in `nordvpn/auth.txt`
- No encryption at rest (local deployment assumption)

### Network

- VPN traffic routed through OpenVPN
- Local API keys stored in environment variables
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

## Related Documentation

- [API Endpoints](api-endpoints.md) - HTTP interface
- [Database Schema](database-schema.md) - Data structures
- [Installation](../getting-started/installation.md) - Setup guide
