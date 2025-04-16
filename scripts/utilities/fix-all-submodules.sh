#!/bin/bash

# Master script to fix all submodules and commit changes

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== FIXING ALL SUBMODULES =====${NC}"
echo -e "${YELLOW}This script will fix both agent_module and persona-service submodules${NC}"
echo -e "${YELLOW}Then commit all changes to the main repository${NC}"

# Fix agent_module first
if [ -f "./fix-agent-module.sh" ]; then
    echo -e "\n${BLUE}==== Step 1: Fixing agent_module ====${NC}"
    ./fix-agent-module.sh
else
    echo -e "${RED}fix-agent-module.sh script not found!${NC}"
    exit 1
fi

# Fix persona-service next
if [ -f "./fix-persona-service.sh" ]; then
    echo -e "\n${BLUE}==== Step 2: Fixing persona-service ====${NC}"
    ./fix-persona-service.sh
else
    echo -e "${RED}fix-persona-service.sh script not found!${NC}"
    exit 1
fi

# Final check of the main repository
echo -e "\n${BLUE}==== Step 3: Final status check ====${NC}"
git status

# Ask if ready to commit everything
echo -e "\n${YELLOW}Are you ready to commit all remaining changes? (y/n)${NC}"
read -p "> " commit_choice

if [ "$commit_choice" = "y" ] || [ "$commit_choice" = "Y" ]; then
    git add .
    echo -e "${YELLOW}Enter final commit message:${NC}"
    read -p "> " commit_message
    
    if [ -z "$commit_message" ]; then
        commit_message="Fix all submodules and update references"
    fi
    
    git commit -m "$commit_message"
    
    echo -e "${YELLOW}Do you want to push all changes? (y/n)${NC}"
    read -p "> " push_choice
    
    if [ "$push_choice" = "y" ] || [ "$push_choice" = "Y" ]; then
        git push
    fi
    
    echo -e "${GREEN}All changes committed successfully!${NC}"
else
    echo -e "${YELLOW}No final commit made. You can review changes and commit manually.${NC}"
fi

echo -e "\n${GREEN}===== ALL SUBMODULE FIXES COMPLETED =====${NC}"
echo -e "${YELLOW}Use ./commit-changes.sh for future commits to maintain proper submodule references${NC}"
