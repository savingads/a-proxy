# A-Proxy: A Persona Proxy with Geolocation and Language Emulation

A-Proxy is a tool that allows you to view websites with different geolocation and language settings by using VPN connections and a customized browser setup. This is useful for testing how websites behave for users in different countries and with different language preferences.

The system uses a flexible architecture with a dynamic persona schema that adapts to configuration, allowing reuse of persona profiles across multiple applications. The recommended approach is to use the full stack with both A-Proxy and the separate Persona API service.

## Features

- Connect to VPN servers in different countries
- Simulate different browser language settings
- Override geolocation data in the browser
- Create and manage user personas with demographic, psychographic, behavioral, and contextual data
- Take screenshots of websites with the simulated settings
- Web interface for easy management
- Archive webpages with metadata and screenshots
- Store multiple mementos (snapshots) of the same URL over time
- Multiple implementation options for persona management
- **AI Assistant Integration**: Interact with an AI agent during journeys and save conversations as waypoints

## Implementation Options

A-Proxy now offers three different ways to run the application:

### 1. Database Implementation (Simplest)

This approach uses your existing SQLite database directly, with no additional services needed:

```bash
python app_with_db.py
```

### 2. Mock Implementation (For Testing)

Uses an in-memory mock implementation - perfect for development and testing:

```bash
python app_with_mock.py
```

### 3. API-Based Implementation (For Multiple Applications)

Uses a separate API service for persona management:

```bash
# Start API service
cd persona-service
python run.py

# In another terminal
python app.py
```

### Unified Startup Scripts

For convenience, several startup scripts are provided:

#### Development Environment (Recommended)

The most reliable way to run the development environment is to use the enhanced `start-dev.sh` script:

```bash
# Run the complete stack (API + A-Proxy) for development environment
./start-dev.sh
```

This script:
- Creates necessary directories
- Creates and activates Python virtual environment
- Installs all required dependencies
- Properly initializes the database with dedicated scripts
- Automatically creates sample personas if none exist
- Starts the Persona Service with health checking
- Runs the A-Proxy application
- Provides detailed status information
- Automatically cleans up when stopped with Ctrl+C

The script is designed to be robust across different development environments and will work even on fresh installations.

#### Legacy Development Scripts

For backward compatibility, older scripts are still available:

```bash
# Alternative development script
./run_dev_stack.sh
```

#### Other Startup Options

```bash
# Database mode (default)
./start_a_proxy_all.py

# Mock mode
./start_a_proxy_all.py --implementation mock

# API mode
./start_a_proxy_all.py --implementation api
```

## Running the Complete Stack (Recommended)

The simplest way to run the complete A-Proxy with the Persona service is using the provided script:

```bash
./start-api-stack.sh
```

This script will:
- Create all necessary directories
- Generate a JWT secret key
- Build and start both A-Proxy and the Persona API service using Docker Compose
- Make the services available at:
  - Persona API: http://localhost:5050
  - A-Proxy Web UI: http://localhost:5002

If this is your first time running the stack, you'll need to migrate existing personas to the API:

```bash
python migrate_to_api.py
```

## Running with Docker

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

Choose one of the implementation options described above, such as:

```bash
python app_with_db.py
```

For more detailed instructions on manual setup, see [HOW_TO_START.md](HOW_TO_START.md).

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
- [PERSONA_ARCHITECTURE.md](PERSONA_ARCHITECTURE.md) - Detailed persona architecture documentation
- [PERSONA_API.md](PERSONA_API.md) - The Dynamic Persona API System
- [PERSONA_SCHEMA.md](docs/PERSONA_SCHEMA.md) - Details of the dynamic schema implementation

## Architecture

A-Proxy now supports multiple implementation options:

### 1. Database Implementation

Uses the existing SQLite database directly, without requiring any additional services:
- `utils/persona_client_db.py` - Client for database operations
- `routes/persona_api_db.py` - Routes for database implementation
- `app_with_db.py` - Main application using database implementation

### 2. Mock Implementation

Uses an in-memory implementation for testing:
- `utils/persona_client_mock.py` - Mock client implementation
- `routes/persona_api_mock.py` - Routes for mock implementation
- `app_with_mock.py` - Main application using mock implementation

### 3. API Service Implementation

Uses a standalone RESTful API for managing personas:
- `persona-service/` - API service implementation
- `persona-client/` - Python client library
- `utils/persona_client.py` - Client for API interactions
- `routes/persona_api.py` - Routes for API implementation
- `app.py` - Main application using API implementation

For detailed architecture documentation, see [PERSONA_ARCHITECTURE.md](PERSONA_ARCHITECTURE.md).

## License

GPL-3.0 License
