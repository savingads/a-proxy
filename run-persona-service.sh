#!/bin/bash

# Run just the Persona Service API in a development environment without Docker

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check for required commands
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}python3 could not be found. Please install it first.${NC}"
    exit 1
fi

# Check if necessary directories exist
if [ ! -d "persona-service" ]; then
    echo -e "${RED}persona-service directory doesn't exist!${NC}"
    exit 1
fi

# Create Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo -e "${YELLOW}Creating Python virtual environment...${NC}"
  python3 -m venv venv
fi

# Set up Python environment
echo -e "${YELLOW}Setting up Persona Service Python environment...${NC}"
. venv/bin/activate
pip install -r persona-service/requirements.txt

# Additional dependencies
echo -e "${YELLOW}Installing additional dependencies...${NC}"
pip install flask-sqlalchemy flask-marshmallow marshmallow-sqlalchemy

# Start the Persona Service
echo -e "${YELLOW}Starting Persona Service API on port 5050...${NC}"
cd persona-service
python run.py --debug

echo -e "${GREEN}Done!${NC}"
