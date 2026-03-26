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

For Docker (includes Ollama + Qwen 2.5 7B, no API keys needed): `docker-compose up --build`

Full installation details: [Installation Guide](https://savingads.github.io/a-proxy/getting-started/installation/)

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

Other options include cloud APIs (Anthropic Claude, OpenAI GPT) and HPC clusters via vLLM. See the **[LLM Setup Guide](https://savingads.github.io/a-proxy/how-to/llm-setup/)** for all providers, configuration details, and troubleshooting.

**Drexel Picotte users:** See the **[Picotte HPC Guide](https://savingads.github.io/a-proxy/how-to/picotte-vllm/)** for automated vLLM setup with `picotte_vllm.py`.

## Documentation

Full documentation is hosted at **<https://savingads.github.io/a-proxy/>** and built from the `docs/` directory using [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

To serve docs locally:

```bash
pip install mkdocs-material
mkdocs serve
```

Key sections:

| Section | What's covered |
|---------|---------------|
| [Installation](https://savingads.github.io/a-proxy/getting-started/installation/) | Docker and manual setup, environment variables, troubleshooting |
| [First Login](https://savingads.github.io/a-proxy/getting-started/first-login/) | Default credentials, interface overview, creating your first persona |
| [LLM Setup](https://savingads.github.io/a-proxy/how-to/llm-setup/) | Ollama, cloud APIs, HPC/vLLM configuration |
| [Picotte HPC](https://savingads.github.io/a-proxy/how-to/picotte-vllm/) | Drexel Picotte cluster setup and automation script |
| [Proxy & Geo-IP](https://savingads.github.io/a-proxy/how-to/proxy-setup/) | SOCKS5/HTTP proxy configuration for location emulation |
| [API Reference](https://savingads.github.io/a-proxy/reference/api-endpoints/) | REST API endpoints |
| [Architecture](https://savingads.github.io/a-proxy/reference/architecture/) | System design and database schema |

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
