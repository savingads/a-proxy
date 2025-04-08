# Managing Multiple A-Proxy Development Environments

This guide provides instructions for setting up and managing multiple A-Proxy development environments without conflicts. This is useful if you need to maintain separate instances for different purposes (e.g., testing, feature development, or production-like environments).

## Overview

Each A-Proxy environment should have:
- Its own directory/clone of the repository
- A unique database file location
- A unique port number
- Separate VPN configuration (if using VPN features)

## Setting Up New Environments

### 1. Clone the Repository to a New Directory

```bash
# Create a new directory with a descriptive name
mkdir ~/a-proxy-feature-x

# Clone the repository into this directory
# If you're using git:
git clone https://your-repository-url.git ~/a-proxy-feature-x
# OR copy from an existing directory:
cp -r ~/a-proxy/* ~/a-proxy-feature-x/
```

### 2. Configure Database Location

Each environment should use a separate database file to avoid conflicts. Edit the `database.py` file to change the database path:

```python
# Original line:
DB_PATH = os.path.join('data', 'personas.db')

# Changed line (example):
DB_PATH = os.path.join('data', 'personas_feature_x.db')
```

### 3. Configure Different Port

To run multiple instances simultaneously, each must use a different port. When starting the application:

```bash
python app.py --port 5003  # Use a different port than the default 5002
```

You can also create a custom startup script for each environment:

```bash
#!/bin/bash
# start-feature-x.sh
cd ~/a-proxy-feature-x
source venv/bin/activate
python app.py --port 5003
```

### 4. Separate VPN Configuration (If Using VPN Features)

If you're using VPN features, create separate VPN credential files:

```bash
mkdir -p ~/a-proxy-feature-x/nordvpn/ovpn_udp ~/a-proxy-feature-x/nordvpn/ovpn_tcp
```

Create a separate auth.txt file with the appropriate credentials:

```bash
echo "your_nordvpn_username" > ~/a-proxy-feature-x/nordvpn/auth.txt
echo "your_nordvpn_password" >> ~/a-proxy-feature-x/nordvpn/auth.txt
```

## Practical Environment Separation Examples

### Development Environment (Default)

- Directory: `~/a-proxy`
- Database: `data/personas.db`
- Port: 5002
- Purpose: Main development work

### Feature Development Environment

- Directory: `~/a-proxy-feature-x`
- Database: `data/personas_feature_x.db`
- Port: 5003
- Purpose: Developing and testing a specific feature without affecting the main development environment

### Testing Environment

- Directory: `~/a-proxy-testing`
- Database: `data/personas_testing.db`
- Port: 5004
- Purpose: Running tests or experimenting with changes

## Environment Comparison Table

| Environment | Directory | Database | Port | Purpose |
|-------------|-----------|----------|------|---------|
| Main Dev | ~/a-proxy | personas.db | 5002 | Primary development |
| Feature X | ~/a-proxy-feature-x | personas_feature_x.db | 5003 | Feature development |
| Testing | ~/a-proxy-testing | personas_testing.db | 5004 | Testing and experiments |

## Managing Environment-Specific Settings

For more advanced control, you can use environment variables to manage configuration:

1. Create a `.env` file for each environment with specific settings
2. Modify `config.py` to read these variables:

```python
# Example modification to config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use environment variables with fallbacks
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
DB_PATH = os.environ.get('DB_PATH', os.path.join('data', 'personas.db'))
PORT = int(os.environ.get('PORT', 5002))
```

This approach requires adding `python-dotenv` to your requirements.txt file.

## Recommended Workflow

1. Make changes in a specific environment
2. Test thoroughly within that environment
3. If the changes are successful and should be applied across all environments:
   - Commit the changes to version control (if using Git)
   - Pull/merge the changes into other environments
   
Remember to document any database migrations or structural changes that might affect other environments.
