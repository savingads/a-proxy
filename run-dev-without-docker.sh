#!/bin/bash

# Run the Persona Service and MCP client example in a dev environment without Docker

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to ensure we have venv installed
check_venv() {
  if ! python3 -c "import venv" &> /dev/null; then
    echo -e "${RED}Python venv module not found. Please install it first.${NC}"
    echo -e "On Ubuntu/Debian: ${GREEN}sudo apt-get install python3-venv${NC}"
    exit 1
  fi
}

# Check for required commands
check_command() {
  if ! command -v $1 &> /dev/null; then
    echo -e "${RED}$1 could not be found. Please install it first.${NC}"
    exit 1
  fi
}

check_command python3
check_command npm
# ts-node will be used from node_modules
check_venv

# Check if submodule is initialized
if [ ! -f "persona-service-new/Dockerfile" ]; then
    echo -e "${RED}Persona service submodule not initialized properly.${NC}"
    echo -e "Run: ${GREEN}git submodule update --init --recursive${NC}"
    exit 1
fi

# Create Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo -e "${YELLOW}Creating Python virtual environment...${NC}"
  python3 -m venv venv
fi

# Function to set up Python environment
setup_persona_service() {
  echo -e "${YELLOW}Setting up Persona Service Python environment...${NC}"
  . venv/bin/activate
  cd persona-service-new
  pip install -r requirements.txt
  cd ..
}

# Function to start the Persona Service
start_persona_service() {
  echo -e "${YELLOW}Starting Persona Service API on port 5050...${NC}"
  . venv/bin/activate
  cd persona-service-new
  python run.py --debug &
  PERSONA_PID=$!
  cd ..
  echo -e "${GREEN}Persona Service running with PID: ${PERSONA_PID}${NC}"
  sleep 3  # Give it a moment to start up
}

# Function to set up MCP client environment
setup_mcp_client() {
  echo -e "${YELLOW}Setting up MCP client environment...${NC}"
  cd persona-mcp-server/examples
  npm install
  cd ../..
}

# Function to run the MCP client example
run_mcp_client() {
  echo -e "${YELLOW}Running MCP client example...${NC}"
  cd persona-mcp-server/examples
  echo -e "${BLUE}===== MCP CLIENT OUTPUT =====${NC}"
  npx ts-node mcp-client-example.ts
  RESULT=$?
  cd ../..
  return $RESULT
}

# Function to clean up processes on exit
cleanup() {
  echo -e "${YELLOW}Cleaning up processes...${NC}"
  if [ ! -z "$PERSONA_PID" ]; then
    echo -e "Stopping Persona Service (PID: ${PERSONA_PID})..."
    kill $PERSONA_PID 2>/dev/null || true
  fi
  echo -e "${GREEN}Done!${NC}"
}

# Set up trap to handle script termination
trap cleanup EXIT INT TERM

# Main execution
echo -e "${YELLOW}==== Running Persona Service and MCP Client in Dev Mode ====${NC}"

setup_persona_service
setup_mcp_client
start_persona_service

echo -e "${YELLOW}Testing MCP client connection...${NC}"
if run_mcp_client; then
  echo -e "${GREEN}MCP client example executed successfully!${NC}"
else
  echo -e "${RED}MCP client example failed with error code $?.${NC}"
fi

echo -e "\n${YELLOW}Press Ctrl+C to stop the services and exit.${NC}"
# Keep script running to maintain the background services
wait $PERSONA_PID
