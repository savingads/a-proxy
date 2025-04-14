#!/bin/bash

# Script to start the Persona API service, A-Proxy, and MCP server together

set -e

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting A-Proxy Full Stack${NC}"
echo "=================================="

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}Note: Some operations may require sudo privileges.${NC}"
    echo "If Docker commands fail, try running this script with sudo."
    SUDO_CMD=""
else
    SUDO_CMD="sudo"
fi

# Create required directories
echo -e "${GREEN}Creating required directories...${NC}"
mkdir -p data persona-service/data nordvpn/ovpn_udp nordvpn/ovpn_tcp persona-mcp-server/dist

# Check if auth.txt exists and create a placeholder if it doesn't
if [ ! -f nordvpn/auth.txt ]; then
    echo -e "${YELLOW}NordVPN auth.txt not found. Creating placeholder...${NC}"
    echo -e "${YELLOW}Update credentials in nordvpn/auth.txt for VPN functionality.${NC}"
    echo "your_nordvpn_username" > nordvpn/auth.txt
    echo "your_nordvpn_password" >> nordvpn/auth.txt
    chmod 600 nordvpn/auth.txt
fi

# Generate a random JWT secret key if not set
if [ -z "$JWT_SECRET_KEY" ]; then
    export JWT_SECRET_KEY=$(openssl rand -hex 32)
    echo -e "${GREEN}Generated random JWT secret key.${NC}"
fi

# Check if MCP server is built
if [ ! -f persona-mcp-server/dist/index.js ]; then
    echo -e "${YELLOW}MCP server not built. Building now...${NC}"
    (cd persona-mcp-server && npm install && npm run build)
fi

# Build and start the containers
echo -e "${GREEN}Building and starting containers with Docker Compose...${NC}"
$SUDO_CMD docker-compose -f docker-compose-api.yml build
$SUDO_CMD docker-compose -f docker-compose-api.yml up -d

echo ""
echo -e "${GREEN}Stack started successfully!${NC}"
echo "=========================================="
echo "Persona API: http://localhost:5050"
echo "A-Proxy Web UI: http://localhost:5002"
echo "MCP Server: Running in container"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "View logs: docker-compose -f docker-compose-api.yml logs -f"
echo "Stop stack: docker-compose -f docker-compose-api.yml down"
echo "Restart stack: docker-compose -f docker-compose-api.yml restart"
echo ""
echo -e "${YELLOW}Note:${NC} The first time you start the stack, you may need to"
echo "migrate existing personas to the API with:"
echo "python migrate_to_api.py"
echo "=========================================="
