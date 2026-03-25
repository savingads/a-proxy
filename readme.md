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

## Prerequisites

- Python 3.10+ (3.12+ recommended)
- [Playwright](https://playwright.dev/python/) Chromium browser
- An LLM endpoint: local (vLLM, Ollama) or cloud API key (Anthropic, OpenAI)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/savingads/a-proxy.git
cd a-proxy

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
python -m playwright install chromium

# Configure environment
cp .env.example .env
# Edit .env -- see "LLM Configuration" below

# Initialize data directory
mkdir -p data

# Start the application
python app.py --port 5002
```

Open <http://localhost:5002> and log in with `admin@example.com` / `password`.

## Docker

```bash
docker-compose up --build
```

The app will be available at <http://localhost:5002>.

## Configuration

### LLM Configuration

The fastest way to get started is with [Ollama](https://ollama.com) (free, local, no API key needed):

```bash
# Install Ollama (see ollama.com for your platform)
ollama pull qwen2.5:7b
```

Then set in `.env`:

```bash
OPENAI_COMPATIBLE_URL=http://localhost:11434/v1
OPENAI_COMPATIBLE_MODEL=qwen2.5:7b
OPENAI_COMPATIBLE_API_KEY=none
```

A-Proxy also supports **Anthropic (Claude)** and **OpenAI (GPT)** via API keys, as well as **vLLM on HPC clusters** for larger models. See the full [LLM Setup Guide](docs/how-to/llm-setup.md) for all options, including HPC/SLURM instructions.

If multiple providers are configured, auto-detection priority is: local > Anthropic > OpenAI. Set `LLM_PROVIDER` to override (values: `openai_compatible`, `anthropic`, `openai`).

### All Environment Variables

| Variable | Description | Default |
| -------- | ----------- | ------- |
| `OPENAI_COMPATIBLE_URL` | Local LLM endpoint URL | -- |
| `OPENAI_COMPATIBLE_MODEL` | Model name on local endpoint | `Qwen/Qwen2.5-72B-Instruct` |
| `OPENAI_COMPATIBLE_API_KEY` | API key for local endpoint | `none` |
| `ANTHROPIC_API_KEY` | Anthropic (Claude) API key | -- |
| `ANTHROPIC_MODEL` | Claude model name | `claude-sonnet-4-20250514` |
| `OPENAI_API_KEY` | OpenAI API key | -- |
| `OPENAI_MODEL` | GPT model name | `gpt-4o-mini` |
| `LLM_PROVIDER` | Force provider selection | auto-detect |
| `LLM_MAX_OUTPUT_TOKENS` | Max response tokens | `4096` |
| `SECRET_KEY` | Flask session secret key | dev default |
| `DEBUG` | Enable debug mode | `False` |
| `PROXY_URL` | Default proxy URL (e.g. `socks5://host:port`) | -- |
| `BROWSER_HEADLESS` | Run browser headless | `True` |

### Proxy Setup

A-Proxy supports optional SOCKS5/HTTP proxies for geo-IP shifting. No VPN software is required.

- Set `PROXY_URL` in `.env` for a default proxy, or
- Configure per-session via the proxy controls in the web UI

The proxy is applied per browser context through Playwright, so each persona session can use a different proxy.

## Project Structure

```
app.py                     # Flask app, blueprint registration
config.py                  # Configuration (API keys, regions, proxy)
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
```

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Sample Data

```bash
python create_sample_personas_simple.py   # Create sample personas
python init_default_user.py               # Initialize default user
```

### Demo Scripts

```bash
python demo/demo_script.py            # Browse and screenshot demo
python demo/create_pdf_report.py      # PDF report generation demo
```

## Tech Stack

- **Backend**: Python, Flask, SQLite
- **Browser Automation**: Playwright (sync API) with per-context geolocation, locale, timezone, and proxy emulation
- **LLM Integration**: OpenAI-compatible endpoints (vLLM, Ollama), Anthropic (Claude), OpenAI (GPT)
- **Frontend**: Jinja2, Bootstrap, Leaflet.js, vanilla JS
- **Deployment**: Docker / docker-compose or local Python venv

## License

See [LICENSE](LICENSE) for details.
