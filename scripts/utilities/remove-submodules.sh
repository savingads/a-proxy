#!/bin/bash

# Script to safely remove git submodules after switching to local packages

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== REMOVING GIT SUBMODULES =====${NC}"
echo -e "${YELLOW}This script will properly remove git submodules from the repository${NC}"
echo -e "${YELLOW}Run this AFTER you've successfully completed the switch to local packages${NC}"

# Ensure we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}Not a git repository!${NC}"
    exit 1
fi

# Confirm removal
echo -e "${YELLOW}Are you sure you want to remove all submodules? (y/n)${NC}"
read -p "> " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo -e "${YELLOW}Operation cancelled.${NC}"
    exit 0
fi

# List to store submodule paths
declare -a submodules

# Get list of registered submodules
echo -e "${YELLOW}Finding registered submodules...${NC}"
while read path; do
    if [ ! -z "$path" ]; then
        submodules+=("$path")
        echo -e "  - Found submodule: ${GREEN}$path${NC}"
    fi
done < <(git config --file .gitmodules --get-regexp path | awk '{ print $2 }')

if [ ${#submodules[@]} -eq 0 ]; then
    echo -e "${YELLOW}No submodules found to remove.${NC}"
    
    # Check if .gitmodules exists but has no submodules
    if [ -f ".gitmodules" ]; then
        echo -e "${YELLOW}Removing empty .gitmodules file...${NC}"
        git rm -f .gitmodules
        echo -e "${GREEN}Removed .gitmodules file${NC}"
    fi
    
    exit 0
fi

# Process each submodule
for submodule in "${submodules[@]}"; do
    echo -e "\n${BLUE}=== Removing submodule: $submodule ===${NC}"
    
    # Step 1: Unregister the submodule
    echo -e "${YELLOW}Unregistering $submodule from git...${NC}"
    git submodule deinit -f "$submodule"
    
    # Step 2: Remove from git index
    echo -e "${YELLOW}Removing $submodule from git index...${NC}"
    git rm --cached "$submodule"
    
    # Step 3: Remove the actual directory if it exists
    if [ -d "$submodule" ]; then
        echo -e "${YELLOW}Checking if we should keep the directory...${NC}"
        echo -e "${YELLOW}Keep the $submodule directory? (y/n)${NC}"
        read -p "> " keep_dir
        
        if [ "$keep_dir" != "y" ] && [ "$keep_dir" != "Y" ]; then
            echo -e "${YELLOW}Removing $submodule directory...${NC}"
            rm -rf "$submodule"
            echo -e "${GREEN}Removed $submodule directory${NC}"
        else
            echo -e "${GREEN}Keeping $submodule directory${NC}"
        fi
    fi
    
    # Step 4: Remove the .git/modules entry
    echo -e "${YELLOW}Removing .git/modules/$submodule...${NC}"
    rm -rf ".git/modules/$submodule"
    
    echo -e "${GREEN}=== Submodule $submodule removed successfully ===${NC}"
done

# Remove .gitmodules file
if [ -f ".gitmodules" ]; then
    echo -e "\n${YELLOW}Removing .gitmodules file...${NC}"
    git rm -f .gitmodules
    echo -e "${GREEN}Removed .gitmodules file${NC}"
fi

# Commit the changes
echo -e "\n${YELLOW}Do you want to commit these changes? (y/n)${NC}"
read -p "> " commit_choice

if [ "$commit_choice" = "y" ] || [ "$commit_choice" = "Y" ]; then
    echo -e "${YELLOW}Committing changes...${NC}"
    git commit -m "Remove git submodules in favor of local packages"
    
    echo -e "${YELLOW}Do you want to push these changes? (y/n)${NC}"
    read -p "> " push_choice
    
    if [ "$push_choice" = "y" ] || [ "$push_choice" = "Y" ]; then
        echo -e "${YELLOW}Pushing changes...${NC}"
        git push
    fi
fi

echo -e "\n${GREEN}===== SUBMODULE REMOVAL COMPLETED =====${NC}"
echo -e "${YELLOW}The submodules have been properly removed from the repository.${NC}"
echo -e "${YELLOW}Your current branch is now free of submodule references.${NC}"
