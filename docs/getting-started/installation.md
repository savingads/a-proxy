# Installation

A-Proxy can be installed using Docker or through manual installation.

## Prerequisites

=== "Docker Installation"

    - [Docker](https://docs.docker.com/get-docker/) installed on your system
    - [Docker Compose](https://docs.docker.com/compose/install/) installed on your system

=== "Manual Installation"

    - Python 3.10+ (3.12+ recommended)
    - Git for version control

## Docker Installation

Docker provides the easiest setup experience by handling all dependencies automatically.

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/savingads/a-proxy.git
   cd a-proxy
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and configure at least one LLM provider (see [LLM Configuration](#llm-configuration) below).

3. Build and start:
   ```bash
   docker-compose up --build
   ```

4. Access the application at `http://localhost:5002`

### Stop the Container

```bash
docker-compose down
```

## Manual Installation

### Setup Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/savingads/a-proxy.git
   cd a-proxy
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   python -m playwright install chromium
   ```

4. Set up environment:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and configure at least one LLM provider (see below).

5. Initialize the data directory:
   ```bash
   mkdir -p data
   python create_sample_personas_simple.py  # Optional: Add sample data
   python init_default_user.py              # Initialize default user
   ```

6. Start the application:
   ```bash
   python app.py --port 5002
   ```

The application will be available at `http://localhost:5002`

### Custom Port

If port 5002 is in use, specify a different port:

```bash
python app.py --port 5003
```

## LLM Configuration

A-Proxy supports three LLM provider types. Configure one or more in `.env`:

### Local / Self-Hosted (recommended for HPC)

Any OpenAI-compatible endpoint works -- vLLM, Ollama, text-generation-webui, LiteLLM, etc.

```bash
OPENAI_COMPATIBLE_URL=http://your-host:8000/v1
OPENAI_COMPATIBLE_MODEL=Qwen/Qwen2.5-72B-Instruct
OPENAI_COMPATIBLE_API_KEY=none
```

For quick local testing with [Ollama](https://ollama.com):

```bash
ollama serve
ollama pull qwen2.5:7b
```

Then set:
```bash
OPENAI_COMPATIBLE_URL=http://localhost:11434/v1
OPENAI_COMPATIBLE_MODEL=qwen2.5:7b
```

### Anthropic (Claude)

```bash
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
```

### OpenAI (GPT)

```bash
OPENAI_API_KEY=sk-YOUR_KEY_HERE
```

If multiple providers are configured, auto-detection priority is: local > Anthropic > OpenAI. Set `LLM_PROVIDER` to override.

## Proxy Configuration (Optional)

For geo-IP shifting, configure a SOCKS5 or HTTP proxy:

```bash
PROXY_URL=socks5://user:pass@host:port
```

The proxy can also be set per-session via the web UI. See [Proxy & Geo-IP](../how-to/proxy-setup.md) for details.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_COMPATIBLE_URL` | Local LLM endpoint URL | No |
| `OPENAI_COMPATIBLE_MODEL` | Model on local endpoint | No |
| `ANTHROPIC_API_KEY` | Claude API key | No |
| `OPENAI_API_KEY` | OpenAI API key | No |
| `LLM_PROVIDER` | Force provider selection | No |
| `SECRET_KEY` | Flask session security key | Recommended |
| `DEBUG` | Enable debug mode | No |
| `PROXY_URL` | Default proxy URL for geo-IP | No |
| `BROWSER_HEADLESS` | Run browser headless (default: True) | No |

## Troubleshooting

### Port Conflicts

Use the `--port` option to specify a different port:
```bash
python app.py --port 5003
```

### Database Issues

Remove the database and reinitialize:
```bash
rm -f data/personas.db
python init_default_user.py
```

### Missing Dependencies

Ensure your virtual environment is activated:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Playwright Browser Issues

If Playwright can't find Chromium:
```bash
python -m playwright install chromium
```

## Next Steps

After installation, proceed to [First Login](first-login.md) to access the application.
