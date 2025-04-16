#!/bin/bash

# Script to add sample persona creation to the start-with-packages.sh script

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== UPDATING START-WITH-PACKAGES.SH SCRIPT =====${NC}"
echo -e "${YELLOW}This script will add sample persona creation functionality${NC}"

# Check if start-with-packages.sh exists
if [ ! -f "start-with-packages.sh" ]; then
  echo -e "${RED}start-with-packages.sh script doesn't exist!${NC}"
  exit 1
fi

# Create a temporary file
TEMP_FILE=$(mktemp)

# Function to check for the sample personas
ENSURE_SAMPLE_PERSONAS_FUNCTION='
# Function to ensure sample personas exist in the database
ensure_sample_personas() {
  echo -e "${YELLOW}Checking for sample personas...${NC}"
  
  # Check if curl command exists
  if ! command -v curl &> /dev/null; then
    echo -e "${RED}curl command could not be found. Cannot verify personas.${NC}"
    return 1
  fi
  
  # Try to get the list of personas from the API
  local RESPONSE=$(curl -s --connect-timeout 5 http://localhost:5050/api/v1/personas)
  
  # Check if the response contains empty data (no personas)
  if [[ $RESPONSE == *"\"data\":[]"* ]]; then
    echo -e "${YELLOW}No personas found in database, creating sample personas...${NC}"
    
    # Run the create-personas.py script to add sample personas
    echo -e "${YELLOW}Passing count=5 to create all 5 sample personas${NC}"
    python create-personas.py --api-url http://localhost:5050 --count 5
    
    # Check the result
    if [ $? -eq 0 ]; then
      echo -e "${GREEN}Sample personas created successfully${NC}"
    else
      echo -e "${RED}Failed to create sample personas${NC}"
    fi
  else
    echo -e "${GREEN}Sample personas already exist in the database${NC}"
  fi
}
'

# Find where to insert the function - before the trap cleanup line
if grep -q "trap cleanup" start-with-packages.sh; then
  # Get content before the trap line
  sed -n '1,/trap cleanup/p' start-with-packages.sh > "$TEMP_FILE"
  
  # Add the ensure_sample_personas function
  echo "$ENSURE_SAMPLE_PERSONAS_FUNCTION" >> "$TEMP_FILE"
  
  # Get content from the trap line to the end
  sed -n '/trap cleanup/,$p' start-with-packages.sh >> "$TEMP_FILE"
  
  # Replace the original file
  mv "$TEMP_FILE" start-with-packages.sh
  chmod +x start-with-packages.sh
else
  echo -e "${RED}Could not find 'trap cleanup' in start-with-packages.sh${NC}"
  rm "$TEMP_FILE"
  exit 1
fi

# Now add the call to ensure_sample_personas function
# Find where to insert the function call - after "sleep 5" and before "Start A-Proxy"
TEMP_FILE=$(mktemp)
if grep -q "Waiting for service to initialize" start-with-packages.sh; then
  # Get content before "sleep 5"
  sed -n '1,/sleep 5/p' start-with-packages.sh > "$TEMP_FILE"
  
  # Add a call to the ensure_sample_personas function
  echo -e "\n# Ensure sample personas exist in the database\nensure_sample_personas\n" >> "$TEMP_FILE"
  
  # Get content after "sleep 5" to the end
  sed -n '/sleep 5/,$p' start-with-packages.sh | sed '1d' >> "$TEMP_FILE"
  
  # Replace the original file
  mv "$TEMP_FILE" start-with-packages.sh
  chmod +x start-with-packages.sh
else
  echo -e "${RED}Could not find 'Waiting for service to initialize' in start-with-packages.sh${NC}"
  rm "$TEMP_FILE"
  exit 1
fi

echo -e "\n${GREEN}===== START-WITH-PACKAGES.SH UPDATED =====${NC}"
echo -e "${YELLOW}Sample persona creation functionality has been added${NC}"
echo -e "${YELLOW}Now when you run start-with-packages.sh, it will check for and create sample personas if needed${NC}"
