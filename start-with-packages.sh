#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Repository root directory
ROOT_DIR=$(pwd)

# Activate virtual environment
source venv/bin/activate

# Ensure persona-service database is initialized
echo -e "${YELLOW}Initializing persona-service database...${NC}"

# Check if we're using the source directory
if [ -d "_src/persona-service" ]; then
    cd _src/persona-service
else
    cd persona-service
fi

# Create data directory if it doesn't exist
mkdir -p data
chmod 755 data

# Run database initialization
if [ -f "init_db.py" ]; then
    python init_db.py
else
    echo -e "${RED}init_db.py not found!${NC}"
    exit 1
fi

cd $ROOT_DIR

# Start persona-service API
echo -e "${YELLOW}Starting persona-service API on port 5050...${NC}"
if [ -d "_src/persona-service" ]; then
    cd _src/persona-service
else
    cd persona-service
fi

python run.py --debug &
PERSONA_PID=$!
cd $ROOT_DIR

echo -e "${GREEN}Persona Service running with PID: ${PERSONA_PID}${NC}"
echo -e "${YELLOW}Waiting for service to initialize...${NC}"
sleep 5

# Start A-Proxy
echo -e "${YELLOW}Starting A-Proxy application on port 5002...${NC}"
python app.py --port 5002 --host 127.0.0.1 &
APROXY_PID=$!

echo -e "${GREEN}A-Proxy running with PID: ${APROXY_PID}${NC}"

# Set up trap to handle script termination
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

trap cleanup EXIT INT TERM

echo -e "${BLUE}Services are running:${NC}"
echo -e "  - Persona Service API: ${GREEN}http://localhost:5050${NC}"
echo -e "  - A-Proxy: ${GREEN}http://localhost:5002${NC}"

echo -e "\n${YELLOW}Press Ctrl+C to stop all services and exit.${NC}"

# Keep script running to maintain the background services
wait $APROXY_PID $PERSONA_PID
