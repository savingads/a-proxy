# A-Proxy: How to Start the Application

## Prerequisites

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

## Starting the Application

The recommended way to start A-Proxy is:

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

## Custom Port Configuration

If port 5002 is already in use, you can specify a different port:

```bash
python app.py --port 5003
```

## Troubleshooting

If you encounter issues:

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
