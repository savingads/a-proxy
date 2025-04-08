# Setting Up A-Proxy in WSL

This guide provides specific instructions for setting up A-Proxy in Windows Subsystem for Linux (WSL). These steps are tailored to ensure a smooth setup process in the WSL environment.

## Prerequisites

Ensure your WSL instance has the following:

- WSL with a compatible Linux distribution (Ubuntu recommended)
- Python 3.8+
- Node.js and npm
- Git (if you plan to use version control)

## Setup Process

### Option 1: Automated Setup (Recommended)

1. Make the setup script executable:
   ```bash
   chmod +x setup-dev-environment.sh
   ```

2. Run the setup script:
   ```bash
   ./setup-dev-environment.sh
   ```

   This script will:
   - Install any missing dependencies (Python, pip, Node.js, npm)
   - Create a Python virtual environment
   - Install all required Python and Node.js packages
   - Set up required directories and configuration files
   - Initialize the database
   - Offer to create sample personas

3. Start the application:
   ```bash
   ./start-dev.sh
   ```

   Or, to specify a custom port:
   ```bash
   ./start-dev.sh 5003
   ```

### Option 2: Manual Setup

If you prefer to set up manually, follow the detailed instructions in [SETUP_DEV_ENVIRONMENT.md](SETUP_DEV_ENVIRONMENT.md).

## WSL-Specific Considerations

### File Permissions

If you encounter permission issues, ensure your files have the correct permissions:

```bash
# Make scripts executable
chmod +x *.sh

# Fix permissions for directories if needed
chmod -R 755 data nordvpn
```

### Accessing the Application

When the application is running in WSL, you can access it from your Windows host using:

- **WSL 1**: `http://localhost:5002`
- **WSL 2**: By default, use `http://localhost:5002`. If that doesn't work, you may need to use the WSL instance's IP address, which you can find with `ip addr show eth0`.

### Browser Integration

For features that require browser interaction, you can:
- Use a browser inside WSL (like a headless Chrome)
- Use Windows browsers by properly configuring the WSL network

### Node.js in WSL

If you encounter Node.js issues in WSL:

1. Use the recommended installation method in our setup script
2. Alternatively, install Node.js using NVM:
   ```bash
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
   nvm install node
   ```

## Running Multiple Environments in WSL

For managing multiple development environments within WSL, see [MULTIPLE_ENVIRONMENTS.md](MULTIPLE_ENVIRONMENTS.md).

## Troubleshooting WSL-Specific Issues

### Network Connection Issues

If you have trouble connecting to external services:

1. Check your WSL network configuration:
   ```bash
   cat /etc/resolv.conf
   ```

2. Ensure Windows firewall isn't blocking connections

### Python Virtual Environment Issues

If you encounter issues with the Python virtual environment:

1. Try reinstalling venv:
   ```bash
   sudo apt-get update
   sudo apt-get install python3-venv
   ```

2. Create the virtual environment manually:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

### Dependency Installation Issues

If you encounter errors related to building Python packages:

1. Install required build dependencies for Pillow/PIL and other packages:
   ```bash
   sudo apt-get update
   sudo apt-get install -y build-essential python3-dev \
     libjpeg-dev libpng-dev libtiff-dev \
     libfreetype6-dev liblcms2-dev libwebp-dev \
     tcl8.6-dev tk8.6-dev python3-tk \
     libharfbuzz-dev libfribidi-dev libxcb1-dev
   ```

2. For gevent issues, install Cython first:
   ```bash
   pip install Cython
   ```

3. Try alternative installation methods for problematic packages:
   ```bash
   # For Pillow, make sure the JPEG libraries are installed
   pip install --no-build-isolation Pillow==9.4.0
   
   # For gevent specifically
   pip install --no-build-isolation gevent
   
   # Or with flags to disable optimizations
   CFLAGS="-O0" pip install gevent
   ```

4. You can try installing packages one by one to identify issues:
   ```bash
   while IFS= read -r package; do 
       [[ $package =~ ^#.* ]] || [[ -z "$package" ]] && continue
       pip install "$package" || echo "Failed to install $package"
   done < requirements.txt
   ```

### WSL File System Performance

For better performance, keep your project files within the WSL file system (e.g., `/home/username/`) rather than on Windows-mounted drives (e.g., `/mnt/c/`).
