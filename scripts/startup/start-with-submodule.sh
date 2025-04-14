#!/bin/bash
# Start the a-proxy application using the persona-service from the Git submodule

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}==== Starting a-proxy with Submodule Persona Service ====${NC}"

# Check if submodule is initialized
if [ ! -f "persona-service-new/Dockerfile" ]; then
    echo -e "${RED}Persona service submodule not initialized properly.${NC}"
    echo -e "Run: ${GREEN}git submodule update --init --recursive${NC}"
    exit 1
fi

# Optional: Ensure Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker is not running or not accessible. Please start Docker first.${NC}"
    exit 1
fi

# Down any existing services to ensure clean start
echo -e "${YELLOW}Stopping any running services...${NC}"
docker-compose -f docker-compose-submodule.yml down

# Start the services
echo -e "${YELLOW}Starting services with the submodule persona service...${NC}"
docker-compose -f docker-compose-submodule.yml up -d

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 5

# Show running services
echo -e "${YELLOW}Services:${NC}"
docker-compose -f docker-compose-submodule.yml ps

echo -e "${GREEN}a-proxy is now running with the submodule persona service.${NC}"
echo -e "Access the application at: ${GREEN}http://localhost:5002${NC}"
echo -e "Persona service API at: ${GREEN}http://localhost:5050${NC}"
