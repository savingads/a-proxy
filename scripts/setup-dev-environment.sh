#!/bin/bash

# A-Proxy Development Environment Setup Script
# This script sets up a local development environment for A-Proxy

echo "========================================="
echo "  A-Proxy Development Environment Setup  "
echo "========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Installing Python 3..."
    sudo apt-get update
    sudo apt-get install -y python3
fi

# Check if python3-venv is installed
python3 -m venv --help &> /dev/null
if [ $? -ne 0 ]; then
    echo "python3-venv is not installed. Installing python3-venv..."
    sudo apt-get update
    sudo apt-get install -y python3-venv
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "pip is not installed. Installing pip..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Installing Node.js and npm..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Check if npm is installed (should be installed with Node.js)
if ! command -v npm &> /dev/null; then
    echo "npm is not installed. Installing npm..."
    sudo apt-get install -y npm
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
if [ ! -d "venv" ]; then
    echo "Failed to create virtual environment. Please check your Python installation."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Now that the virtual environment is activated, install all dependencies
echo "Installing dependencies within the virtual environment..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install wheel

# Install development packages required for compiling extensions
echo "Installing system packages required for some Python dependencies..."
sudo apt-get update
sudo apt-get install -y build-essential python3-dev \
  libjpeg-dev libpng-dev libtiff-dev \
  libfreetype6-dev liblcms2-dev libwebp-dev \
  tcl8.6-dev tk8.6-dev python3-tk \
  libharfbuzz-dev libfribidi-dev libxcb1-dev

# Install Cython first (required for gevent)
echo "Installing Cython (required for gevent)..."
pip install Cython

# Install critical packages explicitly first
echo "Installing critical packages explicitly..."
pip install Pillow==9.4.0
pip install Flask==1.1.4 'Jinja2<3.0.0' 'MarkupSafe<2.1.0'

# Install requirements one by one to identify any problematic packages
echo "Installing remaining Python dependencies one by one..."
while IFS= read -r package || [[ -n "$package" ]]; do
    # Skip comments and empty lines
    [[ $package =~ ^#.* ]] || [[ -z "$package" ]] && continue
    
    # Skip packages we've already installed
    [[ $package == Pillow* ]] || [[ $package == Flask* ]] || [[ $package == Jinja2* ]] || [[ $package == MarkupSafe* ]] && continue
    
    echo "Installing $package..."
    pip install "$package" || {
        echo "Warning: Failed to install $package. Continuing with other packages..."
    }
done < requirements.txt

# Attempt to install gevent specifically with extra options
echo "Installing gevent with extra options..."
pip install --no-build-isolation gevent || {
    echo "Warning: Failed to install gevent with --no-build-isolation. Trying alternate method..."
    CFLAGS="-O0" pip install gevent || {
        echo "Warning: Failed to install gevent. Some functionality may not work correctly."
    }
}

# Double-check critical packages
echo "Verifying critical packages..."
pip install Pillow==9.4.0

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Create required directories
echo "Creating required directories..."
mkdir -p data nordvpn/ovpn_udp nordvpn/ovpn_tcp

# Check if auth.txt exists and create if needed
if [ ! -f nordvpn/auth.txt ]; then
    echo "Creating placeholder VPN credentials file..."
    echo "placeholder_username" > nordvpn/auth.txt
    echo "placeholder_password" >> nordvpn/auth.txt
    echo "NOTE: Replace the placeholders in nordvpn/auth.txt with real credentials for VPN functionality."
fi

# Initialize the database
echo "Initializing the database..."
python database.py

# Ask if sample personas should be created
read -p "Would you like to create sample personas? (y/n) " create_personas
if [[ $create_personas == "y" || $create_personas == "Y" ]]; then
    echo "Creating sample personas..."
    python create_sample_personas.py
fi

echo "========================================="
echo "  Setup Complete!  "
echo "========================================="
echo 
echo "To start the application, run:"
echo "source venv/bin/activate"
echo "python app.py"
echo
echo "The application will be available at: http://localhost:5002"
echo
echo "For more information, see SETUP_DEV_ENVIRONMENT.md"
