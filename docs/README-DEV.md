# A-Proxy Developer Guide

This guide covers all aspects of local development, environment setup, workflow, and troubleshooting for A-Proxy.

---

## Table of Contents
- [A-Proxy Developer Guide](#a-proxy-developer-guide)
  - [Table of Contents](#table-of-contents)
  - [Development Environment Setup](#development-environment-setup)
    - [Prerequisites](#prerequisites)
    - [1. Create a Python Virtual Environment](#1-create-a-python-virtual-environment)
    - [2. Install Dependencies](#2-install-dependencies)
    - [3. (Optional) VPN Setup](#3-optional-vpn-setup)
    - [4. Initialize the Database](#4-initialize-the-database)
    - [5. Start the Application](#5-start-the-application)
  - [Local Package Workflow](#local-package-workflow)
  - [Utility Scripts](#utility-scripts)
  - [Running and Debugging](#running-and-debugging)
  - [Managing Multiple Environments](#managing-multiple-environments)
  - [Troubleshooting](#troubleshooting)
  - [Best Practices](#best-practices)

---

## Development Environment Setup

### Prerequisites
- Python 3.8+ with pip
- Node.js with npm
- OpenVPN (if using VPN features)

### 1. Create a Python Virtual Environment
```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
npm install
```

### 3. (Optional) VPN Setup
```bash
mkdir -p nordvpn/ovpn_udp nordvpn/ovpn_tcp
# Add credentials
echo "your_nordvpn_username" > nordvpn/auth.txt
echo "your_nordvpn_password" >> nordvpn/auth.txt
# Download OpenVPN configs from https://nordvpn.com/ovpn/
```

### 4. Initialize the Database
```bash
python database.py
python create_sample_personas.py  # Optional sample data
```

### 5. Start the Application
```bash
python app.py
# Or specify a port:
python app.py --port 5003
```

---

## Local Package Workflow
- Local development uses `_src/agent_module/` and `_src/persona-service/` for immediate code changes.
- Avoids submodule sync issues and allows direct editing.
- Utility scripts for switching to local packages and fixing dependencies are in `scripts/utilities/`.

---

## Utility Scripts
- `scripts/utilities/switch-to-local-packages.sh`: Switch from submodules to local packages
- `scripts/utilities/fix-persona-service-dependencies.sh`: Fix persona-service dependencies
- `scripts/utilities/fix-create-personas.sh`: Force creation of sample personas

---

## Running and Debugging
- Use `start-with-packages.sh` for a full dev stack (persona-service + web app):
  ```bash
  ./start-with-packages.sh
  ```
- Logs from both services are shown in the terminal.
- Edit code in `_src/` for instant effect.
- Add personas via the UI or utility scripts.
- Databases:
  - Persona Service: `_src/persona-service/data/persona_service.db`
  - A-Proxy: `data/aproxy.db`

---

## Managing Multiple Environments
- Use different ports for each environment to avoid conflicts.
- Create separate database files by editing `config.py`.
- Use Git branches for different features.
- Document environment-specific settings in a local README.

---

## Troubleshooting
- **Database issues:**
  ```bash
  cp personas.db personas.db.backup
  python migrate_database.py
  ```
- **Python dependency issues:**
  - Upgrade pip and wheel:
    ```bash
    pip install --upgrade pip
    pip install wheel
    ```
  - Install build tools:
    ```bash
    sudo apt-get update
    sudo apt-get install -y build-essential python3-dev
    ```
  - For gevent:
    ```bash
    pip install Cython
    pip install --no-build-isolation gevent
    # Or:
    CFLAGS="-O0" pip install gevent
    ```
  - For Pillow:
    ```bash
    pip install Pillow==9.4.0
    ```
  - For Flask:
    ```bash
    pip install Flask==1.1.4 'Jinja2<3.0.0' 'MarkupSafe<2.1.0'
    ```
- **Port already in use:**
  ```bash
  python app.py --port 5003
  ```
- **Install packages one by one:**
  ```bash
  while IFS= read -r package; do
      [[ $package =~ ^#.* ]] || [[ -z "$package" ]] && continue
      pip install "$package" || echo "Failed to install $package"
  done < requirements.txt
  ```

---

## Best Practices
- Document new dependencies in requirements.txt or package.json
- Use relative paths in code
- Test changes in isolation before merging
- Use environment variables for environment-specific settings

---

For WSL-specific or advanced environment management, see [WSL_SETUP.md](./WSL_SETUP.md) and [MULTIPLE_ENVIRONMENTS.md](./MULTIPLE_ENVIRONMENTS.md).
