#!/bin/bash

# Script to fix the sample persona creation and forcibly create samples

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== FIXING SAMPLE PERSONA CREATION =====${NC}"

# Repository root directory
ROOT_DIR=$(pwd)

# First check if the API is responsive
echo -e "${YELLOW}Checking if the Persona API is running...${NC}"
RESPONSE=$(curl -s --connect-timeout 5 http://localhost:5050)
if [ $? -ne 0 ]; then
    echo -e "${RED}Cannot connect to the Persona API. Make sure it's running.${NC}"
    echo -e "${YELLOW}Start the API with ./start-with-packages.sh in another terminal${NC}"
    exit 1
fi

# Check for the create-personas.py script
if [ ! -f "create-personas.py" ]; then
    echo -e "${RED}The create-personas.py script doesn't exist!${NC}"
    exit 1
fi

# Check the persona API for existing personas
echo -e "${YELLOW}Checking existing personas from API...${NC}"
PERSONA_RESPONSE=$(curl -s --connect-timeout 5 http://localhost:5050/api/v1/personas)
echo -e "API Response: $PERSONA_RESPONSE"

# Force creation of sample personas
echo -e "${YELLOW}Forcibly creating sample personas...${NC}"
echo -e "${YELLOW}Running create-personas.py with API URL...${NC}"

# Run with --reset to clear existing personas and recreate them
python create-personas.py --api-url http://localhost:5050 --count 5 --reset

# Check the result
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Sample personas created successfully${NC}"
else
    echo -e "${RED}Failed to create sample personas${NC}"
    echo -e "${YELLOW}Checking create-personas.py for API compatibility...${NC}"
    
    # Look for API URL usage in the script
    if grep -q "api_url" create-personas.py; then
        echo -e "${GREEN}create-personas.py appears to support API URLs${NC}"
    else
        echo -e "${RED}create-personas.py might not support API URLs${NC}"
        echo -e "${YELLOW}You may need to modify the script to use the API${NC}"
    fi
    
    # Check for direct database access
    if grep -q "sqlite" create-personas.py; then
        echo -e "${YELLOW}create-personas.py appears to use direct database access${NC}"
        echo -e "${YELLOW}Creating a modified version that uses the API...${NC}"
        
        # Create a modified version that ensures API usage
        cat > create-personas-api.py << 'EOF'
#!/usr/bin/env python3
"""
Script to create sample personas using the Persona API
"""
import argparse
import json
import random
import requests
import sys

def create_sample_persona(api_url, index=0):
    """Create a sample persona using the API"""
    # Sample persona data
    sample_names = ["Alex Thompson", "Jordan Lee", "Taylor Smith", "Morgan Chen", "Casey Williams"]
    sample_interests = [
        ["Technology", "Science Fiction", "Hiking"],
        ["Art", "Music", "Cooking"],
        ["Sports", "Fitness", "Travel"],
        ["Reading", "Writing", "Photography"],
        ["Gaming", "Movies", "Social Media"]
    ]
    sample_locations = [
        {"city": "New York", "country": "USA", "latitude": 40.7128, "longitude": -74.0060},
        {"city": "London", "country": "UK", "latitude": 51.5074, "longitude": -0.1278},
        {"city": "Tokyo", "country": "Japan", "latitude": 35.6762, "longitude": 139.6503},
        {"city": "Sydney", "country": "Australia", "latitude": -33.8688, "longitude": 151.2093},
        {"city": "Berlin", "country": "Germany", "latitude": 52.5200, "longitude": 13.4050}
    ]
    sample_ages = [25, 32, 45, 19, 38]
    sample_occupations = ["Software Engineer", "Artist", "Marketing Manager", "Student", "Chef"]
    
    # Use index to get consistent sample data
    idx = index % 5
    
    # Create persona data
    persona_data = {
        "name": sample_names[idx],
        "attributes": {
            "age": sample_ages[idx],
            "occupation": sample_occupations[idx],
            "interests": sample_interests[idx]
        },
        "demographic_data": {
            "location": sample_locations[idx]
        }
    }
    
    # Make API request to create persona
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{api_url}/personas", json=persona_data, headers=headers)
    
    if response.status_code == 201:
        created_persona = response.json()
        print(f"Created persona: {created_persona.get('name')}")
        return created_persona
    else:
        print(f"Failed to create persona: {response.text}")
        return None

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Create sample personas using the Persona API")
    parser.add_argument("--api-url", required=True, help="Persona API URL (e.g., http://localhost:5050/api/v1)")
    parser.add_argument("--count", type=int, default=5, help="Number of sample personas to create")
    parser.add_argument("--force", action="store_true", help="Force creation even if personas exist")
    args = parser.parse_args()
    
    # Ensure API URL has the correct format
    api_url = args.api_url.rstrip("/")
    if not api_url.endswith("/api/v1"):
        api_url += "/api/v1"
    
    # Check if personas already exist
    if not args.force:
        try:
            response = requests.get(f"{api_url}/personas")
            if response.status_code == 200 and response.json().get("data") and len(response.json()["data"]) > 0:
                print("Personas already exist. Use --force to create anyway.")
                return 0
        except Exception as e:
            print(f"Error checking existing personas: {e}")
    
    # Create sample personas
    success_count = 0
    for i in range(args.count):
        if create_sample_persona(api_url, i):
            success_count += 1
    
    print(f"Created {success_count} out of {args.count} requested personas")
    return 0 if success_count == args.count else 1

if __name__ == "__main__":
    sys.exit(main())
EOF
        chmod +x create-personas-api.py
        
        echo -e "${YELLOW}Running the API-compatible script...${NC}"
        python create-personas-api.py --api-url http://localhost:5050 --force
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}Successfully created sample personas with the API-compatible script${NC}"
        else
            echo -e "${RED}Failed to create sample personas with the API-compatible script${NC}"
        fi
    fi
fi

# Verify personas exist
echo -e "${YELLOW}Verifying personas were created...${NC}"
PERSONA_RESPONSE=$(curl -s --connect-timeout 5 http://localhost:5050/api/v1/personas)
if [[ $PERSONA_RESPONSE == *"\"data\":[]"* ]]; then
    echo -e "${RED}No personas found in the database after creation attempt${NC}"
else
    echo -e "${GREEN}Personas now exist in the database!${NC}"
    echo -e "API Response: $PERSONA_RESPONSE"
fi

echo -e "\n${GREEN}===== PERSONA CREATION FIX COMPLETED =====${NC}"
echo -e "${YELLOW}If you still don't see personas in the web interface, try refreshing the page${NC}"
