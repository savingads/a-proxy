# A-Proxy: A Persona Proxy with Geolocation and Language Emulation

A-Proxy is a tool that allows you to view websites with different geolocation and language settings by using VPN connections and a customized browser setup. This is useful for testing how websites behave for users in different countries and with different language preferences.

## Features

- Connect to VPN servers in different countries
- Simulate different browser language settings
- Override geolocation data in the browser
- Create and manage user personas with demographic, psychographic, behavioral, and contextual data
- Take screenshots of websites with the simulated settings
- Web interface for easy management
- Archive webpages with metadata and screenshots
- Store multiple mementos (snapshots) of the same URL over time

## Running with Docker (Recommended)

The easiest way to run A-Proxy is using Docker, which handles all dependencies and environment setup automatically.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed on your system
- [Docker Compose](https://docs.docker.com/compose/install/) installed on your system
- NordVPN credentials (optional, for VPN features)

### Quick Start

We've provided a helper script to make setup easy:

```bash
./start-a-proxy.sh
```

This script will:
1. Check for Docker permissions and use sudo if needed
2. Create the necessary directories
3. Set up placeholder VPN credentials if needed
4. Build and start the container
5. Provide status information and helpful commands

Once the container is running, access the application at:
```
http://localhost:5002
```

### Manual Docker Setup

If you prefer to set up manually:

1. Create required directories for persistent data:
   ```bash
   mkdir -p data nordvpn/ovpn_udp nordvpn/ovpn_tcp
   ```

2. Set up VPN configuration (if using VPN features):
   ```bash
   # Create auth.txt file with your NordVPN credentials
   echo "your_nordvpn_username" > nordvpn/auth.txt
   echo "your_nordvpn_password" >> nordvpn/auth.txt
   
   # Download OpenVPN configuration files from NordVPN
   # Visit: https://nordvpn.com/ovpn/
   # Download .ovpn files for the servers you want to use
   # Place UDP files in nordvpn/ovpn_udp/
   # Place TCP files in nordvpn/ovpn_tcp/
   ```

3. Build and start the container:
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

For more detailed Docker instructions, including troubleshooting and advanced configuration, see [DOCKER.md](DOCKER.md).

## Manual Installation (Alternative)

If you prefer not to use Docker, you can install and run A-Proxy directly on your system.

### Prerequisites

- Linux-based system (Ubuntu/Debian recommended)
- Python 3.6+
- pip (Python package manager)
- Node.js and npm (for frontend dependencies)
- sudo privileges for VPN setup

### Install Dependencies

```bash
# Install system dependencies
sudo apt update && sudo apt install -y openvpn chromium-browser

# Install Python and Node.js dependencies
pip install -r requirements.txt
npm install
```

### Set Up VPN (Optional)

Follow the VPN configuration steps as described in the Docker setup section above.

### Initialize Database

```bash
# For fresh installation
python database.py
python create_sample_personas.py  # Optional: Add sample data

# For existing installations (after updates)
python migrate_database.py
```

### Run the Application

```bash
python app.py
```

For more detailed instructions on manual setup, see [HOW_TO_START.md](HOW_TO_START.md).

## Available Regions

The application comes pre-configured with the following regions:

- United States (US)
- Brazil (BR)
- Germany (DE)
- Japan (JP)
- South Africa (ZA)

## Using the Archive Feature

The archive feature allows you to save snapshots of websites for future reference:

1. Enter a URL in the main interface
2. Click the "Archive" button instead of "Preview"
3. The page will be archived with its current state
4. Access your archived pages by clicking on "Archived Pages" in the sidebar
5. View details of an archived page by clicking "View Mementos"
6. Each archived URL can have multiple mementos (snapshots taken at different times)

## Development and Testing

A-Proxy includes a comprehensive test suite. For details on running and writing tests, see [tests/README.md](tests/README.md).

## Documentation

Detailed documentation for setting up and managing A-Proxy can be found in the `docs` directory:

- [SETUP_DEV_ENVIRONMENT.md](docs/SETUP_DEV_ENVIRONMENT.md) - Guide for setting up a local development environment
- [WSL_SETUP.md](docs/WSL_SETUP.md) - Specific instructions for Windows Subsystem for Linux users
- [MULTIPLE_ENVIRONMENTS.md](docs/MULTIPLE_ENVIRONMENTS.md) - Managing multiple development environments
- [CLAUDE.md](docs/CLAUDE.md) - Development progress and guidelines

## Development Scripts

A-Proxy includes scripts to help with development:

- `start-dev.sh` - Main script for launching the development server (in root directory)
- `scripts/setup-dev-environment.sh` - Script for setting up a complete development environment

For development guidelines, see [docs/CLAUDE.md](docs/CLAUDE.md).

## License

GPL-3.0 License
