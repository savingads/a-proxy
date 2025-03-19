# A-Proxy: Web Testing with Geolocation and Language Simulation

A-Proxy is a tool that allows you to test websites with different geolocation and language settings by using VPN connections and a customized browser setup. This is useful for testing how websites behave for users in different countries and with different language preferences.

## Features

- Connect to VPN servers in different countries
- Simulate different browser language settings
- Override geolocation data in the browser
- Create and manage user personas with demographic, psychographic, behavioral, and contextual data
- Take screenshots of websites with the simulated settings
- Web interface for easy management
- Planned additions for archving webpages in WARC format
## Installation

### Prerequisites

- Linux-based system (Ubuntu/Debian recommended)
- Python 3.6+
- pip (Python package manager)
- sudo privileges for VPN setup

### Clone the Repository

```bash
git clone https://github.com/savingads/personas
cd a-proxy
```

### Install Python Dependencies

```bash
pip install -r requirements.txt
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
sudo apt update
sudo apt install -y google-chrome-stable

# Alternatively, install Chromium
# sudo apt install -y chromium-browser
```

After installation, verify that Chrome is installed at `/usr/bin/google-chrome`. If it's installed at a different location, update the `binary_location` in `selenium_proxy.py`.

### Install Selenium WebDriver Dependencies

```bash
pip install selenium webdriver-manager
```

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

### Using Your Own VPN Provider

If you want to use a different VPN provider:

1. Obtain the OpenVPN configuration files from your provider
2. Place them in a directory structure similar to `nordvpn/ovpn_udp/`
3. Update the VPN paths in `services.py` and `app.py` to point to your configuration files

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

1. From the web interface, select a region to connect to via VPN
2. Enter a URL to visit
3. Optionally, customize language and geolocation settings
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

## License

GPL-3.0 License

