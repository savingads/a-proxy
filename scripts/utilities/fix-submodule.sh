#!/bin/bash

# Script to fix the submodule issue

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}==== Fixing Persona Service Submodule ====${NC}"

# Remove persona-service from Git index
echo -e "${YELLOW}Removing persona-service from Git index...${NC}"
git rm -rf --cached persona-service 2>/dev/null || true
rm -rf persona-service 2>/dev/null || true

# Add the submodule correctly
echo -e "${YELLOW}Adding persona-service as a submodule...${NC}"
git submodule add file:///home/chris/a-proxy/persona-service-backup persona-service

# Commit the changes
git add .gitmodules persona-service
git commit -m "Add normalized persona-service submodule"

echo -e "${GREEN}Submodule fix complete!${NC}"
echo -e "The submodule is now at ${YELLOW}persona-service${NC}"
echo
echo -e "To use the new submodule, run:"
echo -e "${GREEN}git submodule update --init --recursive${NC}"
