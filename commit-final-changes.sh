#!/bin/bash

# Script to commit all final changes to the repository

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== COMMITTING FINAL CHANGES =====${NC}"
echo -e "${YELLOW}This script will commit all the changes to your repository${NC}"

# Add modified files
echo -e "\n${BLUE}=== Adding modified files ===${NC}"
git add utils/agent.py
echo -e "${GREEN}Added utils/agent.py${NC}"

# Add new script files but not backup files
echo -e "\n${BLUE}=== Adding new script files ===${NC}"
git add remove-submodules.sh
git add start-with-packages.sh
git add switch-to-local-packages.sh
echo -e "${GREEN}Added new script files${NC}"

# Check if routes/agent.py is modified
if git status --porcelain | grep -q "M routes/agent.py"; then
    echo -e "${YELLOW}Adding routes/agent.py${NC}"
    git add routes/agent.py
    echo -e "${GREEN}Added routes/agent.py${NC}"
fi

# Skip backup files
echo -e "\n${BLUE}=== Skipping backup files ===${NC}"
echo -e "${YELLOW}Skipping *.bak files${NC}"

# Show status before commit
echo -e "\n${BLUE}=== Current status ===${NC}"
git status

# Ask for commit message
echo -e "\n${YELLOW}Enter commit message:${NC}"
read -p "> " commit_message

if [ -z "$commit_message" ]; then
    commit_message="Switch from submodules to local packages for agent integration"
fi

# Commit changes
echo -e "\n${BLUE}=== Committing changes ===${NC}"
git commit -m "$commit_message"

# Push changes
echo -e "\n${YELLOW}Do you want to push these changes to remote? (y/n)${NC}"
read -p "> " push_choice

if [ "$push_choice" = "y" ] || [ "$push_choice" = "Y" ]; then
    echo -e "\n${BLUE}=== Pushing changes ===${NC}"
    git push
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Changes successfully pushed to remote repository${NC}"
    else
        echo -e "${RED}Failed to push changes${NC}"
    fi
else
    echo -e "${YELLOW}Changes committed locally but not pushed.${NC}"
fi

echo -e "\n${GREEN}===== COMMIT PROCESS COMPLETED =====${NC}"
