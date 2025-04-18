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

# Ensure necessary files are available in the persona-service directory
if [ ! -f "_src/persona-service/persona_field_config.py" ]; then
    echo -e "${YELLOW}First-time setup: copying necessary files...${NC}"
    if [ -f "fix-persona-service-dependencies.sh" ]; then
        ./fix-persona-service-dependencies.sh
    else
        echo -e "${RED}fix-persona-service-dependencies.sh not found!${NC}"
        echo -e "${RED}Please run switch-to-local-packages.sh first.${NC}"
        exit 1
    fi
fi

# Ensure persona-service database is initialized
echo -e "${YELLOW}Initializing persona-service database...${NC}"

# Check if we're using the source directory
if [ -d "_src/persona-service" ]; then
    cd _src/persona-service
else
    echo -e "${RED}_src/persona-service directory not found!${NC}"
    echo -e "${RED}Please run switch-to-local-packages.sh first.${NC}"
    exit 1
fi

# Create data directory if it doesn't exist
mkdir -p data
chmod 755 data

# Run database initialization
if [ -f "init_db.py" ]; then
    PYTHONPATH=$ROOT_DIR/_src python init_db.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}Database initialization failed!${NC}"
        cd $ROOT_DIR
        exit 1
    fi
else
    echo -e "${RED}init_db.py not found!${NC}"
    cd $ROOT_DIR
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

# Export PYTHONPATH to include the root directory
export PYTHONPATH=$ROOT_DIR:$PYTHONPATH

python run.py --debug &
PERSONA_PID=$!
cd $ROOT_DIR

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to start persona-service!${NC}"
    exit 1
fi

echo -e "${GREEN}Persona Service running with PID: ${PERSONA_PID}${NC}"
echo -e "${YELLOW}Waiting for service to initialize...${NC}"
sleep 5

# Start A-Proxy
echo -e "${YELLOW}Starting A-Proxy application on port 5002...${NC}"
python app.py --port 5002 --host 127.0.0.1 &
APROXY_PID=$!

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to start A-Proxy!${NC}"
    kill $PERSONA_PID 2>/dev/null || true
    exit 1
fi

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
