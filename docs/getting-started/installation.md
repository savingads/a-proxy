# Installation

A-Proxy can be installed using Docker (recommended) or through manual installation.

## Prerequisites

=== "Docker Installation"

    - [Docker](https://docs.docker.com/get-docker/) installed on your system
    - [Docker Compose](https://docs.docker.com/compose/install/) installed on your system
    - NordVPN credentials (optional, for VPN features)

=== "Manual Installation"

    - Python 3.8+ with pip
    - Node.js with npm
    - Git for version control
    - Chromium browser (for web archiving features)

## Docker Installation (Recommended)

Docker provides the easiest setup experience by handling all dependencies and environment configuration automatically.

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/savingads/a-proxy.git
   cd a-proxy
   ```

2. Run the helper script:
   ```bash
   ./start-a-proxy.sh
   ```

   This script will:

   - Check for Docker permissions and use sudo if needed
   - Create necessary directories
   - Set up placeholder VPN credentials if needed
   - Build and start the container
   - Provide status information

3. Access the application at `http://localhost:5002`

### Manual Docker Setup

If you prefer manual setup:

1. Create required directories:
   ```bash
   mkdir -p data nordvpn/ovpn_udp nordvpn/ovpn_tcp archives
   ```

2. Build and start the container:
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

3. Access the application at `http://localhost:5002`

4. Stop the container when done:
   ```bash
   docker-compose down
   ```

### VPN Configuration (Optional)

For VPN functionality:

1. Create a credentials file:
   ```bash
   echo "your_nordvpn_username" > nordvpn/auth.txt
   echo "your_nordvpn_password" >> nordvpn/auth.txt
   ```

2. Download OpenVPN configuration files from [NordVPN](https://nordvpn.com/ovpn/):
   - Place UDP files in `nordvpn/ovpn_udp/`
   - Place TCP files in `nordvpn/ovpn_tcp/`

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
   .\venv\Scripts\activate   # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   npm install
   ```

4. Set up environment:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your `ANTHROPIC_API_KEY` for Claude AI integration.

5. Initialize the database:
   ```bash
   mkdir -p data
   python database.py
   python create_sample_personas_simple.py  # Optional: Add sample data
   ```

6. Start the application:
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5002`

### Custom Port

If port 5002 is in use, specify a different port:

```bash
python app.py --port 5003
```

## Windows WSL Users

If using Docker with WSL:

1. Add your user to the docker group:
   ```bash
   sudo usermod -aG docker $USER
   ```

2. Log out and log back in, or run:
   ```bash
   newgrp docker
   ```

3. Verify Docker access:
   ```bash
   docker ps
   ```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | API key for Claude AI integration | Yes (for chat features) |
| `SECRET_KEY` | Flask session security key | Recommended |
| `DEBUG` | Enable debug mode | No (default: False) |

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
python database.py
```

### Missing Dependencies

Ensure your virtual environment is activated:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Next Steps

After installation, proceed to [First Login](first-login.md) to access the application.
