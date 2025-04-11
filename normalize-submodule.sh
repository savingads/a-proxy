#!/bin/bash

# Script to normalize the persona-service submodule naming

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the repo root
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Please run this script from the repository root directory.${NC}"
    exit 1
fi

echo -e "${YELLOW}==== Normalizing Persona Service Submodule ====${NC}"

# Check the current state
if [ ! -d "persona-service-new" ]; then
    echo -e "${RED}persona-service-new directory doesn't exist!${NC}"
    exit 1
fi

# Step 1: Backup the content of persona-service-new
echo -e "${YELLOW}Backing up persona-service-new content...${NC}"
mkdir -p persona-service-backup
cp -r persona-service-new/* persona-service-backup/ 2>/dev/null || true
cp -r persona-service-new/.env* persona-service-backup/ 2>/dev/null || true
cp -r persona-service-new/.git* persona-service-backup/ 2>/dev/null || true

# Step 2: Remove the existing submodule configuration if it exists
echo -e "${YELLOW}Removing existing submodule configuration...${NC}"
git submodule deinit -f persona-service-new 2>/dev/null || true
git rm -f persona-service-new 2>/dev/null || true
rm -rf .git/modules/persona-service-new 2>/dev/null || true
git config -f .gitmodules --remove-section submodule.persona-service-new 2>/dev/null || true
git add .gitmodules 2>/dev/null || true
git commit -m "Remove persona-service-new submodule" 2>/dev/null || true

# Step 3: Remove old directories
echo -e "${YELLOW}Backing up original persona-service directory...${NC}"
if [ -d "persona-service" ]; then
    mkdir -p persona-service-original-backup
    cp -r persona-service/* persona-service-original-backup/ 2>/dev/null || true
    echo -e "${YELLOW}Removing old persona-service directory...${NC}"
    rm -rf persona-service
fi

# Step 4: Initialize a local git repository in persona-service-backup
echo -e "${YELLOW}Setting up local git repository for persona-service...${NC}"
cd persona-service-backup
rm -rf .git* 2>/dev/null || true
git init
git add .
git config user.email "admin@example.com"
git config user.name "Administrator"
git commit -m "Initial commit of persona-service"
cd ..

# Step 5: Add the new submodule
echo -e "${YELLOW}Adding persona-service as a submodule...${NC}"
git submodule add file:///home/chris/a-proxy/persona-service-backup persona-service
git add .gitmodules persona-service
git commit -m "Add normalized persona-service submodule" || true

# Step 6: Update references in scripts
echo -e "${YELLOW}Updating references in scripts...${NC}"
SCRIPT_FILES=$(find . -type f -name "*.sh" -o -name "*.py" 2>/dev/null | xargs grep -l "persona-service-new" 2>/dev/null || true)
if [ -n "$SCRIPT_FILES" ]; then
    for file in $SCRIPT_FILES; do
        echo "Updating $file"
        sed -i 's/persona-service-new/persona-service/g' "$file"
    done

    # Commit the changes
    git add .
    git commit -m "Update script references to use normalized persona-service path" || true
else
    echo "No script files found that reference persona-service-new"
fi

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Persona Service submodule normalized!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo
echo -e "The original files are backed up in:"
echo -e "- ${YELLOW}persona-service-backup${NC} (from persona-service-new)"
if [ -d "persona-service-original-backup" ]; then
    echo -e "- ${YELLOW}persona-service-original-backup${NC} (from original persona-service)"
fi
echo -e "The submodule is now at ${YELLOW}persona-service${NC}"
echo
echo -e "To use the new submodule, run:"
echo -e "${GREEN}git submodule update --init --recursive${NC}"
