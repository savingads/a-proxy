# Running A-Proxy in Docker

This guide will help you run A-Proxy in a Docker container, making it easier to deploy and isolate the application from your system.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed on your system
- [Docker Compose](https://docs.docker.com/compose/install/) installed on your system
- NordVPN credentials (if you want to use VPN features)

## Quickstart

We've provided a helper script to make setup easy:

```bash
./start-a-proxy.sh
```

This script will:
1. Check for Docker permissions and use sudo if needed
2. Create the necessary directories
3. Set up placeholder VPN credentials if needed
4. Build and start the container
5. Provide status information and helpful commands

Once the container is running, access the application at:
```
http://localhost:5002
```

## Manual Setup

If you prefer to set up manually instead of using the script:

1. Create required directories for persistent data:
   ```bash
   mkdir -p data nordvpn/ovpn_udp nordvpn/ovpn_tcp
   ```

2. Set up VPN configuration (if using VPN features):
   ```bash
   # Create auth.txt file with your NordVPN credentials
   echo "your_nordvpn_username" > nordvpn/auth.txt
   echo "your_nordvpn_password" >> nordvpn/auth.txt
   
   # Download OpenVPN configuration files from NordVPN
   # Visit: https://nordvpn.com/ovpn/
   # Download .ovpn files for the servers you want to use
   # Place UDP files in nordvpn/ovpn_udp/
   # Place TCP files in nordvpn/ovpn_tcp/
   ```

3. Build and start the container:
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

4. Access the application:
   ```
   http://localhost:5002
   ```

5. Stop the container:
   ```bash
   docker-compose down
   ```

## Windows WSL Users

If you're using Docker with WSL (Windows Subsystem for Linux), you might need to:

1. Add your user to the docker group:
   ```bash
   sudo usermod -aG docker $USER
   ```

2. Either log out and log back in, or run:
   ```bash
   newgrp docker
   ```

3. Verify that you can run docker commands:
   ```bash
   docker ps
   ```

If you still have permission issues, try running the commands with sudo.

## VPN Configuration

For VPN functionality to work properly:

1. Create a file with your NordVPN credentials:
   ```bash
   echo "your_nordvpn_username" > nordvpn/auth.txt
   echo "your_nordvpn_password" >> nordvpn/auth.txt
   ```

2. Download OpenVPN configuration files from [NordVPN's website](https://nordvpn.com/ovpn/):
   - Place UDP configuration files in `nordvpn/ovpn_udp/`
   - Place TCP configuration files in `nordvpn/ovpn_tcp/`

## Container Details

The Docker container:
- Uses Python 3.11-slim as the base image
- Installs all necessary dependencies (Chromium, OpenVPN, Node.js, build tools)
- Sets up the database in the `/app/data` directory for persistence
- Exposes port 5002 for web access
- Includes a health check to monitor the application status

## Troubleshooting

### Database Issues

If you encounter database-related errors:

1. Stop the container:
   ```bash
   docker-compose down
   ```

2. Remove the database files:
   ```bash
   rm -f data/personas.db persona-service/data/persona_service.db
   ```

3. Restart the container:
   ```bash
   docker-compose up -d
   ```

This will recreate both the main application database and the persona service database with fresh schemas.

### VPN Connection Issues

If you encounter issues with VPN connections:

1. Check that your `auth.txt` file contains valid NordVPN credentials.
2. Ensure you've downloaded valid OpenVPN configuration files to the `nordvpn/ovpn_udp/` or `nordvpn/ovpn_tcp/` directories.
3. Check Docker logs for connection errors:
   ```bash
   docker-compose logs
   ```

### Container Access Issues

If you can't access the application at http://localhost:5002:

1. Check if the container is running:
   ```bash
   docker-compose ps
   ```

2. Verify the port mapping:
   ```bash
   docker-compose port a-proxy 5002
   ```

3. Check container logs for errors:
   ```bash
   docker-compose logs
   ```

### Python Dependency Issues

If you encounter issues with Python dependency installation:

1. Check the build logs for specific error messages:
   ```bash
   docker-compose logs
   ```

2. If you see errors related to Python package building, the Dockerfile has been updated with necessary build dependencies, so running `docker-compose build --no-cache` should resolve these issues.

## Advanced Configuration

### Changing the Port

If you want to use a different port, modify the `docker-compose.yml` file:

```yaml
services:
  a-proxy:
    build: .
    ports:
      - "8080:5002"  # Change 8080 to your desired port
    volumes:
      - ./data:/app/data
      - ./nordvpn:/app/nordvpn
```

### Persistent Archives

The archives are stored in the container's file system. To make them persistent, add another volume mount to your `docker-compose.yml`:

```yaml
services:
  a-proxy:
    build: .
    ports:
      - "5002:5002"
    volumes:
      - ./data:/app/data
      - ./nordvpn:/app/nordvpn
      - ./archives:/app/archives
```

Then create the archives directory:
```bash
mkdir -p archives
```

## Security Considerations

- The OpenVPN configuration requires root access inside the container
- VPN credentials are stored in plain text in the `auth.txt` file
- Make sure to secure the `nordvpn` directory with appropriate permissions
