#!/bin/bash

# Script to set up the development environment without Docker

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}==== Setting up Development Environment ====${NC}"

# Check if persona-service-backup exists
if [ ! -d "persona-service-backup" ]; then
    echo -e "${YELLOW}Creating persona-service-backup from persona-service-new...${NC}"
    mkdir -p persona-service-backup
    cp -r persona-service-new/* persona-service-backup/ 2>/dev/null || true
    cp -r persona-service-new/.env* persona-service-backup/ 2>/dev/null || true
fi

# Create persona-service directory
echo -e "${YELLOW}Creating persona-service directory...${NC}"
mkdir -p persona-service
if [ -d "persona-service-backup" ]; then
    cp -r persona-service-backup/* persona-service/ 2>/dev/null || true
    cp -r persona-service-backup/.env* persona-service/ 2>/dev/null || true
elif [ -d "persona-service-new" ]; then
    cp -r persona-service-new/* persona-service/ 2>/dev/null || true
    cp -r persona-service-new/.env* persona-service/ 2>/dev/null || true
else
    echo -e "${RED}No source directory found for persona-service!${NC}"
    exit 1
fi

# Create Python virtual environment
echo -e "${YELLOW}Creating Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
. venv/bin/activate
pip install -r persona-service/requirements.txt

# Fix run.py if it has syntax errors
RUNPY_FILE="persona-service/run.py"
if grep -q "default=" "$RUNPY_FILE"; then
    echo -e "${YELLOW}Fixing syntax errors in run.py...${NC}"
    sed -i 's/default=/default="/g' "$RUNPY_FILE"
    sed -i 's/, help=/, help="/g' "$RUNPY_FILE"
    sed -i 's/--debug"/--debug", /g' "$RUNPY_FILE"
    sed -i 's/host=args.host port/host=args.host, port/g' "$RUNPY_FILE"
    sed -i 's/port=args.port debug/port=args.port, debug/g' "$RUNPY_FILE"
fi

# Set up the MCP client environment
echo -e "${YELLOW}Setting up MCP client example...${NC}"
cd persona-mcp-server/examples
npm install
cd ../..

echo -e "${GREEN}===============================================${NC}"
echo -e "${GREEN}Development environment setup complete!${NC}"
echo -e "${GREEN}===============================================${NC}"
echo
echo -e "To run the environment:"
echo -e "1. Start the Persona Service API:"
echo -e "   ${GREEN}cd persona-service && python run.py --debug${NC}"
echo -e "2. In another terminal, run the MCP client example:"
echo -e "   ${GREEN}cd persona-mcp-server/examples && npx ts-node mcp-client-example.ts${NC}"
echo
echo -e "Or use the run-dev-without-docker-fixed.sh script to start everything at once."
