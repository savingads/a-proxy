#!/bin/bash

# Script to commit changes to submodules and main repository in the correct order
# This ensures proper references are maintained

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Repository root directory
ROOT_DIR=$(pwd)

# Function to commit changes to a specific submodule
commit_submodule() {
    local submodule_path=$1
    local submodule_name=$(basename $submodule_path)
    
    echo -e "${BLUE}=== Processing submodule: $submodule_name ===${NC}"
    
    # Check if directory exists
    if [ ! -d "$submodule_path" ]; then
        echo -e "${RED}Submodule directory $submodule_path not found!${NC}"
        return 1
    fi
    
    # Enter submodule directory
    cd "$submodule_path"
    
    # Check if this is actually a git repository
    if [ ! -d ".git" ]; then
        echo -e "${RED}Not a git repository: $submodule_path${NC}"
        cd "$ROOT_DIR"
        return 1
    fi
    
    # Get current branch
    local current_branch=$(git rev-parse --abbrev-ref HEAD)
    echo -e "${YELLOW}Current branch: $current_branch${NC}"
    
    # Check for changes
    if ! git diff-index --quiet HEAD --; then
        # Changes exist
        echo -e "${YELLOW}Changes detected in $submodule_name${NC}"
        
        # Show status
        git status
        
        # Ask for commit message
        echo -e "${YELLOW}Enter commit message for $submodule_name (or 'skip' to skip):${NC}"
        read -p "> " commit_message
        
        if [ "$commit_message" = "skip" ]; then
            echo -e "${YELLOW}Skipping commit for $submodule_name${NC}"
        else
            # Add all changes
            git add .
            
            # Commit changes
            git commit -m "$commit_message"
            
            # Push changes (ask first)
            echo -e "${YELLOW}Do you want to push changes to remote? (y/n)${NC}"
            read -p "> " push_choice
            
            if [ "$push_choice" = "y" ] || [ "$push_choice" = "Y" ]; then
                # Ensure our branch exists on remote before pushing
                if git ls-remote --heads origin $current_branch | grep -q $current_branch; then
                    git push origin $current_branch
                else
                    echo -e "${YELLOW}Branch $current_branch doesn't exist on remote.${NC}"
                    echo -e "${YELLOW}Do you want to push and set upstream? (y/n)${NC}"
                    read -p "> " setup_upstream
                    
                    if [ "$setup_upstream" = "y" ] || [ "$setup_upstream" = "Y" ]; then
                        git push --set-upstream origin $current_branch
                    else
                        echo -e "${YELLOW}Changes committed locally but not pushed.${NC}"
                    fi
                fi
            else
                echo -e "${YELLOW}Changes committed locally but not pushed.${NC}"
            fi
        fi
    else
        echo -e "${GREEN}No changes detected in $submodule_name${NC}"
    fi
    
    # Return to root directory
    cd "$ROOT_DIR"
    echo -e "${GREEN}=== Finished processing submodule: $submodule_name ===${NC}\n"
}

# Function to restore init_db.py before committing if needed
ensure_init_db_exists() {
    if [ -f "restore-persona-init.sh" ]; then
        echo -e "${YELLOW}Running restore-persona-init.sh to ensure init_db.py exists...${NC}"
        ./restore-persona-init.sh
    fi
}

# Main execution
echo -e "${BLUE}===== Committing Changes to Submodules and Main Repository =====${NC}"
echo -e "${YELLOW}This script will help you commit changes in the correct order${NC}"

# Ensure init_db.py exists
ensure_init_db_exists

# Process each submodule in order
echo -e "\n${BLUE}Starting with submodules first...${NC}"

# Agent module submodule
if [ -d "agent_module" ]; then
    commit_submodule "agent_module"
else
    echo -e "${YELLOW}agent_module directory not found, skipping...${NC}"
fi

# Persona service submodule
if [ -d "persona-service" ]; then
    commit_submodule "persona-service"
else
    echo -e "${YELLOW}persona-service directory not found, skipping...${NC}"
fi

# Persona client submodule
if [ -d "persona-client" ]; then
    commit_submodule "persona-client"
else
    echo -e "${YELLOW}persona-client directory not found, skipping...${NC}"
fi

# Finally, commit main repository
echo -e "\n${BLUE}=== Processing main repository ===${NC}"

# Check for changes
if ! git diff-index --quiet HEAD --; then
    # Changes exist
    echo -e "${YELLOW}Changes detected in main repository${NC}"
    
    # Show status
    git status
    
    # Ask for commit message
    echo -e "${YELLOW}Enter commit message for main repository (or 'skip' to skip):${NC}"
    read -p "> " commit_message
    
    if [ "$commit_message" = "skip" ]; then
        echo -e "${YELLOW}Skipping commit for main repository${NC}"
    else
        # Add all changes
        git add .
        
        # Commit changes
        git commit -m "$commit_message"
        
        # Push changes (ask first)
        echo -e "${YELLOW}Do you want to push changes to remote? (y/n)${NC}"
        read -p "> " push_choice
        
        if [ "$push_choice" = "y" ] || [ "$push_choice" = "Y" ]; then
            # Get current branch
            current_branch=$(git rev-parse --abbrev-ref HEAD)
            
            # Ensure our branch exists on remote before pushing
            if git ls-remote --heads origin $current_branch | grep -q $current_branch; then
                git push origin $current_branch
            else
                echo -e "${YELLOW}Branch $current_branch doesn't exist on remote.${NC}"
                echo -e "${YELLOW}Do you want to push and set upstream? (y/n)${NC}"
                read -p "> " setup_upstream
                
                if [ "$setup_upstream" = "y" ] || [ "$setup_upstream" = "Y" ]; then
                    git push --set-upstream origin $current_branch
                else
                    echo -e "${YELLOW}Changes committed locally but not pushed.${NC}"
                fi
            fi
        else
            echo -e "${YELLOW}Changes committed locally but not pushed.${NC}"
        fi
    fi
else
    echo -e "${GREEN}No changes detected in main repository${NC}"
fi

echo -e "\n${GREEN}===== Commit process completed =====${NC}"
echo -e "${YELLOW}Remember to verify the changes in your remote repositories${NC}"
