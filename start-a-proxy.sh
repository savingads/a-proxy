#!/bin/bash

# Script to build and run A-Proxy in Docker

echo "=== A-Proxy Docker Setup ==="
echo

# Check if docker group is in effect
if ! groups | grep -q "\bdocker\b"; then
  echo "Docker group not active in current session."
  echo "This script will use sudo for Docker commands."
  DOCKER_CMD="sudo docker"
  DOCKER_COMPOSE_CMD="sudo docker-compose"
else
  DOCKER_CMD="docker"
  DOCKER_COMPOSE_CMD="docker-compose"
fi

# Make sure directories exist
echo "Ensuring required directories exist..."
mkdir -p data nordvpn/ovpn_udp nordvpn/ovpn_tcp

# Check if auth.txt exists
if [ ! -f nordvpn/auth.txt ]; then
  echo "Creating placeholder NordVPN credentials file..."
  echo "placeholder_username" > nordvpn/auth.txt
  echo "placeholder_password" >> nordvpn/auth.txt
  echo "NOTE: Replace the placeholders in nordvpn/auth.txt with real credentials for VPN functionality."
fi

# Start the build
echo "Building and starting Docker container..."
$DOCKER_COMPOSE_CMD down
$DOCKER_COMPOSE_CMD build --no-cache
$DOCKER_COMPOSE_CMD up -d

# Check if container is running
if $DOCKER_CMD ps | grep -q a-proxy; then
  echo
  echo "=== Success! ==="
  echo "A-Proxy is now running at http://localhost:5002"
  echo
  echo "To view logs:"
  echo "  $DOCKER_COMPOSE_CMD logs -f"
  echo
  echo "To stop the container:"
  echo "  $DOCKER_COMPOSE_CMD down"
else
  echo
  echo "=== Error ==="
  echo "Container failed to start. Check the logs for more details:"
  echo "  $DOCKER_COMPOSE_CMD logs"
fi
