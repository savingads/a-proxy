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

Docker provides the easiest setup experience. The default `docker-compose.yml` bundles an Ollama service with Qwen 2.5 7B, so no API keys or external LLM setup is required.

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/savingads/a-proxy.git
   cd a-proxy
   ```

2. Build and start (includes Ollama + Qwen 2.5 7B):
   ```bash
   docker-compose up --build
   ```

   On first run, Ollama will download the Qwen model (~4.7 GB). A-Proxy waits for the model to be ready before starting.

3. Access the application at `http://localhost:5002`

   Default login: `admin@example.com` / `password`

!!! note "GPU Support"
    Ollama automatically uses GPU acceleration if available. For NVIDIA GPUs, ensure [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) is installed. CPU-only inference works but is slower.

### Using a Different LLM Provider

To use a cloud API or external endpoint instead of the bundled Ollama, create a `.env` file:

```bash
cp .env.example .env
```

Then set your preferred provider. See [LLM Configuration](#llm-configuration) below.

### Using Drexel Picotte HPC

Picotte provides access to larger models (e.g., Qwen 2.5 72B) but requires:

- Drexel VPN (Cisco AnyConnect) connected
- An active vLLM SLURM job on the cluster
- SSH tunnel forwarding the vLLM port to localhost

If you have a tunnel running (`ssh -L 8000:<gpu-node>:8000 picotte -N`), set in `.env`:

```bash
OPENAI_COMPATIBLE_URL=http://host.docker.internal:8000/v1
OPENAI_COMPATIBLE_MODEL=Qwen/Qwen2.5-72B-Instruct
```

The `host.docker.internal` hostname lets the container reach services on the host machine. See the [Picotte HPC Guide](../how-to/picotte-vllm.md) for full setup instructions.

### Stop the Containers

```bash
docker-compose down
```

To also remove the downloaded model data:

```bash
docker-compose down -v
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
   python init_default_user.py              # Creates the admin@example.com login account
   python create_sample_personas_simple.py  # Optional: populates a few demo personas
   ```
   The default user is created automatically on first startup, but running `init_default_user.py` explicitly ensures it exists. Sample personas are optional — you can create your own from the web UI.

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

A-Proxy requires at least one LLM provider. The quickest option is [Ollama](https://ollama.com) (free, local, no API key):

```bash
ollama pull qwen2.5:7b
```

Then set in `.env`:

```bash
LLM_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_URL=http://localhost:11434/v1
OPENAI_COMPATIBLE_MODEL=qwen2.5:7b
OPENAI_COMPATIBLE_API_KEY=none
```

For all LLM options (cloud APIs, HPC clusters, model recommendations, troubleshooting), see the **[LLM Setup Guide](../how-to/llm-setup.md)**.

For Drexel Picotte HPC users, see the **[Picotte HPC Guide](../how-to/picotte-vllm.md)**.

## Proxy Configuration (Optional)

For geo-IP shifting, configure a SOCKS5 or HTTP proxy in `.env`:

```bash
PROXY_URL=socks5://user:pass@host:port
```

The proxy can also be set per-session via the web UI. See [Proxy & Geo-IP](../how-to/proxy-setup.md) for details.

## Environment Variables

If multiple providers are configured, auto-detection priority is: **local (OpenAI-compatible) > Anthropic > OpenAI**. Set `LLM_PROVIDER` explicitly to override. All environment variables and their defaults are documented in the [LLM Setup Guide](../how-to/llm-setup.md). The key ones for installation:

| Variable | Description | Required |
|----------|-------------|----------|
| `LLM_PROVIDER` | Force provider selection (`openai_compatible`, `anthropic`, `openai`) | No (auto-detected) |
| `OPENAI_COMPATIBLE_URL` | Local LLM endpoint URL | Yes, if using local models |
| `OPENAI_COMPATIBLE_MODEL` | Model name on local endpoint | Yes, if using local models |
| `SECRET_KEY` | Flask session security key | Recommended for production |
| `PROXY_URL` | Default proxy URL for geo-IP | No |

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

1. [First Login](first-login.md) — log in and explore the interface
2. [LLM Setup](../how-to/llm-setup.md) — configure an LLM backend for the Agent chat feature
3. [Create Personas](../how-to/create-personas.md) — start building personas
