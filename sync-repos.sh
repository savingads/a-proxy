#!/bin/bash
# sync-repos.sh - Synchronize changes across repositories
# Usage: ./sync-repos.sh "Commit message here"

# Display help if no argument provided
if [ -z "$1" ]; then
    echo "Usage: ./sync-repos.sh \"Your commit message here\""
    echo "This script commits changes to all repositories with the same message."
    exit 1
fi

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to handle repository sync
sync_repo() {
    local repo_path=$1
    local branch=$2
    local repo_name=$(basename "$repo_path")
    
    echo -e "${BLUE}Syncing $repo_name repository...${NC}"
    
    # Check if directory exists
    if [ ! -d "$repo_path" ]; then
        echo -e "${RED}Error: Directory $repo_path does not exist${NC}"
        return 1
    fi
    
    # Change to repo directory
    cd "$repo_path" || { echo -e "${RED}Error: Could not change to directory $repo_path${NC}"; return 1; }
    
    # Check if there are changes to commit
    if git status --porcelain | grep -q .; then
        echo -e "${YELLOW}Changes detected in $repo_name...${NC}"
        git add .
        git commit -m "$1"
        
        # Push if origin remote exists and branch is specified
        if [ ! -z "$branch" ] && git remote | grep -q "origin"; then
            echo -e "${YELLOW}Pushing changes to origin/$branch...${NC}"
            git push origin "$branch"
        fi
        echo -e "${GREEN}✓ $repo_name synchronization complete${NC}"
    else
        echo -e "${GREEN}✓ No changes to commit in $repo_name${NC}"
    fi
    
    # Return to original directory
    cd - > /dev/null
}

# Get current directory
current_dir=$(pwd)

# Sync persona-service repository
sync_repo "$current_dir/_src/persona-service" "develop" "$1"

# Sync agent_module repository  
sync_repo "$current_dir/_src/agent_module" "personas" "$1"

# Sync main repository
echo -e "${BLUE}Syncing main repository...${NC}"
cd "$current_dir" || { echo -e "${RED}Error: Could not change to main directory${NC}"; exit 1; }

# Check if there are changes to commit
if git status --porcelain | grep -q .; then
    echo -e "${YELLOW}Changes detected in main repository...${NC}"
    git add .
    git commit -m "$1"
    
    # Get current branch
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    
    # Push if origin remote exists
    if git remote | grep -q "origin"; then
        echo -e "${YELLOW}Pushing changes to origin/$current_branch...${NC}"
        git push origin "$current_branch"
    fi
    echo -e "${GREEN}✓ Main repository synchronization complete${NC}"
else
    echo -e "${GREEN}✓ No changes to commit in main repository${NC}"
fi

echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}All repositories synchronized!${NC}"
echo -e "${GREEN}==================================${NC}"
