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

3. Initialized the database:
   ```bash
   python database.py
   ```

4. (Optional) Added sample data:
   ```bash
   python create_sample_personas.py
   ```

## Starting the Application

The recommended way to start A-Proxy is:

```bash
python app.py --port 5001
```

This command:
- Launches the Flask web server on port 5001
- Enables debug mode for development
- Activates auto-reloading on code changes

You can then access the application by opening a web browser and navigating to:
```
http://localhost:5001
```

## Custom Port Configuration

If port 5001 is already in use, you can specify a different port:

```bash
python app.py --port 5002
```

## Troubleshooting

If you encounter issues:

1. Check terminal output for error messages
2. Verify VPN credentials if using VPN features
3. Ensure all prerequisites are properly installed
4. Check database connection by running `python database.py`

For database migration issues after updates:
```bash
python migrate_database.py
