#!/bin/bash
# start.sh - Start the A-Proxy application with repository synchronization

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Repository root directory
ROOT_DIR=$(pwd)

# Function to check repository status
check_repo_status() {
    local repo_path=$1
    local repo_name=$(basename "$repo_path")
    
    if [ ! -d "$repo_path" ]; then
        echo -e "${RED}Repository $repo_name not found at $repo_path${NC}"
        return 1
    fi
    
    cd "$repo_path" || return 1
    
    # Check if repo has changes
    if git status --porcelain | grep -q .; then
        echo -e "${YELLOW}[$repo_name] has uncommitted changes${NC}"
        has_changes="true"
    else
        echo -e "${GREEN}[$repo_name] is clean${NC}"
    fi
    
    # Check if repo has unpushed commits
    local current_branch=$(git rev-parse --abbrev-ref HEAD)
    local unpushed=$(git log @{u}.. 2>/dev/null)
    if [ ! -z "$unpushed" ]; then
        echo -e "${YELLOW}[$repo_name] has unpushed commits on branch $current_branch${NC}"
        has_unpushed="true"
    fi
    
    cd - > /dev/null
    return 0
}

# Function to synchronize repositories
sync_repos() {
    echo -e "${BLUE}Synchronizing repositories...${NC}"
    
    if [ ! -f "$ROOT_DIR/sync-repos.sh" ]; then
        echo -e "${RED}sync-repos.sh not found!${NC}"
        return 1
    fi
    
    # Ask for commit message
    read -p "Enter commit message for synchronization: " commit_message
    if [ -z "$commit_message" ]; then
        commit_message="Automatic synchronization from start.sh"
    fi
    
    # Run the sync-repos.sh script
    "$ROOT_DIR/sync-repos.sh" "$commit_message"
    return $?
}

# Check repository status
echo -e "${BLUE}Checking repository status...${NC}"
has_changes="false"
has_unpushed="false"

check_repo_status "$ROOT_DIR"
check_repo_status "$ROOT_DIR/_src/persona-service"
check_repo_status "$ROOT_DIR/_src/agent_module"

# If there are changes, offer to sync repositories
if [ "$has_changes" = "true" ] || [ "$has_unpushed" = "true" ]; then
    echo ""
    read -p "Would you like to synchronize repositories before starting? (y/n): " sync_choice
    if [[ "$sync_choice" =~ ^[Yy]$ ]]; then
        sync_repos
        if [ $? -ne 0 ]; then
            echo -e "${RED}Repository synchronization failed!${NC}"
            echo -e "${YELLOW}Continuing with application startup...${NC}"
        fi
    fi
fi

# Check if _src repos exist, if not, run switch-to-local-packages.sh automatically
if [ ! -d "_src/persona-service" ] || [ ! -d "_src/agent_module" ]; then
    echo -e "${YELLOW}Required source repos not found. Running switch-to-local-packages.sh...${NC}"
    if [ -f "switch-to-local-packages.sh" ]; then
        bash switch-to-local-packages.sh
    else
        echo -e "${RED}switch-to-local-packages.sh not found!${NC}"
        exit 1
    fi
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo -e "${YELLOW}Virtual environment not found, running without it...${NC}"
fi

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

# Ensure persona-service dependencies are installed
if [ -d "_src/persona-service" ]; then
    if [ -f "_src/persona-service/requirements.txt" ]; then
        echo -e "${YELLOW}Installing persona-service Python dependencies...${NC}"
        pip install -r _src/persona-service/requirements.txt
    else
        echo -e "${YELLOW}No requirements.txt found in _src/persona-service. Using root requirements.txt if available...${NC}"
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt
        fi
    fi
else
    echo -e "${RED}_src/persona-service directory not found!${NC}"
    exit 1
fi

# Ensure persona_field_config.py exists in persona-service
if [ ! -f "_src/persona-service/persona_field_config.py" ]; then
    if [ -f "persona_field_config.py" ]; then
        echo -e "${YELLOW}Copying persona_field_config.py to _src/persona-service...${NC}"
        cp persona_field_config.py _src/persona-service/
    elif [ -f "sample_custom_field_config.json" ]; then
        echo -e "${YELLOW}Creating persona_field_config.py from sample_custom_field_config.json...${NC}"
        cp sample_custom_field_config.json _src/persona-service/persona_field_config.py
    else
        echo -e "${RED}No persona_field_config.py or sample_custom_field_config.json found!${NC}"
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
