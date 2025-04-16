#!/bin/bash

# Script to switch from git submodules to local pip install approach
# This provides better separation between repo management and dependencies

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Repository root directory
ROOT_DIR=$(pwd)

echo -e "${BLUE}===== SWITCHING FROM SUBMODULES TO LOCAL PACKAGES =====${NC}"
echo -e "${YELLOW}This script will convert submodule dependencies to locally installed packages${NC}"
echo -e "${YELLOW}This approach provides better separation between repo management and dependency updates${NC}"

# Function to ensure we have venv installed
check_venv() {
  if ! python3 -c "import venv" &> /dev/null; then
    echo -e "${RED}Python venv module not found. Please install it first.${NC}"
    echo -e "On Ubuntu/Debian: ${GREEN}sudo apt-get install python3-venv${NC}"
    exit 1
  fi
}

# Check for required commands
check_venv

# Ensure virtual environment exists
if [ ! -d "venv" ]; then
  echo -e "${YELLOW}Creating Python virtual environment...${NC}"
  python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install Flask-Migrate in the virtual environment
echo -e "${YELLOW}Installing Flask-Migrate...${NC}"
pip install flask-migrate

# Check if we should remove submodules
echo -e "${YELLOW}Do you want to keep the existing submodule directories? (y/n)${NC}"
echo -e "${YELLOW}(Answering 'n' will clone fresh copies to _src directory)${NC}"
read -p "> " keep_dirs

# Install persona-service as a local package
echo -e "\n${BLUE}==== Installing persona-service as a local package ====${NC}"

if [ "$keep_dirs" = "n" ] || [ "$keep_dirs" = "N" ]; then
    # Create _src directory if it doesn't exist
    mkdir -p _src
    
    # Clone fresh copies
    echo -e "${YELLOW}Cloning fresh copy of persona-service...${NC}"
    git clone https://github.com/savingads/persona-service.git _src/persona-service
    
    # Check if we should check out specific branches
    echo -e "${YELLOW}Do you want to check out the develop branch for persona-service? (y/n)${NC}"
    read -p "> " checkout_branch
    
    if [ "$checkout_branch" = "y" ] || [ "$checkout_branch" = "Y" ]; then
        cd _src/persona-service
        git checkout develop
        cd $ROOT_DIR
    fi
    
    # Install from the cloned directory
    echo -e "${YELLOW}Installing persona-service in development mode...${NC}"
    pip install -e _src/persona-service

    # Copy init_db.py to the cloned directory for later use
    if [ -f "persona-service/init_db.py" ]; then
        echo -e "${YELLOW}Copying init_db.py to cloned directory...${NC}"
        cp persona-service/init_db.py _src/persona-service/
        chmod +x _src/persona-service/init_db.py
    fi
else
    # Install from existing directory
    echo -e "${YELLOW}Installing persona-service in development mode from existing directory...${NC}"
    pip install -e persona-service
fi

# Install agent_module as a local package
echo -e "\n${BLUE}==== Installing agent_module as a local package ====${NC}"

if [ "$keep_dirs" = "n" ] || [ "$keep_dirs" = "N" ]; then
    # Clone fresh copy
    echo -e "${YELLOW}Cloning fresh copy of agent_module...${NC}"
    git clone https://github.com/cr625/agent_module.git _src/agent_module
    
    # Check if we should check out specific branches
    echo -e "${YELLOW}Do you want to check out the personas branch for agent_module? (y/n)${NC}"
    read -p "> " checkout_branch
    
    if [ "$checkout_branch" = "y" ] || [ "$checkout_branch" = "Y" ]; then
        cd _src/agent_module
        git checkout personas || git checkout -b personas
        cd $ROOT_DIR
    fi
    
    # Install from the cloned directory
    echo -e "${YELLOW}Installing agent_module in development mode...${NC}"
    pip install -e _src/agent_module
else
    # Install from existing directory
    echo -e "${YELLOW}Installing agent_module in development mode from existing directory...${NC}"
    pip install -e agent_module
fi

# Update import statements in the main repo
echo -e "\n${BLUE}==== Updating imports to use package imports ====${NC}"

# Fix any direct imports referencing the old paths
echo -e "${YELLOW}Updating import statements in routes/agent.py...${NC}"
if [ -f "routes/agent.py" ]; then
    # Create backup
    cp routes/agent.py routes/agent.py.bak
    
    # Update the import statements
    sed -i 's/from agent_module import /import agent_module\nfrom agent_module import /g' routes/agent.py
    
    echo -e "${GREEN}Updated routes/agent.py (backup saved as routes/agent.py.bak)${NC}"
fi

# Update utils/agent.py
echo -e "${YELLOW}Updating import statements in utils/agent.py...${NC}"
if [ -f "utils/agent.py" ]; then
    # Create backup
    cp utils/agent.py utils/agent.py.bak
    
    # Update the import statements
    sed -i 's/from agent_module import /import agent_module\nfrom agent_module import /g' utils/agent.py
    
    echo -e "${GREEN}Updated utils/agent.py (backup saved as utils/agent.py.bak)${NC}"
fi

# Create a modified startup script
echo -e "\n${BLUE}==== Creating new startup script ====${NC}"
cat > start-with-packages.sh << 'EOF'
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
EOF

chmod +x start-with-packages.sh

echo -e "\n${GREEN}===== CONVERSION COMPLETED =====${NC}"
echo -e "${YELLOW}To start the application with the new package approach, run:${NC}"
echo -e "${GREEN}./start-with-packages.sh${NC}"
echo -e "${YELLOW}This approach makes it easier to manage code changes in each repository independently.${NC}"
