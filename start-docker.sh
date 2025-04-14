#!/bin/bash

# Main startup script for running A-Proxy with Docker
# Starts the Persona Service, MCP server, and main application in Docker containers

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Repository root directory
ROOT_DIR=$(pwd)

# Check for required commands
check_command() {
  if ! command -v $1 &> /dev/null; then
    echo -e "${RED}$1 could not be found. Please install it first.${NC}"
    exit 1
  fi
}

check_command docker
check_command docker-compose

# Check if necessary directories exist
if [ ! -d "persona-service" ]; then
    echo -e "${RED}persona-service directory doesn't exist!${NC}"
    exit 1
fi

if [ ! -d "persona-mcp-server" ]; then
    echo -e "${RED}persona-mcp-server directory doesn't exist!${NC}"
    exit 1
fi

# Create JWT secret if it doesn't exist
JWT_SECRET_FILE=".jwt_secret"
if [ ! -f "$JWT_SECRET_FILE" ]; then
    echo -e "${YELLOW}Generating new JWT secret key...${NC}"
    openssl rand -hex 32 > "$JWT_SECRET_FILE"
    echo -e "${GREEN}JWT secret generated.${NC}"
fi

# Ensure data directories exist
mkdir -p "persona-service/data"
mkdir -p "data"

# Ensure the MCP server is built
if [ ! -d "persona-mcp-server/dist" ] || [ ! -f "persona-mcp-server/dist/index.js" ]; then
    echo -e "${YELLOW}Building MCP server...${NC}"
    cd persona-mcp-server
    npm install
    npm run build
    cd ..
    echo -e "${GREEN}MCP server built successfully.${NC}"
fi

# Function to clean up on exit
cleanup() {
    echo -e "${YELLOW}Cleaning up Docker containers...${NC}"
    docker-compose -f docker-compose-api.yml down
    echo -e "${GREEN}Done!${NC}"
}

# Set up trap to handle script termination
trap cleanup EXIT INT TERM

# Main execution
echo -e "${YELLOW}==== Setting up A-Proxy Docker Environment ====${NC}"

# Start the API stack
echo -e "${YELLOW}Starting API stack with Docker Compose...${NC}"
JWT_SECRET=$(cat "$JWT_SECRET_FILE")
export PERSONA_JWT_SECRET="$JWT_SECRET"

docker-compose -f docker-compose-api.yml up --build -d

echo -e "${GREEN}Docker containers started successfully!${NC}"
echo -e "${BLUE}Services are running:${NC}"
echo -e "  - Persona Service API: ${GREEN}http://localhost:5050${NC}"
echo -e "  - MCP Server: ${GREEN}Connected to Persona API${NC}"
echo -e "  - A-Proxy: ${GREEN}http://localhost:5002${NC}"

echo -e "\n${YELLOW}Press Ctrl+C to stop all containers and exit.${NC}"
echo -e "Or use: ${GREEN}docker-compose -f docker-compose-api.yml down${NC} to stop manually."

# Wait for input to keep the script running
read -p "Press Enter to stop all containers and exit..."
