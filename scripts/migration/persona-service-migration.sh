#!/bin/bash
# Script to migrate the persona-service to its own repository

set -e  # Exit on any error

# Configuration
NEW_REPO_NAME="persona-service-migrated"
GITHUB_USERNAME="your-github-username"
SOURCE_DIR="./persona-service"
TARGET_DIR="./$NEW_REPO_NAME"  # Keep it in current directory for demo
DEMO_MODE=true  # Set to true to run in demo mode (skip interactive prompts)

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}==== Persona Service Migration Script ====${NC}"
echo -e "This script will move the persona-service from your current project to a standalone repository."
echo -e "Make sure you have Git installed and GitHub CLI (gh) if you want to create the repository on GitHub."
echo -e "Current source directory: ${GREEN}$SOURCE_DIR${NC}"
echo -e "Target directory: ${GREEN}$TARGET_DIR${NC}"
echo ""

# Skip prompt if in demo mode
if [ "$DEMO_MODE" != "true" ]; then
    read -p "Press Enter to continue or Ctrl+C to abort..."
fi

# Step 1: Create the new repository directory
echo -e "\n${YELLOW}Step 1: Creating new repository directory${NC}"
if [ -d "$TARGET_DIR" ]; then
    echo -e "${RED}Target directory already exists. Removing in demo mode...${NC}"
    if [ "$DEMO_MODE" == "true" ]; then
        rm -rf "$TARGET_DIR"
    else
        echo -e "${RED}Please backup or remove it first.${NC}"
        exit 1
    fi
fi
mkdir -p "$TARGET_DIR"
mkdir -p "$TARGET_DIR/app"
mkdir -p "$TARGET_DIR/data"
mkdir -p "$TARGET_DIR/tests"
touch "$TARGET_DIR/data/.gitkeep"
echo -e "${GREEN}Created directory structure${NC}"

# Step 2: Copy core files from the original persona-service
echo -e "\n${YELLOW}Step 2: Copying core files${NC}"
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}Source directory does not exist. Creating sample structure for demo.${NC}"
    # In demo mode, create a minimal sample structure
    if [ "$DEMO_MODE" == "true" ]; then
        mkdir -p "$SOURCE_DIR/app"
        touch "$SOURCE_DIR/app/__init__.py"
        touch "$SOURCE_DIR/Dockerfile"
        echo "flask==2.3.2" > "$SOURCE_DIR/requirements.txt"
    else
        exit 1
    fi
fi

cp -r "$SOURCE_DIR/app/"* "$TARGET_DIR/app/" || echo -e "${YELLOW}Warning: No files to copy from app directory${NC}"
cp "$SOURCE_DIR/Dockerfile" "$TARGET_DIR/" || echo -e "${YELLOW}Warning: Dockerfile not found${NC}"
cp "$SOURCE_DIR/requirements.txt" "$TARGET_DIR/" || echo -e "${YELLOW}Warning: requirements.txt not found${NC}"

# If there are tests, copy them too
if [ -d "$SOURCE_DIR/tests" ]; then
    cp -r "$SOURCE_DIR/tests/"* "$TARGET_DIR/tests/"
fi

echo -e "${GREEN}Copied core files${NC}"

# Step 3: Creating new files directly
echo -e "\n${YELLOW}Step 3: Creating new files directly${NC}"

# Instead of copying files, let's create them directly
cat > "$TARGET_DIR/README.md" << 'EOF'
# Persona Service

A standalone API service for managing user personas with demographic, psychographic, behavioral, and contextual attributes.

## Overview

The Persona Service provides a flexible and powerful API for creating and managing user personas. It supports a dynamic schema that allows for a wide range of persona attributes without requiring database schema changes.

### Features

- **Dynamic Schema**: Add fields without database migrations
- **Rich Persona Data**: Support for demographic, psychographic, behavioral, and contextual attributes
- **RESTful API**: Clean API endpoints for CRUD operations
- **Flexible Integration**: Use directly via API or with the included client library
- **Docker Support**: Easy deployment with Docker
EOF

# Create .env.example file
cat > "$TARGET_DIR/.env.example" << 'EOF'
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1

# Database Configuration
DATABASE_URI=sqlite:///data/persona_service.db

# Authentication
JWT_SECRET_KEY=change-this-to-a-random-secret-key
JWT_ACCESS_TOKEN_HOURS=1
JWT_REFRESH_TOKEN_DAYS=30

# CORS settings
CORS_ORIGINS=http://localhost:3000,http://localhost:5000
EOF

# Create docker-compose.yml file
cat > "$TARGET_DIR/docker-compose.yml" << 'EOF'
version: '3.8'

services:
  persona-service:
    build: .
    ports:
      - "5050:5050"
    volumes:
      - ./data:/app/data
    environment:
      - FLASK_APP=run.py
      - FLASK_ENV=development
      - DATABASE_URI=sqlite:///data/persona_service.db
      - JWT_SECRET_KEY=${JWT_SECRET_KEY:-dev-secret-key}
    command: gunicorn --bind 0.0.0.0:5050 --workers 2 "app:create_app()"
EOF

# Create run.py file
cat > "$TARGET_DIR/run.py" << 'EOF'
#!/usr/bin/env python3
"""
Entry point for running the Persona Service
"""
import argparse
from app import create_app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Persona Service API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=5050, help="Port to run the server on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")

    args = parser.parse_args()

    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)
EOF

# Create .gitignore file
cat > "$TARGET_DIR/.gitignore" << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/

# Database
*.db
*.db-shm
*.db-wal
data/*
!data/.gitkeep

# Environment variables
.env
EOF

# Create a basic integration document
cat > "$TARGET_DIR/INTEGRATION.md" << 'EOF'
# Persona Service Integration Guide

This guide explains how to integrate the Persona Service into your applications.

## REST API Integration

You can make direct HTTP requests to the Persona Service API endpoints.

```python
import requests

def get_personas(base_url="http://localhost:5050"):
    response = requests.get(f"{base_url}/api/v1/personas")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get personas: {response.text}")
```

## Python Client Library

For Python applications, you can use the provided client library.

```python
from personaclient import PersonaClient

client = PersonaClient(base_url="http://localhost:5050")
personas = client.get_all_personas()
```
EOF

# Ensure config.py is updated with environment variable support
cat > "$TARGET_DIR/app/config.py" << 'EOF'
"""
Configuration for the Persona Service API
"""
import os
from datetime import timedelta

# Database URI
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///data/persona_service.db")

# JWT Authentication settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_ACCESS_TOKEN_HOURS", "1")))
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_DAYS", "30")))

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
EOF

echo -e "${GREEN}Created new files directly${NC}"

# Fix the permissions for executable files
chmod +x "$TARGET_DIR/run.py"

echo -e "${GREEN}Created new files${NC}"

# Step 4: Fix missing dependencies in requirements.txt
echo -e "\n${YELLOW}Step 4: Updating requirements.txt${NC}"

# Ensure requirements.txt exists
if [ ! -f "$TARGET_DIR/requirements.txt" ]; then
    echo "# Generated requirements.txt" > "$TARGET_DIR/requirements.txt"
    echo "flask==2.3.2" >> "$TARGET_DIR/requirements.txt"
fi

if ! grep -q "flask-cors" "$TARGET_DIR/requirements.txt"; then
    echo "flask-cors==4.0.0" >> "$TARGET_DIR/requirements.txt"
    echo -e "${GREEN}Added flask-cors to requirements.txt${NC}"
fi

if ! grep -q "python-dotenv" "$TARGET_DIR/requirements.txt"; then
    echo "python-dotenv==1.0.0" >> "$TARGET_DIR/requirements.txt"
    echo -e "${GREEN}Added python-dotenv to requirements.txt${NC}"
fi

# Step 5: Initialize git repository
echo -e "\n${YELLOW}Step 5: Initializing Git repository${NC}"
cd "$TARGET_DIR"
git init
git add .
git commit -m "Initial commit: Migrated persona-service to standalone repository"
echo -e "${GREEN}Git repository initialized${NC}"

# Step 6: Create GitHub repo (optional) - skip in demo mode
echo -e "\n${YELLOW}Step 6: Create GitHub repository (optional)${NC}"
if [ "$DEMO_MODE" == "true" ]; then
    echo -e "${YELLOW}Skipping GitHub repo creation in demo mode${NC}"
else
    read -p "Do you want to create a GitHub repository? (y/n): " create_github_repo
    if [ "$create_github_repo" = "y" ]; then
        if command -v gh &> /dev/null; then
            echo -e "Creating GitHub repository: ${GREEN}$GITHUB_USERNAME/$NEW_REPO_NAME${NC}"
            read -p "Enter repository description: " repo_description
            gh repo create "$GITHUB_USERNAME/$NEW_REPO_NAME" --description "$repo_description" --public
            git remote add origin "https://github.com/$GITHUB_USERNAME/$NEW_REPO_NAME.git"
            git push -u origin main || git push -u origin master
            echo -e "${GREEN}GitHub repository created and code pushed${NC}"
        else
            echo -e "${RED}GitHub CLI (gh) not found. Please install it to create GitHub repositories.${NC}"
            echo -e "You can manually create a GitHub repository and push your code:"
            echo -e "git remote add origin https://github.com/$GITHUB_USERNAME/$NEW_REPO_NAME.git"
            echo -e "git push -u origin main"
        fi
    fi
fi

# Step 7: List files in the new repository
echo -e "\n${YELLOW}Step 7: Repository Structure${NC}"
echo -e "Files in the new repository:"
find . -type f | sort

# Step 8: Provide setup instructions
echo -e "\n${YELLOW}Step 8: Setup Instructions${NC}"
echo -e "The persona-service repository has been created at: ${GREEN}$TARGET_DIR${NC}"
echo -e "\nTo get started:"
echo -e "1. ${GREEN}cd $TARGET_DIR${NC}"
echo -e "2. ${GREEN}python -m venv venv${NC}"
echo -e "3. ${GREEN}source venv/bin/activate${NC}  # On Windows: venv\\Scripts\\activate"
echo -e "4. ${GREEN}pip install -r requirements.txt${NC}"
echo -e "5. ${GREEN}cp .env.example .env${NC}  # Edit with your configuration"
echo -e "6. ${GREEN}python run.py${NC}"
echo -e "\nThe service will be available at http://localhost:5050"
echo -e "\n${GREEN}Migration complete!${NC}"

# Return to original directory
cd - > /dev/null
