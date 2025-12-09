# Settings

This guide documents the configuration options available in A-Proxy.

## Accessing Settings

Navigate to **Settings** in the main navigation menu.

## Configuration Categories

### API Keys

| Setting | Description |
|---------|-------------|
| Anthropic API Key | Required for Claude AI chat functionality |

API keys can also be set via environment variables (recommended for production).

#### Setting via Environment

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Or in `.env` file:

```
ANTHROPIC_API_KEY=sk-ant-...
```

### VPN Configuration

| Setting | Description |
|---------|-------------|
| VPN Enabled | Toggle VPN functionality |
| Default Protocol | UDP or TCP |
| Server Selection | Automatic or manual |

See [VPN Integration](vpn-integration.md) for detailed configuration.

### Browser Settings

| Setting | Description | Default |
|---------|-------------|---------|
| Default Viewport | Screen size for captures | 1920x1080 |
| JavaScript Enabled | Execute JS during browsing | true |
| Image Loading | Load images during browsing | true |
| Timeout | Page load timeout (seconds) | 30 |

### Archive Settings

| Setting | Description | Default |
|---------|-------------|---------|
| Archive Location | Directory for saved archives | ./archives |
| Screenshot Format | PNG or JPEG | PNG |
| Capture Full Page | Screenshot entire page or viewport | viewport |
| Save HTML | Include raw HTML in archive | true |

### Session Settings

| Setting | Description | Default |
|---------|-------------|---------|
| Session Timeout | Inactivity timeout (minutes) | 30 |
| Auto-save Journeys | Save journey progress automatically | true |
| Cookie Persistence | Retain cookies between sessions | per-persona |

## Environment Variables

Settings can be configured via environment variables:

| Variable | Setting | Example |
|----------|---------|---------|
| `ANTHROPIC_API_KEY` | Claude API key | sk-ant-... |
| `SECRET_KEY` | Flask session key | random-string |
| `DEBUG` | Debug mode | true/false |
| `PORT` | Server port | 5002 |

### Example .env File

```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
SECRET_KEY=your-secret-key-here
DEBUG=false
PORT=5002
```

## Database Location

The SQLite database is stored at:

```
data/personas.db
```

This includes:

- Persona records
- Journey and waypoint data
- User accounts
- Settings

### Backup

To backup the database:

```bash
cp data/personas.db data/personas_backup_$(date +%Y%m%d).db
```

### Reset

To reset the database:

```bash
rm data/personas.db
python database.py
```

## User Management

### Default Account

| Field | Value |
|-------|-------|
| Email | admin@example.com |
| Password | password |

Change these credentials after initial setup.

### Adding Users

Currently managed through direct database access. Future versions may include a user management interface.

## Logging

### Log Location

Application logs are output to stdout/stderr by default.

### Log Level

Set via environment:

```bash
export LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

## Performance Settings

### Concurrent Sessions

| Setting | Description | Default |
|---------|-------------|---------|
| Max Concurrent Browsers | Simultaneous browser instances | 3 |
| Queue Size | Pending archive requests | 100 |

### Resource Limits

Docker deployments can configure resource limits in `docker-compose.yml`:

```yaml
services:
  a-proxy:
    deploy:
      resources:
        limits:
          memory: 2G
```

## Troubleshooting Settings

### Common Issues

| Problem | Setting to Check |
|---------|------------------|
| API calls fail | Anthropic API Key |
| Pages don't load | Browser timeout, JavaScript enabled |
| VPN not working | VPN enabled, credentials |
| Archives incomplete | Archive location permissions |

### Diagnostic Information

View system status:

1. Navigate to **Settings**
2. Check **System Status** section
3. Review connection status for all services

## Related Guides

- [Installation](../getting-started/installation.md) - Initial configuration
- [VPN Integration](vpn-integration.md) - VPN-specific settings
