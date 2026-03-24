#!/bin/bash

# Script to fix the agent_module submodule by checking out the personas branch

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== Fixing agent_module submodule =====${NC}"
echo -e "${YELLOW}This script will check out the personas branch for the agent_module submodule${NC}"

# Check if the agent_module directory exists
if [ ! -d "agent_module" ]; then
    echo -e "${RED}agent_module directory doesn't exist!${NC}"
    exit 1
fi

# Initialize and update the submodule
echo -e "${YELLOW}Initializing and updating agent_module submodule...${NC}"
git submodule update --init agent_module

# Navigate to the submodule directory
cd agent_module

# Check which branch we're on
echo -e "${YELLOW}Current branch or commit:${NC}"
git status

# Check out the personas branch
echo -e "${YELLOW}Attempting to checkout personas branch...${NC}"
git checkout personas

# Check if the checkout was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Successfully checked out personas branch for agent_module${NC}"
    git status
else
    echo -e "${RED}Failed to checkout personas branch${NC}"
    
    # List available branches
    echo -e "${YELLOW}Available branches:${NC}"
    git branch -a
    
    # Try to create the branch if it doesn't exist
    echo -e "${YELLOW}Attempting to create personas branch from current commit...${NC}"
    git checkout -b personas
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Created and checked out personas branch${NC}"
    else
        echo -e "${RED}Failed to create personas branch${NC}"
    fi
fi

# Return to the root directory
cd ..

# Now commit the submodule reference change in the main repository
echo -e "${YELLOW}Do you want to add and commit this submodule change? (y/n)${NC}"
read -p "> " commit_choice

if [ "$commit_choice" = "y" ] || [ "$commit_choice" = "Y" ]; then
    git add agent_module
    git commit -m "Update agent_module submodule to personas branch"
    
    echo -e "${YELLOW}Do you want to push this change? (y/n)${NC}"
    read -p "> " push_choice
    
    if [ "$push_choice" = "y" ] || [ "$push_choice" = "Y" ]; then
        git push
    fi
fi

echo -e "${GREEN}===== agent_module submodule fix completed =====${NC}"
