# A-Proxy: Web Testing with Geolocation and Language Simulation

A-Proxy is a tool that allows you to test websites with different geolocation and language settings by using VPN connections and a customized browser setup. This is useful for testing how websites behave for users in different countries and with different language preferences.

## Features

- Connect to VPN servers in different countries
- Simulate different browser language settings
- Override geolocation data in the browser
- Create and manage user personas with demographic, psychographic, behavioral, and contextual data
- Take screenshots of websites with the simulated settings
- Web interface for easy management
- Archive webpages with metadata and screenshots
- Store multiple mementos (snapshots) of the same URL over time
## Installation

### Prerequisites

- Linux-based system (Ubuntu/Debian recommended)
- Python 3.6+
- pip (Python package manager)
- Node.js and npm (for frontend dependencies)
- sudo privileges for VPN setup

### Clone the Repository

```bash
git clone https://github.com/savingads/a-proxy
cd a-proxy
```

### Install Python Dependencies

It is recommended to use a virtual environment to avoid conflicts with system-wide Python packages. To create and activate a virtual environment, run:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Install Node.js Dependencies

The application uses some JavaScript libraries for the frontend. Install them with:

```bash
npm install
```

### Install OpenVPN

OpenVPN is required to establish VPN connections to different regions:

```bash
sudo apt update && sudo apt install openvpn -y
```

### Install Google Chrome/Chromium

The application uses Chrome/Chromium for web testing. Install it with:

```bash
# For Ubuntu/Debian
sudo apt install -y chromium-browser
```

After installation, verify that Chrome is installed at `/usr/bin/google-chrome`. If it's installed at a different location, update the `binary_location` in `selenium_proxy.py`.

## VPN Configuration

### Using NordVPN (Included)

This project includes configuration files for NordVPN. However, **you need to provide your own NordVPN credentials**:

1. Create a file named `auth.txt` in the `nordvpn` directory
2. Add your NordVPN username on the first line
3. Add your NordVPN password on the second line

```bash
mkdir -p nordvpn
echo "your_nordvpn_username" > nordvpn/auth.txt
echo "your_nordvpn_password" >> nordvpn/auth.txt
```

4. Download the OpenVPN configuration files for NordVPN:
   - Visit the [NordVPN server tools page](https://nordvpn.com/ovpn/) and download the `.ovpn` files for the servers you want to use.
   - Choose between UDP or TCP configurations based on your preference:
     - **UDP**: Faster but less reliable
     - **TCP**: Slower but more reliable
   - Place the downloaded `.ovpn` files in the `nordvpn/ovpn_udp/` or `nordvpn/ovpn_tcp/` directories, depending on the protocol.

```bash
mkdir -p nordvpn/ovpn_udp nordvpn/ovpn_tcp
# Example: Move downloaded files to the appropriate directory
mv ~/Downloads/*.udp.ovpn nordvpn/ovpn_udp/
mv ~/Downloads/*.tcp.ovpn nordvpn/ovpn_tcp/
```

### Using Your Own VPN Provider

If you want to use a different VPN provider:

1. Obtain the OpenVPN configuration files from your provider
2. Place them in a directory structure similar to `nordvpn/ovpn_udp/`
3. Update the VPN paths in `services.py` and `app.py` to point to your configuration files

## Database Setup

### For Fresh Installation

The application will automatically create and initialize the database on first run, but you can also manually set up the database and add sample data:

```bash
# Initialize the database
python database.py

# (Optional) Add sample personas
python create_sample_personas.py
```

### For Existing Installations

If you're upgrading from a previous version, update your database schema:

```bash
python migrate_database.py
```

## Running the Application

Start the Flask web server:

```bash
python app.py --port 5001
```

Then open your browser and navigate to:

```
http://localhost:5001
```

## Usage

### Basic Usage

1. From the web interface choose to start the vpn or attempt to use the user profile in your current connection.
2. If you have not activated the VPN optionally, customize language and geolocation settings
2. Enter a URL to visit
4. Click "Visit Page" to open a Chrome browser with the specified settings
5. A screenshot will be saved to the project directory

### Creating Personas

You can create and save personas with specific demographic, psychographic, behavioral, and contextual data:

1. Navigate to the Personas tab
2. Fill in the persona details
3. Save the persona
4. Use the persona for testing by selecting it from the dropdown

## Available Regions

The application comes pre-configured with the following regions:

- United States (US)
- Brazil (BR)
- Germany (DE)
- Japan (JP)
- South Africa (ZA)

## Updating to the Latest Version

If you already have A-Proxy installed and want to update to the latest version with new features, follow these steps:

1. Pull the latest changes from the repository:
   ```bash
   cd a-proxy
   git pull origin main
   ```

2. Update Python dependencies (activate your virtual environment first if you're using one):
   ```bash
   pip install -r requirements.txt
   ```

3. Update Node.js dependencies for the frontend:
   ```bash
   npm install
   ```

4. Update the database schema to include new tables and fields:
   ```bash
   python migrate_database.py
   ```

5. Check for any new configuration requirements in the updated readme or by examining the code changes.

6. Restart the application:
   ```bash
   python app.py --port 5001
   ```

### Using the Archive Feature

The archive feature allows you to save snapshots of websites for future reference:

1. Enter a URL in the main interface
2. Click the "Archive" button instead of "Preview"
3. The page will be archived with its current state, including:
   - HTML content
   - Screenshot
   - HTTP headers and metadata
   - Association with the selected persona (if any)

4. Access your archived pages by clicking on "Archived Pages" in the sidebar
5. View details of an archived page by clicking "View Mementos"
6. Each archived URL can have multiple mementos (snapshots taken at different times)

## Troubleshooting

### VPN Connection Issues

- Ensure OpenVPN is installed correctly
- Verify your VPN credentials in the auth.txt file
- Check that the VPN configuration files exist in the expected location
- Run `sudo openvpn --config nordvpn/ovpn_udp/us123.nordvpn.com.udp.ovpn --auth-user-pass nordvpn/auth.txt` manually to test the connection

### Browser Issues

- Ensure Google Chrome or Chromium is installed
- Verify the browser path in `selenium_proxy.py` matches your installation
- Install the required Selenium dependencies with `pip install selenium webdriver-manager`

### Database and Upgrade Issues

- If you encounter database errors after upgrading, try:
  - Backing up your personas.db file (`cp personas.db personas.db.backup`)
  - Running the migration script again (`python migrate_database.py`)
  - If problems persist, consider initializing a fresh database (`python database.py`) after backing up your data
- For changes that don't appear after updating:
  - Clear your browser cache or use incognito/private mode
  - Restart the application completely
  - Check the console for JavaScript errors
- If you experience errors with the archive feature:
  - Ensure the 'archives' directory exists and is writable
  - Check that the required Python packages are installed

## License

GPL-3.0 License
