# A-Proxy: How to Start the Application

There are two main ways to run A-Proxy: using Docker (recommended) or manual installation.

## Option 1: Using Docker (Recommended)

Docker provides the easiest setup experience by handling all dependencies and environment configuration automatically.

### Quick Start with Docker

1. Run the provided helper script:
   ```bash
   ./start-a-proxy.sh
   ```

2. Access the application in your browser:
   ```
   http://localhost:5002
   ```

That's it! The script handles everything else, including setting up directories, placeholders for VPN credentials, and building and starting the container.

For detailed Docker instructions, advanced configuration options, and troubleshooting, see [DOCKER.md](DOCKER.md).

## Option 2: Manual Installation

If you prefer not to use Docker, follow these steps for manual installation.

### Prerequisites

Before starting A-Proxy, ensure you have:

1. Installed all required dependencies:
   ```bash
   pip install -r requirements.txt
   npm install
   ```

2. Set up VPN configuration (if using VPN features):
   - Created `nordvpn/auth.txt` with your NordVPN credentials
   - Downloaded OpenVPN configuration files to `nordvpn/ovpn_udp/` or `nordvpn/ovpn_tcp/`

3. Set up the database:
   
   For a fresh installation:
   ```bash
   python database.py  # Initialize the database
   python create_sample_personas.py  # Optional: Add sample data
   ```
   
   For existing installations (after updates):
   ```bash
   python migrate_database.py  # Update database schema to latest version
   ```

### Starting the Application Manually

The recommended way to start A-Proxy manually is:

```bash
python app.py
```

This command:
- Launches the Flask web server on port 5002 (default)
- Enables debug mode for development
- Activates auto-reloading on code changes

You can then access the application by opening a web browser and navigating to:
```
http://localhost:5002
```

### Custom Port Configuration

If port 5002 is already in use, you can specify a different port:

```bash
python app.py --port 5003
```

## Troubleshooting

### Docker Issues

See [DOCKER.md](DOCKER.md) for Docker-specific troubleshooting.

### Manual Installation Issues

If you encounter issues with manual installation:

1. Check terminal output for error messages
2. Verify VPN credentials if using VPN features
3. Ensure all prerequisites are properly installed
4. Check database connection by running `python database.py`

For database migration issues:
1. Check the migration output for specific error messages
2. Ensure you have the latest version with `git pull origin main`
3. Try backing up your database before migration:
   ```bash
   cp personas.db personas.db.backup
   python migrate_database.py
   ```
4. The migrate script will show the current database version and report success or failure
