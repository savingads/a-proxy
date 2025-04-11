#!/bin/bash
# Clean up unused persona-service directories, keeping only the submodule

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}==== Cleaning up persona-service directories ====${NC}"
echo -e "This script will remove unused persona-service directories,"
echo -e "keeping only the 'persona-service-new' submodule."
echo 

# Check if we have the submodule
if [ ! -d "persona-service-new" ]; then
    echo -e "${RED}Submodule persona-service-new not found!${NC}"
    echo -e "Cannot proceed with cleanup. Please make sure the submodule is correctly set up."
    exit 1
fi

echo -e "${YELLOW}Directories to be removed:${NC}"
echo "  - persona-service-migrated"
echo "  - persona-service-repo"
echo 
echo -e "${YELLOW}Original persona-service directory will be kept for reference until we're sure the migration is complete.${NC}"
echo 
echo -e "${YELLOW}Files to be removed:${NC}"
echo "  - persona-service-README.md"
echo "  - persona-service-config.py"
echo "  - persona-service-docker-compose.yml"
echo "  - persona-service-env-example"
echo "  - persona-service-gitignore"
echo "  - persona-service-integration-guide.md"
echo "  - persona-service-repo-plan.md"
echo "  - persona-service-run.py"
echo 
echo -e "${YELLOW}Migration script will be kept for reference.${NC}"
echo "  - persona-service-migration.sh"
echo 

read -p "Do you want to proceed with cleanup? (y/n): " confirm
if [[ "$confirm" != "y" ]]; then
    echo -e "${RED}Cleanup aborted.${NC}"
    exit 0
fi

# Remove directories
echo -e "${YELLOW}Removing directories...${NC}"
rm -rf persona-service-migrated
rm -rf persona-service-repo

# Remove files
echo -e "${YELLOW}Removing files...${NC}"
rm -f persona-service-README.md
rm -f persona-service-config.py
rm -f persona-service-docker-compose.yml
rm -f persona-service-env-example
rm -f persona-service-gitignore
rm -f persona-service-integration-guide.md
rm -f persona-service-repo-plan.md
rm -f persona-service-run.py

echo -e "${GREEN}Cleanup complete!${NC}"
echo -e "Remaining persona-service directories:"
echo -e "  - ${GREEN}persona-service/${NC} (original)"
echo -e "  - ${GREEN}persona-service-new/${NC} (submodule)"
echo 
echo -e "You can safely delete the original persona-service directory once you've verified everything works with the submodule."
