#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}====== A-Proxy Branch Merge Script ======${NC}"
echo -e "${BLUE}This script will merge developer branch into main${NC}"
echo ""

# Function to check if command executed successfully
check_success() {
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}Success!${NC}"
  else
    echo -e "${RED}Failed!${NC}"
    exit 1
  fi
}

# Function to prompt for confirmation
confirm() {
  read -p "$1 (y/n): " answer
  case ${answer:0:1} in
    y|Y )
      return 0
    ;;
    * )
      return 1
    ;;
  esac
}

# Check current branch
current_branch=$(git branch --show-current)
echo -e "Current branch: ${YELLOW}$current_branch${NC}"

# Ensure we have the latest changes
echo -e "\n${YELLOW}Fetching latest changes...${NC}"
git fetch
check_success

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}You have uncommitted changes.${NC}"
    git status
    
    if confirm "Would you like to commit these changes?"; then
        read -p "Enter commit message: " commit_message
        git add .
        git commit -m "$commit_message"
        check_success
    else
        echo -e "${RED}Please commit or stash your changes before merging.${NC}"
        exit 1
    fi
fi

# Make sure we're on developer branch
if [ "$current_branch" != "developer" ]; then
    echo -e "${YELLOW}Switching to developer branch...${NC}"
    git checkout developer
    check_success
    echo -e "${GREEN}Now on developer branch${NC}"
fi

# Pull latest changes on developer
echo -e "\n${YELLOW}Pulling latest changes for developer branch...${NC}"
git pull origin developer
check_success

# Create a tag of developer branch before merging
timestamp=$(date +%Y%m%d-%H%M%S)
tag_name="developer-pre-merge-$timestamp"
echo -e "\n${YELLOW}Creating tag: $tag_name${NC}"
git tag -a "$tag_name" -m "Developer branch before merging to main on $timestamp"
check_success

# Checkout main branch
echo -e "\n${YELLOW}Checking out main branch...${NC}"
git checkout main
check_success

# Pull latest changes on main to avoid conflicts
echo -e "\n${YELLOW}Pulling latest changes for main branch...${NC}"
git pull origin main
check_success

# Merge developer into main
echo -e "\n${YELLOW}Merging developer branch into main...${NC}"
if confirm "Would you like to continue with merging developer into main?"; then
    git merge developer
    check_success
    echo -e "${GREEN}Successfully merged developer into main${NC}"
else
    echo -e "${RED}Merge aborted.${NC}"
    git checkout "$current_branch"
    exit 1
fi

# Push changes to origin
echo -e "\n${YELLOW}Pushing changes to origin/main...${NC}"
if confirm "Would you like to push the changes to origin/main?"; then
    git push origin main
    check_success
    echo -e "${GREEN}Successfully pushed changes to origin/main${NC}"
else
    echo -e "${RED}Push aborted. Changes are only local.${NC}"
    echo -e "${YELLOW}You can push changes later with:${NC} git push origin main"
fi

# Switch back to original branch
echo -e "\n${YELLOW}Switching back to $current_branch branch...${NC}"
git checkout "$current_branch"
check_success

echo -e "\n${GREEN}====== Branch Merge Complete! ======${NC}"
echo -e "${BLUE}Developer branch has been merged into main.${NC}"
echo -e "${BLUE}A tag '$tag_name' has been created as a backup.${NC}"
echo -e "${BLUE}You can now proceed with deployment.${NC}"
