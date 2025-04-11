#!/bin/bash

# Run A-Proxy with Persona Service API in a dev environment without Docker or MCP
# This script runs both the Persona Service API and the main A-Proxy application

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check for required commands
check_command() {
  if ! command -v $1 &> /dev/null; then
    echo -e "${RED}$1 could not be found. Please install it first.${NC}"
    exit 1
  fi
}

check_command python3

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

# Function to create required directories
create_directories() {
  echo -e "${YELLOW}Creating required directories...${NC}"
  mkdir -p persona-service/data
  mkdir -p persona-service/instance
  
  # Ensure permissions are correct
  chmod -R 755 persona-service/data
  chmod -R 755 persona-service/instance
}

# Function to set up Python environment
setup_python_env() {
  echo -e "${YELLOW}Setting up Python environment...${NC}"
  . venv/bin/activate
  
  # Install persona-service requirements
  cd persona-service
  pip install -r requirements.txt
  
  # Install some additional dependencies that might be needed
  pip install flask-sqlalchemy flask-marshmallow marshmallow-sqlalchemy
  cd ..
  
  # Install main app requirements
  pip install -r requirements.txt
}

# Function to start the Persona Service
start_persona_service() {
  echo -e "${YELLOW}Starting Persona Service API on port 5050...${NC}"
  . venv/bin/activate
  cd persona-service
  python run.py --debug &
  PERSONA_PID=$!
  cd ..
  echo -e "${GREEN}Persona Service running with PID: ${PERSONA_PID}${NC}"
  sleep 3  # Give it a moment to start up
}

# Function to start the main A-Proxy application
start_a_proxy() {
  echo -e "${YELLOW}Starting A-Proxy application on port 5002...${NC}"
  . venv/bin/activate
  python app.py --port 5002 --host 127.0.0.1 &
  APROXY_PID=$!
  echo -e "${GREEN}A-Proxy running with PID: ${APROXY_PID}${NC}"
}

# Function to clean up processes on exit
cleanup() {
  echo -e "${YELLOW}Cleaning up processes...${NC}"
  if [ ! -z "$PERSONA_PID" ]; then
    echo -e "Stopping Persona Service (PID: ${PERSONA_PID})..."
    kill $PERSONA_PID 2>/dev/null || true
  fi
  
  if [ ! -z "$APROXY_PID" ]; then
    echo -e "Stopping A-Proxy (PID: ${APROXY_PID})..."
    kill $APROXY_PID 2>/dev/null || true
  fi
  
  echo -e "${GREEN}Done!${NC}"
}

# Set up trap to handle script termination
trap cleanup EXIT INT TERM

# Main execution
echo -e "${YELLOW}==== Running A-Proxy with Persona Service API in Dev Mode ====${NC}"

# Create directories and setup environment
create_directories
setup_python_env

# Start services
start_persona_service
start_a_proxy

echo -e "${BLUE}Services are running:${NC}"
echo -e "  - Persona Service API: ${GREEN}http://localhost:5050${NC}"
echo -e "  - A-Proxy: ${GREEN}http://localhost:5002${NC}"

echo -e "\n${YELLOW}Press Ctrl+C to stop all services and exit.${NC}"

# Keep script running to maintain the background services
wait $APROXY_PID $PERSONA_PID
