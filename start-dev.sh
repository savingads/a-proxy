#!/bin/bash

# Main development startup script for running A-Proxy without Docker
# Starts the Persona Service and main application

# Allow errors without exiting for better error handling
# set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Repository root directory
ROOT_DIR=$(pwd)
PERSONA_SERVICE_DIR="${ROOT_DIR}/persona-service"
DB_PATH="${PERSONA_SERVICE_DIR}/data/persona_service.db"

# Check for required commands
check_command() {
  if ! command -v $1 &> /dev/null; then
    echo -e "${RED}$1 could not be found. Please install it first.${NC}"
    exit 1
  fi
}

# Function to ensure we have venv installed
check_venv() {
  if ! python3 -c "import venv" &> /dev/null; then
    echo -e "${RED}Python venv module not found. Please install it first.${NC}"
    echo -e "On Ubuntu/Debian: ${GREEN}sudo apt-get install python3-venv${NC}"
    exit 1
  fi
}

check_command python3
check_command curl
check_venv

# Check if necessary directories exist
if [ ! -d "$PERSONA_SERVICE_DIR" ]; then
    echo -e "${RED}persona-service directory doesn't exist at ${PERSONA_SERVICE_DIR}!${NC}"
    exit 1
fi

# Ensure data directory exists
mkdir -p "${PERSONA_SERVICE_DIR}/data"
chmod 755 "${PERSONA_SERVICE_DIR}/data"

# Create Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo -e "${YELLOW}Creating Python virtual environment...${NC}"
  python3 -m venv venv
fi

# Function to set up Python environment
setup_python_env() {
  echo -e "${YELLOW}Setting up Python environment...${NC}"
  . venv/bin/activate
  
  # Install requirements for persona-service
  cd $PERSONA_SERVICE_DIR
  echo -e "${YELLOW}Installing Persona Service requirements...${NC}"
  pip install -r requirements.txt
  
  # Install additional dependencies that might be needed
  echo -e "${YELLOW}Installing additional dependencies...${NC}"
  pip install flask-sqlalchemy flask-marshmallow marshmallow-sqlalchemy requests
  cd $ROOT_DIR
  
  # Install main app requirements
  echo -e "${YELLOW}Installing A-Proxy requirements...${NC}"
  pip install -r requirements.txt

  # Ensure persona-client submodule is initialized and updated
  echo -e "${YELLOW}Initializing persona-client submodule...${NC}"
  git submodule update --init --recursive

  # Install persona-client module
  echo -e "${YELLOW}Installing persona-client module...${NC}"
  cd persona-client
  pip install .
  cd $ROOT_DIR
}

# Function to initialize the Persona Service database
init_persona_db() {
  echo -e "${YELLOW}Ensuring Persona Service database is properly initialized...${NC}"
  . venv/bin/activate
  
  # Make the init_db.py script executable
  chmod +x "${PERSONA_SERVICE_DIR}/init_db.py"
  
  # Run the dedicated initialization script
  cd $PERSONA_SERVICE_DIR
  python init_db.py
  DB_INIT_STATUS=$?
  cd $ROOT_DIR
  
  if [ $DB_INIT_STATUS -ne 0 ]; then
    echo -e "${RED}Failed to initialize Persona Service database${NC}"
    exit 1
  fi
  
  echo -e "${GREEN}Persona Service database initialized successfully${NC}"
}

# Function to start the Persona Service
start_persona_service() {
  echo -e "${YELLOW}Starting Persona Service API on port 5050...${NC}"
  . venv/bin/activate
  
  cd $PERSONA_SERVICE_DIR
  python run.py --debug &
  PERSONA_PID=$!
  cd $ROOT_DIR
  
  echo -e "${GREEN}Persona Service running with PID: ${PERSONA_PID}${NC}"
  echo -e "${YELLOW}Waiting for service to initialize...${NC}"
  sleep 5  # Give it time to start up and initialize database
}

# Function to verify the Persona Service API is responsive
verify_persona_service() {
  local max_attempts=10
  local wait_time=2
  local attempt=1
  local url="http://localhost:5050/health"
  
  echo -e "${YELLOW}Verifying Persona Service API is responsive...${NC}"
  
  while [ $attempt -le $max_attempts ]; do
    echo -e "Attempt $attempt/$max_attempts: Checking $url"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" $url)
    
    if [ "$response" -eq 200 ]; then
      echo -e "${GREEN}Persona Service API is responsive!${NC}"
      return 0
    fi
    
    attempt=$((attempt + 1))
    
    if [ $attempt -le $max_attempts ]; then
      echo -e "${YELLOW}Service not ready, waiting ${wait_time} seconds...${NC}"
      sleep $wait_time
    fi
  done
  
  echo -e "${RED}Persona Service API is not responding after ${max_attempts} attempts${NC}"
  echo -e "${YELLOW}Continuing anyway, but you may experience issues with persona functionality${NC}"
  return 1
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
echo -e "${YELLOW}==== Setting up A-Proxy Development Environment ====${NC}"
echo -e "${BLUE}Root directory: ${ROOT_DIR}${NC}"
echo -e "${BLUE}Persona Service directory: ${PERSONA_SERVICE_DIR}${NC}"
echo -e "${BLUE}Database path: ${DB_PATH}${NC}"

# Stop any existing processes
echo -e "${YELLOW}Stopping any existing processes...${NC}"
pkill -f "python run.py --debug" 2>/dev/null || true
pkill -f "python app.py" 2>/dev/null || true
sleep 2

# Setup environment
setup_python_env

# Initialize and verify database before starting services
init_persona_db

# Function to ensure sample personas exist in the database
ensure_sample_personas() {
  echo -e "${YELLOW}Checking if sample personas exist in the database...${NC}"
  . venv/bin/activate
  
  # Create a simple Python script to check if personas exist
  CHECK_SCRIPT=$(mktemp)
  cat > $CHECK_SCRIPT << 'EOF'
import sys
import os

# Add the root directory to the path so we can import personaclient
sys.path.insert(0, os.path.abspath(os.getcwd()))

try:
    from personaclient import PersonaClient
    
    client = PersonaClient(base_url="http://localhost:5050")
    result = client.get_all_personas()
    personas = result.get('personas', [])
    
    if len(personas) == 0:
        print("No personas found in the database")
        sys.exit(1)
    else:
        print(f"Found {len(personas)} personas in the database")
        sys.exit(0)
except Exception as e:
    print(f"Error checking personas: {str(e)}")
    sys.exit(1)
EOF

  # Run the script to check if personas exist
  python $CHECK_SCRIPT
  HAS_PERSONAS=$?
  rm $CHECK_SCRIPT
  
  if [ $HAS_PERSONAS -ne 0 ]; then
    echo -e "${YELLOW}No personas found. Creating sample personas...${NC}"
    
    # Run the create-personas.py script to add sample personas
    # Passing count=5 to create all 5 sample personas 
    python create-personas.py --api-url http://localhost:5050 --count 5
    
    # Check the result
    if [ $? -eq 0 ]; then
      echo -e "${GREEN}Sample personas created successfully${NC}"
    else
      echo -e "${RED}Failed to create sample personas${NC}"
    fi
  else
    echo -e "${GREEN}Sample personas already exist in the database${NC}"
  fi
}

# Start services
start_persona_service
verify_persona_service
ensure_sample_personas
start_a_proxy

echo -e "${BLUE}Services are running:${NC}"
echo -e "  - Persona Service API: ${GREEN}http://localhost:5050${NC}"
echo -e "  - A-Proxy: ${GREEN}http://localhost:5002${NC}"

echo -e "\n${YELLOW}Press Ctrl+C to stop all services and exit.${NC}"

# Keep script running to maintain the background services
wait $APROXY_PID $PERSONA_PID
