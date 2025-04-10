#!/usr/bin/env python3
"""
Script to create a test persona via the API
and show it was successfully created
"""
import requests
import sys
import json

# API URL
API_URL = "http://localhost:5050/api/v1"

def create_test_persona():
    """Create a test persona for integration testing"""
    print("Creating test persona via the API...")
    
    # Simplified persona data
    persona_data = {
        "name": "Integration Test Persona",
        "demographic": {
            "language": "fr-FR",
            "country": "France",
            "city": "Paris",
            "region": "Île-de-France",
            "latitude": 48.8566,
            "longitude": 2.3522
        }
    }
    
    try:
        response = requests.post(f"{API_URL}/personas", json=persona_data)
        response.raise_for_status()
        result = response.json()
        print(f"Successfully created persona with ID: {result.get('id')}")
        return result.get('id')
    except Exception as e:
        print(f"Error creating persona: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return None

def verify_persona_in_api(persona_id):
    """Verify the persona exists in the API"""
    print(f"\nVerifying persona {persona_id} exists in the API...")
    
    try:
        response = requests.get(f"{API_URL}/personas/{persona_id}")
        response.raise_for_status()
        persona = response.json()
        print(f"Found persona: {persona.get('name')}")
        return True
    except Exception as e:
        print(f"Error retrieving persona: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return False

def verify_persona_in_app():
    """Verify the persona is visible in the A-Proxy application"""
    print("\nChecking personas in the A-Proxy application...")
    
    try:
        # First get the personas list page
        response = requests.get("http://localhost:5002/personas")
        response.raise_for_status()
        
        # This is a basic check - just see if our persona name is in the HTML
        if "Integration Test Persona" in response.text:
            print("✅ Persona found in the A-Proxy app interface!")
            return True
        else:
            print("❌ Persona NOT found in the A-Proxy app interface")
            return False
    except Exception as e:
        print(f"Error checking A-Proxy app: {e}")
        return False

def main():
    """Main function to test API integration"""
    print("=== Testing A-Proxy Integration with Persona API ===\n")
    
    # Create a test persona through the API
    persona_id = create_test_persona()
    if not persona_id:
        print("Failed to create test persona")
        return 1
    
    # Verify the persona exists in the API
    if not verify_persona_in_api(persona_id):
        print("Failed to verify persona in API")
        return 1
    
    # Verify the persona is visible in the A-Proxy app
    if not verify_persona_in_app():
        print("Failed to verify persona in A-Proxy app")
        return 1
    
    print("\n=== Integration Test Successful! ===")
    print("""
The persona was:
1. Created through the API
2. Retrieved from the API
3. Visible in the A-Proxy web interface

This confirms that the API-based architecture is working correctly.
""")
    return 0

if __name__ == "__main__":
    sys.exit(main())
