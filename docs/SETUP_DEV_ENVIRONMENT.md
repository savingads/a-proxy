# Setting Up A-Proxy Development Environment

This guide will help you set up a local development environment for A-Proxy without using Docker. This approach is ideal for active development.

## Prerequisites

Ensure you have the following installed:
- Python 3.8+ with pip
- Node.js with npm
- OpenVPN (only if you plan to use VPN features)

## Step 1: Create a Python Virtual Environment (Recommended)

Using a virtual environment keeps your dependencies isolated and prevents conflicts with other projects.

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

## Step 2: Install Python Dependencies

```bash
# Ensure your virtual environment is activated
pip install -r requirements.txt
```

## Step 3: Install Node.js Dependencies

```bash
npm install
```

## Step 4: Set Up VPN Configuration (Optional)

Skip this step if you don't need VPN functionality.

```bash
# Create directories for VPN configs
mkdir -p nordvpn/ovpn_udp nordvpn/ovpn_tcp

# Create auth.txt with your NordVPN credentials
echo "your_nordvpn_username" > nordvpn/auth.txt
echo "your_nordvpn_password" >> nordvpn/auth.txt

# Download OpenVPN configuration files from NordVPN
# Visit: https://nordvpn.com/ovpn/
# Place UDP files in nordvpn/ovpn_udp/
# Place TCP files in nordvpn/ovpn_tcp/
```

## Step 5: Initialize the Database

```bash
# Create the initial database
python database.py

# (Optional) Add sample personas
python create_sample_personas.py
```

## Step 6: Start the Application

```bash
# Ensure your virtual environment is activated
python app.py
```

This will start the application on http://localhost:5002 by default.

To specify a different port:
```bash
python app.py --port 5003
```

## Keeping Multiple Development Environments Separate

If you have multiple development environments, consider these tips to keep them separate:

1. **Use different ports** for each environment to avoid conflicts
2. **Create separate database files** by modifying `config.py` to specify different database paths
3. **Use Git branches** for different development purposes
4. **Document environment-specific settings** in a local README file

## Troubleshooting

### Database Issues

If you encounter database issues:
```bash
# Backup your current database (if needed)
cp personas.db personas.db.backup

# Run the database migration script
python migrate_database.py
```

### Python Dependency Issues

If you encounter issues with any Python packages:
```bash
# Upgrade pip and install wheel
pip install --upgrade pip
pip install wheel

# Install development packages required for building Python extensions
sudo apt-get update
sudo apt-get install -y build-essential python3-dev

# Install Cython (required for gevent)
pip install Cython

# For PIL/Pillow issues
pip install Pillow==9.4.0

# For issues with Flask and its dependencies
pip install Flask==1.1.4 'Jinja2<3.0.0' 'MarkupSafe<2.1.0'

# For gevent installation issues
pip install --no-build-isolation gevent
# If that fails, try:
CFLAGS="-O0" pip install gevent
```

If you continue to have issues, you can try installing packages one by one:
```bash
# Read requirements.txt line by line and install each package
while IFS= read -r package; do
    # Skip comments and empty lines
    [[ $package =~ ^#.* ]] || [[ -z "$package" ]] && continue
    echo "Installing $package..."
    pip install "$package" || echo "Failed to install $package"
done < requirements.txt
```

### Port Already in Use

If port 5002 is already in use:
```bash
# Try a different port
python app.py --port 5003
```

## Maintaining Environment Compatibility

When making changes, keep these guidelines in mind to ensure compatibility across environments:

1. Document any new dependencies immediately in requirements.txt or package.json
2. Use relative paths in your code
3. Test changes in isolation before merging into main branches
4. Use environment variables (via config.py) for environment-specific settings
