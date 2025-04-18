# A-Proxy Production Deployment Guide

This document outlines the process for deploying the A-Proxy application to a production environment on a Digital Ocean Droplet. It provides step-by-step instructions for merging code, setting up the production environment, and configuring the necessary services.

## Overview

The deployment process consists of two main stages:

1. **Code Merge**: Merging the `developer` branch into `main` to prepare for production deployment
2. **Production Deployment**: Setting up the application on the production server with Nginx and Gunicorn

## Prerequisites

- SSH access to the Digital Ocean Droplet (IP: 209.38.62.85)
- Git access to the repository
- Sudo privileges on the production server

## Deployment Scripts

We've created two scripts to automate the deployment process:

1. **`merge-to-main.sh`**: Handles the process of merging the `developer` branch into `main`
2. **`deploy.sh`**: Handles the deployment of the application to the production server

## Step 1: Merge Developer Branch to Main

The first step is to merge the `developer` branch into `main`. This can be done locally or in the development environment.

```bash
# Make the script executable if needed
chmod +x merge-to-main.sh

# Run the merge script
./merge-to-main.sh
```

The script will:
- Check for uncommitted changes
- Ensure you're on the developer branch
- Pull the latest changes
- Create a tag of the developer branch as a backup
- Checkout and update the main branch
- Merge developer into main
- Push the changes to origin (with confirmation)

## Step 2: Deploy to Production

Once the code is merged to main, you can deploy to the production server:

### Option 1: Run Directly on Production Server

1. Transfer the deployment script to the production server:
   ```bash
   scp deploy.sh chris@209.38.62.85:~/
   ```

2. SSH into the production server:
   ```bash
   ssh chris@209.38.62.85
   ```

3. Make the script executable and run it with sudo:
   ```bash
   chmod +x deploy.sh
   sudo ./deploy.sh
   ```

### Option 2: Deploy Using Temporary SSH Key from Development Environment

If you're using a GitHub Codespace or another development environment:

1. Generate a temporary SSH key:
   ```bash
   ssh-keygen -t ed25519 -f ~/.ssh/do_temp_key -C "temporary-codespace-key"
   ```

2. Display the public key:
   ```bash
   cat ~/.ssh/do_temp_key.pub
   ```

3. Add this key to authorized_keys on the production server (from your local machine):
   ```bash
   ssh chris@209.38.62.85 "mkdir -p ~/.ssh && echo 'YOUR_PUBLIC_KEY' >> ~/.ssh/authorized_keys"
   ```

4. SCP the deployment script to the server:
   ```bash
   scp -i ~/.ssh/do_temp_key deploy.sh chris@209.38.62.85:~/
   ```

5. Execute the deployment script:
   ```bash
   ssh -i ~/.ssh/do_temp_key chris@209.38.62.85 "chmod +x ~/deploy.sh && sudo ~/deploy.sh"
   ```

6. Remove the temporary key after deployment:
   ```bash
   ssh chris@209.38.62.85 "sed -i '/temporary-codespace-key/d' ~/.ssh/authorized_keys"
   ```

## What the Deployment Script Does

The `deploy.sh` script performs the following operations:

1. **Environment Check**:
   - Checks for existing directories, services, and configurations
   - Creates backups of existing setup

2. **Directory Setup**:
   - Creates the `/var/www/a-proxy` directory structure
   - Sets up subdirectories for app, data, logs, and venv

3. **Code Deployment**:
   - Clones or updates the repository from main branch
   - Sets up the Python virtual environment
   - Installs dependencies

4. **Configuration**:
   - Sets up environment variables and configuration files
   - Configures Gunicorn
   - Creates systemd service files
   - Sets up Nginx as a reverse proxy

5. **Database Setup**:
   - Backs up and initializes databases

6. **Permissions & Services**:
   - Sets appropriate permissions
   - Reloads configurations and starts services
   - Enables services to start at boot

7. **Verification**:
   - Checks service status and logs
   - Creates deployment documentation

## Verifying the Deployment

After the deployment script completes, verify that the application is running:

1. Check the service status:
   ```bash
   sudo systemctl status persona-service
   sudo systemctl status a-proxy
   sudo systemctl status nginx
   ```

2. Check for errors in the logs:
   ```bash
   sudo journalctl -u persona-service -n 50
   sudo journalctl -u a-proxy -n 50
   ```

3. Access the application in a browser:
   - http://209.38.62.85

## Rollback Procedure

If there are issues with the deployment, follow these steps to roll back:

1. Stop the services:
   ```bash
   sudo systemctl stop a-proxy persona-service
   ```

2. Restore configuration files from backups:
   ```bash
   # Example
   sudo cp /etc/systemd/system/a-proxy.service.bak-YYYYMMDD-HHMMSS /etc/systemd/system/a-proxy.service
   ```

3. Restore database files if needed:
   ```bash
   cp /var/www/a-proxy/data/aproxy.db.bak-YYYYMMDD-HHMMSS /var/www/a-proxy/data/aproxy.db
   ```

4. Checkout the previous version in git:
   ```bash
   cd /var/www/a-proxy/app
   git checkout [previous-tag-or-commit]
   ```

5. Restart the services:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start persona-service a-proxy nginx
   ```

## Maintenance and Updates

For future updates to the application:

1. Merge new changes to the main branch using the merge script
2. On the production server:
   ```bash
   cd /var/www/a-proxy/app
   sudo git pull
   sudo systemctl restart a-proxy persona-service
   ```

For more extensive updates, re-run the deployment script.
