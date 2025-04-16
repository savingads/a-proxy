#!/bin/bash

# Script to fix detached HEAD in submodules and commit changes

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Repository root directory
ROOT_DIR=$(pwd)

# Function to fix a detached HEAD in a submodule and commit changes
fix_submodule() {
    local submodule_path=$1
    local submodule_name=$(basename $submodule_path)
    
    echo -e "${BLUE}=== Fixing detached HEAD in submodule: $submodule_name ===${NC}"
    
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

    # Check if HEAD is detached
    if git symbolic-ref -q HEAD >/dev/null; then
        # We're on a branch
        local current_branch=$(git rev-parse --abbrev-ref HEAD)
        echo -e "${GREEN}Already on branch: $current_branch${NC}"
    else
        # We're in detached HEAD state
        echo -e "${YELLOW}Detached HEAD detected${NC}"
        
        # Get the current commit
        local current_commit=$(git rev-parse HEAD)
        echo -e "${YELLOW}Current commit: $current_commit${NC}"
        
        # Ask for branch name
        echo -e "${YELLOW}Enter branch name to create for $submodule_name (default: 'fixes'):${NC}"
        read -p "> " branch_name
        
        # Use default if empty
        if [ -z "$branch_name" ]; then
            branch_name="fixes"
        fi
        
        # Create and checkout the new branch
        echo -e "${YELLOW}Creating and checking out branch: $branch_name${NC}"
        git checkout -b $branch_name
        
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to create branch: $branch_name${NC}"
            cd "$ROOT_DIR"
            return 1
        fi
    fi
    
    # Check for changes
    if ! git diff-index --quiet HEAD -- || [ -n "$(git ls-files --others --exclude-standard)" ]; then
        # Changes exist (either modified or untracked files)
        echo -e "${YELLOW}Changes detected in $submodule_name${NC}"
        
        # Show status
        git status
        
        # Ask for commit message
        echo -e "${YELLOW}Enter commit message for $submodule_name (or 'skip' to skip):${NC}"
        read -p "> " commit_message
        
        if [ "$commit_message" = "skip" ]; then
            echo -e "${YELLOW}Skipping commit for $submodule_name${NC}"
        else
            # Git add all
            git add .
            
            # Commit changes
            git commit -m "$commit_message"
            
            # Push changes (ask first)
            echo -e "${YELLOW}Do you want to push changes to remote? (y/n)${NC}"
            read -p "> " push_choice
            
            if [ "$push_choice" = "y" ] || [ "$push_choice" = "Y" ]; then
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
        echo -e "${GREEN}No changes detected in $submodule_name${NC}"
    fi
    
    # Return to root directory
    cd "$ROOT_DIR"
    echo -e "${GREEN}=== Finished fixing submodule: $submodule_name ===${NC}\n"
}

# Function to update main repository references to submodules
update_main_repo() {
    echo -e "${BLUE}=== Updating main repository references to submodules ===${NC}"
    
    # Check for changes to submodule references
    if ! git diff-index --quiet HEAD -- || [ -n "$(git ls-files --others --exclude-standard)" ]; then
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
                
                git push origin $current_branch
            else
                echo -e "${YELLOW}Changes committed locally but not pushed.${NC}"
            fi
        fi
    else
        echo -e "${GREEN}No changes detected in main repository${NC}"
    fi
}

# Function to exclude database files from git
ignore_db_files() {
    if [ -d "persona-service" ]; then
        echo -e "${YELLOW}Adding database files to .gitignore in persona-service...${NC}"
        
        cd persona-service
        
        # Check if .gitignore exists
        if [ ! -f ".gitignore" ]; then
            echo -e "# Ignore database files\n*.db\n*.db-shm\n*.db-wal" > .gitignore
            echo -e "${GREEN}Created .gitignore with database exclusions${NC}"
        else
            # Check if db entries already exist
            if ! grep -q "*.db-shm" .gitignore && ! grep -q "*.db-wal" .gitignore; then
                echo -e "\n# Ignore database files\n*.db-shm\n*.db-wal" >> .gitignore
                echo -e "${GREEN}Added database exclusions to .gitignore${NC}"
            else
                echo -e "${GREEN}Database exclusions already in .gitignore${NC}"
            fi
        fi
        
        cd "$ROOT_DIR"
    fi
}

# Main execution
echo -e "${BLUE}===== Fixing Detached HEAD in Submodules and Committing Changes =====${NC}"
echo -e "${YELLOW}This script will help you fix detached HEADs and commit changes to branches${NC}"

# Ignore database files
ignore_db_files

# Fix agent_module submodule
if [ -d "agent_module" ]; then
    fix_submodule "agent_module"
else
    echo -e "${YELLOW}agent_module directory not found, skipping...${NC}"
fi

# Fix persona-service submodule
if [ -d "persona-service" ]; then
    fix_submodule "persona-service"
else
    echo -e "${YELLOW}persona-service directory not found, skipping...${NC}"
fi

# Update main repository
update_main_repo

echo -e "\n${GREEN}===== Submodule fix process completed =====${NC}"
echo -e "${YELLOW}Remember to verify the changes in your remote repositories${NC}"
