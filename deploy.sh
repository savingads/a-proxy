#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}====== A-Proxy Production Deployment Script ======${NC}"
echo -e "${BLUE}This script will deploy A-Proxy to /var/www/a-proxy${NC}"
echo ""

# Function to print section headers
section() {
  echo -e "\n${YELLOW}==== $1 ====${NC}"
}

# Function to backup a file with timestamp
backup_file() {
  if [ -f "$1" ]; then
    local backup="$1.bak-$(date +%Y%m%d-%H%M%S)"
    echo -e "${YELLOW}Backing up $1 to $backup${NC}"
    cp "$1" "$backup"
  fi
}

# Function to check if command executed successfully
check_success() {
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}Success!${NC}"
  else
    echo -e "${RED}Failed!${NC}"
    exit 1
  fi
}

# Function to prompt for confirmation
confirm() {
  read -p "$1 (y/n): " answer
  case ${answer:0:1} in
    y|Y )
      return 0
    ;;
    * )
      return 1
    ;;
  esac
}

# Check if running as root or with sudo
if [ $EUID -ne 0 ]; then
  echo -e "${YELLOW}This script should be run with sudo privileges.${NC}"
  if confirm "Continue anyway?"; then
    echo "Continuing without sudo..."
  else
    echo "Please run with sudo. Exiting..."
    exit 1
  fi
fi

# Phase 1: Check existing environment
section "Checking Existing Environment"

echo "Checking directory structure..."
if [ -d "/var/www/a-proxy" ]; then
  echo -e "${YELLOW}Directory /var/www/a-proxy already exists${NC}"
  ls -la /var/www/a-proxy
else
  echo -e "${YELLOW}Directory /var/www/a-proxy does not exist and will be created${NC}"
fi

echo "Checking for existing systemd services..."
if systemctl list-unit-files | grep -q a-proxy.service; then
  echo -e "${YELLOW}a-proxy.service already exists${NC}"
  systemctl status a-proxy.service || true
else
  echo -e "${YELLOW}a-proxy.service does not exist and will be created${NC}"
fi

if systemctl list-unit-files | grep -q persona-service.service; then
  echo -e "${YELLOW}persona-service.service already exists${NC}"
  systemctl status persona-service.service || true
else
  echo -e "${YELLOW}persona-service.service does not exist and will be created${NC}"
fi

echo "Checking for existing Nginx configuration..."
if [ -f "/etc/nginx/sites-available/a-proxy" ]; then
  echo -e "${YELLOW}Nginx config /etc/nginx/sites-available/a-proxy already exists${NC}"
  cat /etc/nginx/sites-available/a-proxy
else
  echo -e "${YELLOW}Nginx config does not exist and will be created${NC}"
fi

echo "Checking for running processes..."
ps aux | grep -E 'python|gunicorn' | grep -v grep || echo "No matching processes found"

# Phase 2: Prepare environment
section "Preparing Production Environment"

# Create directory structure if it doesn't exist
if [ ! -d "/var/www/a-proxy" ]; then
  echo "Creating /var/www/a-proxy directory..."
  mkdir -p /var/www/a-proxy
  check_success
else
  # Backup existing deployment
  timestamp=$(date +%Y%m%d-%H%M%S)
  echo "Creating backup of existing deployment..."
  mkdir -p /var/www/backups
  if [ -d "/var/www/a-proxy/app" ]; then
    cp -r /var/www/a-proxy /var/www/backups/a-proxy-$timestamp
    check_success
  fi
fi

# Create necessary subdirectories
echo "Creating necessary subdirectories..."
mkdir -p /var/www/a-proxy/{app,data,logs,venv}
check_success

# Set ownership
echo "Setting directory ownership..."
chown -R chris:chris /var/www/a-proxy
check_success

# Phase 3: Deploy application code
section "Deploying Application Code"

# Clone or update repository
if [ ! -d "/var/www/a-proxy/app/.git" ]; then
  echo "Cloning repository..."
  cd /var/www/a-proxy
  rm -rf app # Remove directory if it exists but isn't a git repo
  git clone https://github.com/savingads/a-proxy.git app
  check_success
  cd app
  git checkout main
  check_success
else
  echo "Updating repository..."
  cd /var/www/a-proxy/app
  git fetch
  git checkout main
  git pull
  check_success
fi

# Setup virtual environment
echo "Setting up Python virtual environment..."
cd /var/www/a-proxy
if [ ! -d "venv/bin" ]; then
  python3 -m venv venv
  check_success
fi

echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r app/requirements.txt
pip install gunicorn gevent
check_success

# Setup environment file
echo "Setting up environment file..."
cd /var/www/a-proxy
if [ -f ".env" ]; then
  backup_file ".env"
else
  cp app/.env.example .env
  # Update with production values
  sed -i 's/DEBUG=True/DEBUG=False/' .env
  echo "SECRET_KEY=$(openssl rand -hex 24)" >> .env
  echo "Please update the ANTHROPIC_API_KEY in .env"
  check_success
fi

# Phase 4: Configure Services
section "Configuring Services"

# Gunicorn configuration
echo "Setting up Gunicorn configuration..."
cd /var/www/a-proxy
if [ -f "gunicorn_config.py" ]; then
  backup_file "gunicorn_config.py"
fi

cat > gunicorn_config.py << EOL
bind = "unix:/var/www/a-proxy/a-proxy.sock"
workers = 4
worker_class = "gevent"
timeout = 120
accesslog = "/var/www/a-proxy/logs/access.log"
errorlog = "/var/www/a-proxy/logs/error.log"
loglevel = "info"
EOL
check_success

# Systemd service files
echo "Setting up systemd service files..."

# a-proxy.service
if [ -f "/etc/systemd/system/a-proxy.service" ]; then
  backup_file "/etc/systemd/system/a-proxy.service"
fi

cat > /etc/systemd/system/a-proxy.service << EOL
[Unit]
Description=A-Proxy Web Application
After=network.target persona-service.service
Requires=persona-service.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/a-proxy/app
Environment="PATH=/var/www/a-proxy/venv/bin"
EnvironmentFile=/var/www/a-proxy/.env
ExecStart=/var/www/a-proxy/venv/bin/gunicorn --config /var/www/a-proxy/gunicorn_config.py "app:create_app()"
Restart=always

[Install]
WantedBy=multi-user.target
EOL
check_success

# persona-service.service
if [ -f "/etc/systemd/system/persona-service.service" ]; then
  backup_file "/etc/systemd/system/persona-service.service"
fi

cat > /etc/systemd/system/persona-service.service << EOL
[Unit]
Description=A-Proxy Persona Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/a-proxy/app/_src/persona-service
Environment="PATH=/var/www/a-proxy/venv/bin"
EnvironmentFile=/var/www/a-proxy/.env
ExecStart=/var/www/a-proxy/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL
check_success

# Nginx configuration
echo "Setting up Nginx configuration..."
if [ -f "/etc/nginx/sites-available/a-proxy" ]; then
  backup_file "/etc/nginx/sites-available/a-proxy"
fi

cat > /etc/nginx/sites-available/a-proxy << EOL
server {
    listen 80;
    server_name 209.38.62.85;

    access_log /var/log/nginx/a-proxy-access.log;
    error_log /var/log/nginx/a-proxy-error.log;

    location / {
        proxy_pass http://unix:/var/www/a-proxy/a-proxy.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias /var/www/a-proxy/app/static;
    }
}
EOL
check_success

# Create symbolic link if it doesn't exist
if [ ! -f "/etc/nginx/sites-enabled/a-proxy" ]; then
  ln -s /etc/nginx/sites-available/a-proxy /etc/nginx/sites-enabled/
  check_success
fi

# Remove default site if it exists
if [ -f "/etc/nginx/sites-enabled/default" ]; then
  rm /etc/nginx/sites-enabled/default
fi

# Phase 5: Database Setup
section "Setting Up Database"

# Create data directory
echo "Setting up database directories..."
mkdir -p /var/www/a-proxy/data
check_success

# Backup existing database if it exists
if [ -f "/var/www/a-proxy/data/aproxy.db" ]; then
  backup_file "/var/www/a-proxy/data/aproxy.db"
fi

if [ -f "/var/www/a-proxy/data/persona_service.db" ]; then
  backup_file "/var/www/a-proxy/data/persona_service.db"
fi

# Initialize databases
echo "Initializing A-Proxy database..."
cd /var/www/a-proxy/app
source ../venv/bin/activate
python database.py
check_success

echo "Initializing Persona Service database..."
cd /var/www/a-proxy/app/_src/persona-service
source ../../../venv/bin/activate
python init_db.py
check_success

# Phase 6: Set Permissions
section "Setting Permissions"

echo "Setting file and directory permissions..."
chown -R www-data:www-data /var/www/a-proxy
chmod -R 755 /var/www/a-proxy
chmod 600 /var/www/a-proxy/.env

# Make sure log directory is writable
mkdir -p /var/www/a-proxy/logs
chown -R www-data:www-data /var/www/a-proxy/logs
chmod -R 755 /var/www/a-proxy/logs
check_success

# Phase 7: Start Services
section "Starting Services"

echo "Reloading systemd daemon..."
systemctl daemon-reload
check_success

echo "Testing Nginx configuration..."
nginx -t
check_success

echo "Restarting services..."
systemctl restart persona-service
systemctl restart a-proxy
systemctl restart nginx
check_success

echo "Enabling services to start at boot..."
systemctl enable persona-service
systemctl enable a-proxy
check_success

# Phase 8: Verify Deployment
section "Verifying Deployment"

echo "Checking service status..."
systemctl status persona-service --no-pager
systemctl status a-proxy --no-pager
systemctl status nginx --no-pager

echo "Checking logs for errors..."
echo "Last 10 lines of persona-service log:"
journalctl -u persona-service -n 10 --no-pager

echo "Last 10 lines of a-proxy log:"
journalctl -u a-proxy -n 10 --no-pager

# Phase 9: Documentation
section "Creating Deployment Documentation"

echo "Creating deployment documentation..."
cat > /var/www/a-proxy/DEPLOYMENT.md << EOL
# A-Proxy Production Deployment

Deployed on: $(date)
Git Commit: $(cd /var/www/a-proxy/app && git rev-parse HEAD)
Branch: main

## Configuration Files
- Nginx: /etc/nginx/sites-available/a-proxy
- Services: 
  - /etc/systemd/system/a-proxy.service
  - /etc/systemd/system/persona-service.service
- Gunicorn: /var/www/a-proxy/gunicorn_config.py
- Environment: /var/www/a-proxy/.env

## Database Files
- A-Proxy: /var/www/a-proxy/data/aproxy.db
- Persona Service: /var/www/a-proxy/data/persona_service.db

## Backup Files
- All configuration files are backed up with .bak-YYYYMMDD-HHMMSS extension
- Database backups: /var/www/a-proxy/data/*.bak-YYYYMMDD-HHMMSS

## Maintenance Commands
- Check logs:
  \`\`\`
  sudo journalctl -u a-proxy
  sudo journalctl -u persona-service
  \`\`\`
- Restart services:
  \`\`\`
  sudo systemctl restart a-proxy persona-service nginx
  \`\`\`
- Update application:
  \`\`\`
  cd /var/www/a-proxy/app
  sudo git pull
  sudo systemctl restart a-proxy persona-service
  \`\`\`

## Rollback Procedure
1. Stop services:
   \`\`\`
   sudo systemctl stop a-proxy persona-service
   \`\`\`
2. Restore configuration files from backups
3. Restore database files from backups
4. Restart services:
   \`\`\`
   sudo systemctl start persona-service a-proxy nginx
   \`\`\`
EOL
check_success

echo -e "${GREEN}====== Deployment Complete! ======${NC}"
echo -e "${BLUE}A-Proxy should now be available at: http://209.38.62.85${NC}"
echo -e "${BLUE}Please check the logs for any errors and test the application.${NC}"
echo -e "${BLUE}Deployment documentation: /var/www/a-proxy/DEPLOYMENT.md${NC}"
