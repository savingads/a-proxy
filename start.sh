#!/bin/bash
# start.sh - Start the A-Proxy application

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting A-Proxy...${NC}"

# Repository root directory
ROOT_DIR=$(pwd)

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# Ensure dependencies are installed
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}Checking Python dependencies...${NC}"
    pip install -q -r requirements.txt
fi

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    echo -e "${YELLOW}Creating data directory...${NC}"
    mkdir -p data
fi

# Initialize database
echo -e "${YELLOW}Initializing database...${NC}"
python -c "import database" 2>/dev/null || {
    echo -e "${RED}Database initialization failed!${NC}"
    exit 1
}

# Initialize default user if needed
if [ -f "init_default_user.py" ]; then
    python init_default_user.py 2>/dev/null
fi

# Function to check and kill processes using specific ports
kill_port_processes() {
    local port=$1
    local service_name=$2

    if command -v lsof >/dev/null 2>&1; then
        local pid=$(lsof -ti:$port)
        if [ ! -z "$pid" ]; then
            echo -e "${YELLOW}Found $service_name already running on port $port (PID: $pid)${NC}"
            echo -e "${YELLOW}Killing existing process...${NC}"
            kill -9 $pid 2>/dev/null
            sleep 1
            echo -e "${GREEN}Process terminated${NC}"
        fi
    fi
}

# Parse command line arguments
PORT=${1:-5002}
HOST=${2:-127.0.0.1}

# Kill any existing service on the port
kill_port_processes $PORT "A-Proxy"

# Start A-Proxy
echo -e "${YELLOW}Starting A-Proxy on http://${HOST}:${PORT}...${NC}"
python app.py --port $PORT --host $HOST &
APROXY_PID=$!

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to start A-Proxy!${NC}"
    exit 1
fi

echo -e "${GREEN}A-Proxy running with PID: ${APROXY_PID}${NC}"

# Set up trap to handle script termination
cleanup() {
    echo -e "\n${YELLOW}Shutting down A-Proxy...${NC}"
    if [ ! -z "$APROXY_PID" ]; then
        kill $APROXY_PID 2>/dev/null || true
    fi
    echo -e "${GREEN}Done!${NC}"
}

trap cleanup EXIT INT TERM

echo -e "\n${BLUE}A-Proxy is running:${NC}"
echo -e "  - URL: ${GREEN}http://${HOST}:${PORT}${NC}"
echo -e "  - Default login: ${GREEN}admin@example.com / password${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop the server.${NC}"

# Keep script running
wait $APROXY_PID
