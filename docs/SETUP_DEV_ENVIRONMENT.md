# A-Proxy Development Environment Setup

This guide provides detailed instructions for setting up a development environment for A-Proxy. Follow these steps to get your environment ready for development work.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** with pip
- **Node.js** with npm
- **Git** for version control
- **OpenVPN** (optional, for VPN features)

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/a-proxy.git
cd a-proxy
```

### 2. Create and Activate a Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip wheel
pip install -r requirements.txt
```

If you encounter issues with certain packages:

```bash
# Install packages one at a time
while IFS= read -r package; do
    [[ $package =~ ^#.* ]] || [[ -z "$package" ]] && continue
    pip install "$package" || echo "Failed to install $package"
done < requirements.txt
```

### 4. Install Node.js Dependencies

```bash
npm install
```

### 5. Set Up Data Directories

```bash
# Create data directories
mkdir -p data
```

### 6. (Optional) Set Up VPN Configuration

For testing VPN features:

```bash
# Create VPN directories
mkdir -p nordvpn/ovpn_udp nordvpn/ovpn_tcp

# Add your NordVPN credentials
echo "your_nordvpn_username" > nordvpn/auth.txt
echo "your_nordvpn_password" >> nordvpn/auth.txt

# Download OpenVPN configurations from NordVPN website
# Place in the appropriate directory:
# - UDP configs in nordvpn/ovpn_udp/
# - TCP configs in nordvpn/ovpn_tcp/
```

### 7. Initialize the Database

```bash
python database.py
```

### 8. (Optional) Add Sample Data

```bash
# Create sample personas
python create_sample_personas.py
```

### 9. Set Up Local Packages

A-Proxy now uses a local package approach for dependencies. Set them up with:

```bash
# Ensure the _src directory exists and has the required components
mkdir -p _src

# Make sure agent_module is cloned properly (personas branch)
cd _src
git clone -b personas https://github.com/cr625/agent_module.git

# Make sure persona-service is cloned properly (develop branch)
git clone -b develop https://github.com/yourusername/persona-service.git
cd ..

# Install as local packages
pip install -e _src/agent_module
```

## Starting the Application

### Option 1: Using the Start Script (Recommended)

```bash
./start.sh
```

This script:
- Checks the status of all repository components
- Offers to synchronize changes if needed
- Sets up proper environment
- Starts both the persona service and main application

### Option 2: Manual Startup

Start the Persona Service:

```bash
cd _src/persona-service
python run.py
```

In a new terminal, start the main application:

```bash
python app.py
```

Access the application at [http://localhost:5002](http://localhost:5002)

## Common Issues and Solutions

### Python Dependency Problems

If you encounter issues with dependency installation:

```bash
# Install build dependencies on Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y build-essential python3-dev

# For Pillow issues
sudo apt-get install -y libjpeg-dev libpng-dev libtiff-dev libfreetype6-dev liblcms2-dev libwebp-dev

# For gevent issues
pip install Cython
pip install --no-build-isolation gevent
```

### Database Issues

If you encounter database problems:

```bash
# Remove and reinitialize the database
rm -f data/personas.db
python database.py
python create_sample_personas.py  # Optional

# For persona service database
rm -f _src/persona-service/data/persona_service.db
cd _src/persona-service
python init_db.py
```

### Port Conflicts

If port 5002 or 5050 is already in use:

```bash
# Change the port for the main application
python app.py --port 5003

# Change the port for the persona service
# Edit _src/persona-service/config.py and change the PORT variable
```

## Local Package Development

When working with the local package structure:

1. Make changes in `_src/agent_module` or `_src/persona-service`
2. The changes take effect immediately without needing to reinstall the package
3. For database changes, you might need to restart the respective service

## Next Steps

- Read the [Architecture Overview](../ARCHITECTURE.md)
- Study the [API documentation](PERSONA_API.md)
- Learn about [Docker deployment](DOCKER.md)
- Check the [WSL-specific setup](WSL_SETUP.md) if using Windows

For advanced usage with multiple environments, see [Managing Multiple Environments](MULTIPLE_ENVIRONMENTS.md).
