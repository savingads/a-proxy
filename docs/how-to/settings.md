# Settings

This guide documents the configuration options available in A-Proxy.

## Accessing Settings

Navigate to **Settings** in the main navigation menu.

## Configuration Categories

### LLM Provider

A-Proxy supports multiple LLM providers. Configure via environment variables:

| Setting | Description |
|---------|-------------|
| Local endpoint (vLLM/Ollama) | Recommended for self-hosted models |
| Anthropic API Key | For Claude AI chat functionality |
| OpenAI API Key | For GPT chat functionality |

See [Installation - LLM Configuration](../getting-started/installation.md#llm-configuration) for setup details.

### Proxy Configuration

| Setting | Description |
|---------|-------------|
| Proxy URL | SOCKS5/HTTP proxy for geo-IP shifting |
| Per-session override | Set via dashboard proxy controls |

See [Proxy & Geo-IP](proxy-setup.md) for detailed configuration.

### Browser Settings

| Setting | Description | Default |
|---------|-------------|---------|
| Default Viewport | Screen size for captures | 1920x1080 |
| JavaScript Enabled | Execute JS during browsing | true |
| Image Loading | Load images during browsing | true |
| Timeout | Page load timeout (seconds) | 30 |
| Headless Mode | Run browser without UI | true |

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

## Environment Variables

All settings can be configured via environment variables:

| Variable | Setting | Example |
|----------|---------|---------|
| `OPENAI_COMPATIBLE_URL` | Local LLM endpoint | `http://localhost:11434/v1` |
| `OPENAI_COMPATIBLE_MODEL` | Local model name | `qwen2.5:7b` |
| `ANTHROPIC_API_KEY` | Claude API key | `sk-ant-...` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `LLM_PROVIDER` | Force provider | `openai_compatible` |
| `SECRET_KEY` | Flask session key | random-string |
| `DEBUG` | Debug mode | true/false |
| `PROXY_URL` | Default proxy | `socks5://host:port` |
| `BROWSER_HEADLESS` | Headless browser | true/false |

### Example .env File

```bash
# Local LLM (Ollama)
OPENAI_COMPATIBLE_URL=http://localhost:11434/v1
OPENAI_COMPATIBLE_MODEL=qwen2.5:7b

# Flask
SECRET_KEY=your-secret-key-here
DEBUG=false

# Optional proxy
# PROXY_URL=socks5://host:port
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
python init_default_user.py
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
| LLM calls fail | LLM provider configuration |
| Pages don't load | Browser timeout, proxy settings |
| Proxy not working | Proxy URL format and reachability |
| Archives incomplete | Archive location permissions |

### Diagnostic Information

View system status:

1. Navigate to **Settings**
2. Check **System Status** section
3. Review connection status for all services

## Related Guides

- [Installation](../getting-started/installation.md) - Initial configuration
- [Proxy & Geo-IP](proxy-setup.md) - Proxy-specific settings
