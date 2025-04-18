# A-Proxy: Persona Proxy with Geolocation and Language Emulation

A-Proxy lets you view websites as if you were a user in different countries and languages, using VPN connections and a dynamic persona system. It is ideal for testing, research, and archiving web content with simulated user profiles.

---

## Table of Contents
- [A-Proxy: Persona Proxy with Geolocation and Language Emulation](#a-proxy-persona-proxy-with-geolocation-and-language-emulation)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Quickstart](#quickstart)
    - [Recommended: Docker](#recommended-docker)
  - [Manual Setup](#manual-setup)
  - [Troubleshooting](#troubleshooting)
  - [Development](#development)
  - [Architecture Overview](#architecture-overview)
  - [Documentation Index](#documentation-index)
  - [License](#license)

---

## Features
- Connect to VPN servers in different countries
- Simulate browser language and geolocation
- Create/manage personas (demographic, psychographic, behavioral, contextual)
- Archive webpages with metadata and screenshots
- Store multiple snapshots (mementos) of the same URL
- AI Assistant integration for journeys and waypoints
- Flexible persona management: API, mock, or direct DB

---

## Quickstart

### Recommended: Docker
1. Ensure [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) are installed.
2. (Optional) Prepare NordVPN credentials for VPN features.
3. Run:
   ```bash
   ./start-a-proxy.sh
   ```
4. Access the app at [http://localhost:5002](http://localhost:5002)

For advanced Docker usage, see [docs/DOCKER.md](docs/DOCKER.md).

---

## Manual Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   npm install
   ```
2. (Optional) Set up VPN:
   - Place NordVPN credentials in `nordvpn/auth.txt`
   - Download OpenVPN configs to `nordvpn/ovpn_udp/` and `nordvpn/ovpn_tcp/`
3. Initialize the database:
   ```bash
   python database.py
   python create_sample_personas.py  # Optional sample data
   ```
4. Start the app:
   ```bash
   python app.py
   # Or specify a port:
   python app.py --port 5003
   ```
5. Visit [http://localhost:5002](http://localhost:5002)

---

## Troubleshooting
- **Docker issues:** See [docs/DOCKER.md](docs/DOCKER.md) for troubleshooting, including database resets and VPN config.
- **Manual install issues:**
  - Check terminal output for errors
  - Ensure all dependencies are installed
  - For database issues, try:
    ```bash
    rm -f data/personas.db
    python database.py
    ```
- **VPN issues:**
  - Ensure valid credentials in `nordvpn/auth.txt`
  - Place correct OpenVPN files in the right folders
- **Port conflicts:** Use `--port` to specify a different port

---

## Development
- See [docs/README-DEV.md](docs/README-DEV.md) for local development, environment management, and advanced workflows.
- For WSL or multiple environments, see [docs/WSL_SETUP.md](docs/WSL_SETUP.md) and [docs/MULTIPLE_ENVIRONMENTS.md](docs/MULTIPLE_ENVIRONMENTS.md).
- To run the demo, see [demo/README.md](demo/README.md).

---

## Architecture Overview
- Persona management is available via API, mock, or direct DB (see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)).
- Persona API and schema are dynamic and configurable (see [docs/PERSONA_API.md](docs/PERSONA_API.md)).
- For integrations (Claude, agent modules, TypeScript), see [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md).

---

## Documentation Index
- [docs/README-DEV.md](docs/README-DEV.md): Developer setup and workflow
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): System and persona architecture
- [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md): Integrations and migration notes
- [docs/PERSONA_API.md](docs/PERSONA_API.md): API endpoints and usage
- [docs/HOW_TO_START.md](docs/HOW_TO_START.md): Getting started guide
- [docs/DOCKER.md](docs/DOCKER.md): Docker setup and troubleshooting
- [docs/IMPLEMENTATION_NOTES.md](docs/IMPLEMENTATION_NOTES.md): Implementation details
- [docs/WSL_SETUP.md](docs/WSL_SETUP.md): WSL-specific setup
- [docs/MULTIPLE_ENVIRONMENTS.md](docs/MULTIPLE_ENVIRONMENTS.md): Managing multiple environments
- [docs/COMMON_ERRORS.md](docs/COMMON_ERRORS.md): Common errors and solutions
- [docs/running-persona-with-typescript.md](docs/running-persona-with-typescript.md): TypeScript integration
- [demo/README.md](demo/README.md): Demo usage
- [persona-client/README.md](persona-client/README.md): Persona API client usage
- [persona-mcp-server/README.md](persona-mcp-server/README.md): MCP server usage

---

## License
GPL-3.0 License
