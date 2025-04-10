#!/bin/bash

# Script to run the complete A-Proxy stack (Persona API + A-Proxy) for development
# Runs without Docker for easier debugging and development

# Define colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting A-Proxy Development Stack${NC}"
echo "========================================="

# Create required directories if they don't exist
echo -e "${GREEN}Creating required directories...${NC}"
mkdir -p data persona-service/data

# Ensure data directories exist
echo -e "${GREEN}Setting up data directories...${NC}"
mkdir -p persona-service/data
chmod 755 persona-service/data

# Check database status
if [ ! -f "persona-service/data/persona_service.db" ]; then
    echo -e "${YELLOW}Persona service database not found. Will be created on first run.${NC}"
else  
    echo -e "${GREEN}Found existing database file.${NC}"
    # Optional: Back up the database if needed
    # cp persona-service/data/persona_service.db persona-service/data/persona_service.db.bak
fi

# Generate a JWT secret key if needed
if [ -z "$JWT_SECRET_KEY" ]; then
    export JWT_SECRET_KEY=$(openssl rand -hex 32)
    echo -e "${GREEN}Generated random JWT secret key.${NC}"
fi

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# Cleanup existing processes
echo -e "${GREEN}Cleaning up any existing processes...${NC}"
pkill -f "python run.py" || true
pkill -f "python app.py" || true

# Install dependencies selectively
echo -e "${GREEN}Installing core dependencies...${NC}"
# Install only the persona-client, avoid the problematic dependencies for now
pip install -e ./persona-client > /dev/null

# Fix port issues
echo -e "${GREEN}Checking for port conflicts...${NC}"
fuser -k 5002/tcp 2>/dev/null || true
fuser -k 5050/tcp 2>/dev/null || true
sleep 1

# Function to determine the available terminal emulator
function get_terminal_cmd() {
    if command -v gnome-terminal &> /dev/null; then
        echo "gnome-terminal --title='Persona API Service' -- bash -c"
    elif command -v konsole &> /dev/null; then
        echo "konsole --new-tab -p tabtitle='Persona API Service' -e bash -c"
    elif command -v xfce4-terminal &> /dev/null; then
        echo "xfce4-terminal --title='Persona API Service' -e bash -c"
    elif command -v xterm &> /dev/null; then
        echo "xterm -title 'Persona API Service' -e bash -c"
    elif command -v terminator &> /dev/null; then
        echo "terminator -T 'Persona API Service' -e bash -c"
    else
        echo ""
    fi
}

# Variables to track processes
API_PID=""
API_RUNNING_IN_BACKGROUND=false

# Set DATABASE_URI explicitly for the API service
export DATABASE_URI="sqlite:///${PWD}/persona-service/data/persona_service.db"
echo -e "${GREEN}Setting database URI: ${DATABASE_URI}${NC}"

# Start the Persona API service in a separate terminal or in background
echo -e "${GREEN}Starting Persona API service...${NC}"
TERMINAL_CMD=$(get_terminal_cmd)

if [ -n "$TERMINAL_CMD" ]; then
    # Start in separate terminal window
    eval "$TERMINAL_CMD 'cd persona-service && DATABASE_URI=\"${DATABASE_URI}\" python run.py; read -p \"Press Enter to close...\"'"
else
    # Fallback: Start in background if no terminal emulator is available
    echo -e "${YELLOW}No terminal emulator found. Starting API service in background...${NC}"
    
    # Kill any existing process using the API port
    pkill -f "python run.py" || true
    
    cd persona-service
    # Clear previous log
    > ../persona-api.log
    
    # Start the process with explicit DATABASE_URI
    DATABASE_URI="${DATABASE_URI}" python run.py > ../persona-api.log 2>&1 &
    API_PID=$!
    API_RUNNING_IN_BACKGROUND=true
    cd ..
    
    echo "API service running in background (PID: $API_PID)"
    echo "View logs with: tail -f persona-api.log"
    
    # Output initial log content for debugging
    sleep 2
    if [ -f "persona-api.log" ]; then
        echo -e "${YELLOW}Initial API log output:${NC}"
        tail -n 10 persona-api.log
    fi
fi

# Function to clean up when terminating
cleanup() {
    echo -e "\n${YELLOW}Cleaning up...${NC}"
    if [ "$API_RUNNING_IN_BACKGROUND" = true ] && [ -n "$API_PID" ]; then
        echo "Terminating API service (PID: $API_PID)..."
        kill $API_PID 2>/dev/null || true
    fi
    echo -e "${GREEN}Done!${NC}"
    exit 0
}

# Set up trap for graceful shutdown
trap cleanup SIGINT SIGTERM

# Wait for API to initialize
echo "Waiting for API service to initialize..."
# More robust approach: actually check if the API is responding
for i in {1..10}; do
    echo -n "."
    if curl -s http://localhost:5050/health > /dev/null 2>&1 || curl -s http://localhost:5050/api/v1/health > /dev/null 2>&1; then
        echo -e "\n${GREEN}API service is running!${NC}"
        break
    fi
    
    if [ $i -eq 10 ]; then
        echo -e "\n${YELLOW}Warning: Could not verify API is running. Will try to continue anyway.${NC}"
    fi
    
    sleep 1
done

# Set environment variables for the main app to connect to the API
export PERSONA_API_URL="http://localhost:5050"
export PERSONA_API_VERSION="v1"
export PERSONA_API_TIMEOUT=10

# Check if migration might be needed
if [ ! -f "persona-service/data/persona_service.db" ] && [ -f "data/a_proxy.db" ]; then
    echo -e "${YELLOW}Note: You may need to migrate existing personas to the API:${NC}"
    echo "python migrate_to_api.py"
    echo -e "Run this command in a separate terminal if needed.\n"
fi

# Start the main A-Proxy application in this terminal
echo -e "${GREEN}Starting A-Proxy application...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop both services${NC}"
python app.py

# Clean up when the app is stopped
cleanup
