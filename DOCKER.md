# Running A-Proxy in Docker

This guide will help you run A-Proxy in a Docker container, making it easier to deploy and isolate the application from your system.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed on your system
- [Docker Compose](https://docs.docker.com/compose/install/) installed on your system
- NordVPN credentials (if you want to use VPN features)

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/savingads/a-proxy
   cd a-proxy
   ```

2. Create required directories for persistent data:
   ```bash
   mkdir -p data nordvpn/ovpn_udp nordvpn/ovpn_tcp
   ```

3. Set up VPN configuration (if using VPN features):
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

## Building and Running

1. Build and start the container:
   ```bash
   docker-compose up -d
   ```

   This command will:
   - Build the Docker image using the Dockerfile
   - Start the container in detached mode
   - Mount the `./data` and `./nordvpn` directories as volumes

2. Access the application:
   Open your browser and navigate to:
   ```
   http://localhost:5002
   ```

3. Stop the container:
   ```bash
   docker-compose down
   ```

## Container Details

The Docker container:
- Uses Python 3.11-slim as the base image
- Installs all necessary dependencies (Chromium, OpenVPN, Node.js)
- Sets up the database in the `/app/data` directory for persistence
- Exposes port 5002 for web access
- Includes a health check to monitor the application status

## Troubleshooting

### Database Issues

If the database doesn't initialize properly or you encounter database-related errors:

1. Stop the container:
   ```bash
   docker-compose down
   ```

2. Remove the database file from the data directory:
   ```bash
   rm data/personas.db
   ```

3. Restart the container:
   ```bash
   docker-compose up -d
   ```

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
