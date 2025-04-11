#!/bin/bash

# Run just the MCP client example in a development environment without Docker

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check for required commands
if ! command -v npm &> /dev/null; then
    echo -e "${RED}npm could not be found. Please install it first.${NC}"
    exit 1
fi

# Check if necessary directories exist
if [ ! -d "persona-mcp-server/examples" ]; then
    echo -e "${RED}persona-mcp-server/examples directory doesn't exist!${NC}"
    exit 1
fi

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
  echo -e "${YELLOW}Note: Make sure the Persona Service API is running at port 5050 first!${NC}"
  echo -e "${YELLOW}You can start it with ./run-persona-service.sh in another terminal.${NC}"
  echo
  npx ts-node mcp-client-example.ts
  RESULT=$?
  cd ../..
  return $RESULT
}

# Main execution
echo -e "${YELLOW}==== Running MCP Client Example ====${NC}"

setup_mcp_client
run_mcp_client

if [ $? -eq 0 ]; then
  echo -e "${GREEN}MCP client example executed successfully!${NC}"
else
  echo -e "${RED}MCP client example failed with error code $?.${NC}"
fi

echo -e "${GREEN}Done!${NC}"
