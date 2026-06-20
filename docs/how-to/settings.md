# Settings

This guide documents the configuration options available in A-Proxy.

## Accessing Settings

The only in-app settings page is **Archive Settings**, reached via **Archive Settings** in the sidebar. It manages Internet Archive integration only.

!!! note
    A-Proxy does not have a general Settings UI. LLM provider, proxy, browser, and debug options are configured exclusively through environment variables / your `.env` file (see below), not through an in-app page.

## Archive Settings (in-app)

The Archive Settings page exposes the following options:

| Setting | Description | Default |
|---------|-------------|---------|
| Internet Archive Enabled | Toggle submitting captured pages to the Internet Archive | enabled |
| Internet Archive Rate Limit | Maximum submissions per day (clamped to 1-100) | 10 |

## Configuration (environment variables)

The categories below are configured via environment variables, not an in-app page.

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
| Headless Mode | Run browser without UI (env var `BROWSER_HEADLESS`) | true |

Other browser behavior is fixed in code rather than configurable: the page-load
timeout is hardcoded to 30 seconds (`utils/browser.py`), and the viewport is
derived from persona attributes rather than a global setting.

## Environment Variables

Most configuration (everything except the in-app Archive Settings) is set via environment variables:

| Variable | Setting | Example |
|----------|---------|---------|
| `OPENAI_COMPATIBLE_URL` | Local LLM endpoint | `http://localhost:11434/v1` |
| `OPENAI_COMPATIBLE_MODEL` | Local model name | `qwen2.5:7b` |
| `OPENAI_COMPATIBLE_API_KEY` | Local endpoint API key (vLLM default `none`) | `none` |
| `ANTHROPIC_API_KEY` | Claude API key | `sk-ant-...` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `LLM_PROVIDER` | Force provider | `openai_compatible` |
| `LLM_MAX_OUTPUT_TOKENS` | Max output tokens per LLM call | `4096` |
| `SECRET_KEY` | Flask session key | random-string |
| `SESSION_COOKIE_SECURE` | Send session cookie over HTTPS only | True/False |
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

The log level is currently hardcoded to `DEBUG` via `logging.basicConfig(level=logging.DEBUG)` in `app.py` and is not configurable via an environment variable.

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

1. Navigate to the **Dashboard**
2. Review the integration status (LLM, Internet Archive) and browser information shown there

## Related Guides

- [Installation](../getting-started/installation.md) - Initial configuration
- [Proxy & Geo-IP](proxy-setup.md) - Proxy-specific settings
