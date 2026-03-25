# A-Proxy

A Flask-based web application for persona-driven web browsing, archiving, and LLM-powered conversations. Create personas with demographic, psychographic, behavioral, and contextual attributes, then browse the web as those personas with language, geolocation, timezone, and proxy emulation.

## Features

- **Persona Management** -- Create and manage personas with rich attribute profiles (demographic, psychographic, behavioral, contextual)
- **Persona-Driven Browsing** -- Visit websites with per-persona language, geolocation, timezone, and proxy settings via Playwright
- **Page Archiving** -- Save full HTML, screenshots, and metadata for visited pages
- **LLM Conversations** -- Chat with local models (Qwen, Llama, etc. via vLLM/Ollama) or cloud APIs (Claude, GPT) in persona context
- **Journey Tracking** -- Organize browsing sessions into journeys with waypoints
- **Geo-IP Shifting** -- Route traffic through SOCKS5/HTTP proxies for location emulation (no VPN required)
- **Cross-Platform** -- Runs natively on Windows, macOS, and Linux

## Quick Start

```bash
git clone https://github.com/savingads/a-proxy.git
cd a-proxy
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
python -m playwright install chromium

cp .env.example .env
# Edit .env -- configure an LLM provider (see below)

python app.py --port 5002
```

Open <http://localhost:5002> and log in with `admin@example.com` / `password`.

For Docker: `docker-compose up --build`

Full installation details: [Installation Guide](docs/getting-started/installation.md)

## LLM Setup

A-Proxy needs an LLM backend. The fastest option is [Ollama](https://ollama.com) (free, local, no API key):

```bash
ollama pull qwen2.5:7b
```

Then in `.env`:

```bash
LLM_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_URL=http://localhost:11434/v1
OPENAI_COMPATIBLE_MODEL=qwen2.5:7b
OPENAI_COMPATIBLE_API_KEY=none
```

Other options include cloud APIs (Anthropic Claude, OpenAI GPT) and HPC clusters via vLLM. See the **[LLM Setup Guide](docs/how-to/llm-setup.md)** for all providers, configuration details, and troubleshooting.

**Drexel Picotte users:** See the **[Picotte HPC Guide](docs/how-to/picotte-vllm.md)** for automated vLLM setup with `picotte_vllm.py`.

## Documentation

Full documentation is in the [`docs/`](docs/) directory and can be served locally with [MkDocs](https://www.mkdocs.org/):

```bash
pip install mkdocs-material
mkdocs serve
```

Key sections:

| Section | What's covered |
|---------|---------------|
| [Installation](docs/getting-started/installation.md) | Docker and manual setup, environment variables, troubleshooting |
| [First Login](docs/getting-started/first-login.md) | Default credentials, interface overview, creating your first persona |
| [LLM Setup](docs/how-to/llm-setup.md) | Ollama, cloud APIs, HPC/vLLM configuration |
| [Picotte HPC](docs/how-to/picotte-vllm.md) | Drexel Picotte cluster setup and automation script |
| [Proxy & Geo-IP](docs/how-to/proxy-setup.md) | SOCKS5/HTTP proxy configuration for location emulation |
| [API Reference](docs/reference/api-endpoints.md) | REST API endpoints |
| [Architecture](docs/reference/architecture.md) | System design and database schema |

## Project Structure

```
app.py                     # Flask app, blueprint registration
config.py                  # Configuration (API keys, regions, proxy)
picotte_vllm.py            # Picotte HPC vLLM management script
services.py                # Persona context management, token counting
database/                  # SQLite database layer (repository pattern)
routes/                    # Flask blueprints (browsing, persona, network, agent, etc.)
utils/
  browser.py               # Playwright BrowserManager (singleton, per-context isolation)
  network.py               # Proxy config, IP info
  agent.py                 # LLM agent service
  llm_client.py            # Multi-provider LLM client (local + cloud)
templates/                 # Jinja2 HTML templates
static/                    # CSS, JS (Bootstrap, Leaflet, agent chat)
demo/                      # Python Playwright demo scripts
tests/                     # Unit/integration tests
docs/                      # MkDocs documentation source
```

## Development

```bash
python -m pytest tests/                    # Run tests
python create_sample_personas_simple.py    # Create sample personas
python demo/demo_script.py                 # Browse and screenshot demo
```

## License

See [LICENSE](LICENSE) for details.
