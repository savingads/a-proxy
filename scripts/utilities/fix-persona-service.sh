#!/bin/bash

# Script to fix the persona-service submodule by checking out the develop branch

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== Fixing persona-service submodule =====${NC}"
echo -e "${YELLOW}This script will check out the develop branch for the persona-service submodule${NC}"

# Check if the persona-service directory exists
if [ ! -d "persona-service" ]; then
    echo -e "${RED}persona-service directory doesn't exist!${NC}"
    exit 1
fi

# Initialize and update the submodule
echo -e "${YELLOW}Initializing and updating persona-service submodule...${NC}"
git submodule update --init persona-service

# Navigate to the submodule directory
cd persona-service

# Check which branch we're on
echo -e "${YELLOW}Current branch or commit:${NC}"
git status

# Check out the develop branch
echo -e "${YELLOW}Attempting to checkout develop branch...${NC}"
git checkout develop

# Check if the checkout was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Successfully checked out develop branch for persona-service${NC}"
    git status
else
    echo -e "${RED}Failed to checkout develop branch${NC}"
    
    # List available branches
    echo -e "${YELLOW}Available branches:${NC}"
    git branch -a
    
    # Try to create the branch if it doesn't exist
    echo -e "${YELLOW}Attempting to create develop branch from current commit...${NC}"
    git checkout -b develop
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Created and checked out develop branch${NC}"
    else
        echo -e "${RED}Failed to create develop branch${NC}"
    fi
fi

# Make sure init_db.py exists
echo -e "${YELLOW}Ensuring init_db.py script exists...${NC}"
if [ ! -f "init_db.py" ]; then
    echo -e "${YELLOW}Creating init_db.py script...${NC}"
    cat > "init_db.py" << 'EOF'
#!/usr/bin/env python3
"""
Database initialization script for the Persona Service
"""
import os
import sys
from pathlib import Path

# Ensure the data directory exists
data_dir = Path(__file__).resolve().parent / 'data'
data_dir.mkdir(exist_ok=True)

# Import initialization function from models
from app.models import init_db
from app.config import SQLALCHEMY_DATABASE_URI

def main():
    print("Starting database initialization...")
    print(f"Initializing database with URI: {SQLALCHEMY_DATABASE_URI}")
    
    # Initialize the database
    session = init_db()
    
    # Check if tables were created
    from sqlalchemy import inspect
    inspector = inspect(session.bind)
    tables = inspector.get_table_names()
    print(f"Existing tables: {' '.join(tables)}")
    
    # Close session
    session.close()
    
    print("Database initialized successfully!")

if __name__ == "__main__":
    main()
EOF
    chmod +x "init_db.py"
    echo -e "${GREEN}Created init_db.py script${NC}"
else
    echo -e "${GREEN}init_db.py script already exists${NC}"
fi

# Ensure data directory exists
echo -e "${YELLOW}Ensuring data directory exists...${NC}"
mkdir -p data
chmod 755 data

# Make sure database files are ignored
echo -e "${YELLOW}Ensuring database files are ignored in .gitignore...${NC}"
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

# Add changes if any
if ! git diff-index --quiet HEAD -- || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    echo -e "${YELLOW}Changes detected in persona-service, adding to git...${NC}"
    git add .
    
    # Ask for commit message
    echo -e "${YELLOW}Enter commit message for persona-service (or 'skip' to skip):${NC}"
    read -p "> " commit_message
    
    if [ "$commit_message" = "skip" ]; then
        echo -e "${YELLOW}Skipping commit for persona-service${NC}"
    else
        # Commit changes
        git commit -m "$commit_message"
        
        # Push changes (ask first)
        echo -e "${YELLOW}Do you want to push changes to remote? (y/n)${NC}"
        read -p "> " push_choice
        
        if [ "$push_choice" = "y" ] || [ "$push_choice" = "Y" ]; then
            # Ensure our branch exists on remote before pushing
            if git ls-remote --heads origin develop | grep -q develop; then
                git push origin develop
            else
                echo -e "${YELLOW}Branch develop doesn't exist on remote.${NC}"
                echo -e "${YELLOW}Do you want to push and set upstream? (y/n)${NC}"
                read -p "> " setup_upstream
                
                if [ "$setup_upstream" = "y" ] || [ "$setup_upstream" = "Y" ]; then
                    git push --set-upstream origin develop
                else
                    echo -e "${YELLOW}Changes committed locally but not pushed.${NC}"
                fi
            fi
        else
            echo -e "${YELLOW}Changes committed locally but not pushed.${NC}"
        fi
    fi
else
    echo -e "${GREEN}No changes detected in persona-service${NC}"
fi

# Return to the root directory
cd ..

# Now commit the submodule reference change in the main repository
echo -e "${YELLOW}Do you want to add and commit this submodule change? (y/n)${NC}"
read -p "> " commit_choice

if [ "$commit_choice" = "y" ] || [ "$commit_choice" = "Y" ]; then
    git add persona-service
    git commit -m "Update persona-service submodule to develop branch"
    
    echo -e "${YELLOW}Do you want to push this change? (y/n)${NC}"
    read -p "> " push_choice
    
    if [ "$push_choice" = "y" ] || [ "$push_choice" = "Y" ]; then
        git push
    fi
fi

echo -e "${GREEN}===== persona-service submodule fix completed =====${NC}"
