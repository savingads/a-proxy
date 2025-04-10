#!/usr/bin/env python3
"""
Quick test script to verify that the Persona API is working
"""
import requests
import json
import sys

BASE_URL = "http://localhost:5050/api/v1"

def test_create_persona():
    """Test creating a new persona via the API"""
    print("\n== Testing Persona Creation ==")
    
    persona_data = {
        "name": "Test Persona",
        "demographic": {
            "language": "en-US",
            "country": "US",
            "city": "San Francisco",
            "region": "CA",
            "latitude": 37.7749,
            "longitude": -122.4194
        },
        "psychographic": {
            "interests": ["technology", "travel"],
            "personal_values": ["privacy", "freedom"],
            "lifestyle": "Urban professional"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/personas", json=persona_data)
        response.raise_for_status()
        
        result = response.json()
        print(f"Created persona with ID: {result.get('id')}")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        return result.get('id')
    except requests.exceptions.RequestException as e:
        print(f"Error creating persona: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return None

def test_get_personas():
    """Test retrieving all personas via the API"""
    print("\n== Testing Persona Retrieval (List) ==")
    
    try:
        response = requests.get(f"{BASE_URL}/personas")
        response.raise_for_status()
        
        result = response.json()
        print(f"Found {len(result.get('personas', []))} personas")
        print(f"Response: {json.dumps(result, indent=2)}")
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving personas: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")

def test_get_persona(persona_id):
    """Test retrieving a specific persona via the API"""
    print(f"\n== Testing Persona Retrieval (ID: {persona_id}) ==")
    
    try:
        response = requests.get(f"{BASE_URL}/personas/{persona_id}")
        response.raise_for_status()
        
        result = response.json()
        print(f"Retrieved persona: {result.get('name')}")
        print(f"Response: {json.dumps(result, indent=2)}")
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving persona: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")

def test_update_persona(persona_id):
    """Test updating a persona via the API"""
    print(f"\n== Testing Persona Update (ID: {persona_id}) ==")
    
    update_data = {
        "name": "Updated Test Persona",
        "demographic": {
            "city": "New York",
            "region": "NY",
            "latitude": 40.7128,
            "longitude": -74.0060
        }
    }
    
    try:
        response = requests.put(f"{BASE_URL}/personas/{persona_id}", json=update_data)
        response.raise_for_status()
        
        result = response.json()
        print(f"Updated persona: {result.get('name')}")
        print(f"Response: {json.dumps(result, indent=2)}")
    except requests.exceptions.RequestException as e:
        print(f"Error updating persona: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")

def test_delete_persona(persona_id):
    """Test deleting a persona via the API"""
    print(f"\n== Testing Persona Deletion (ID: {persona_id}) ==")
    
    try:
        response = requests.delete(f"{BASE_URL}/personas/{persona_id}")
        response.raise_for_status()
        
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
    except requests.exceptions.RequestException as e:
        print(f"Error deleting persona: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")

def test_health():
    """Test the health endpoint"""
    print("\n== Testing Health Endpoint ==")
    
    try:
        response = requests.get("http://localhost:5050/health")
        response.raise_for_status()
        
        result = response.json()
        print(f"Health status: {result.get('status')}")
    except requests.exceptions.RequestException as e:
        print(f"Error checking health: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")

def main():
    """Run all tests"""
    print("=== Persona API Test ===")
    
    # Test health endpoint
    test_health()
    
    # Test creating a persona
    persona_id = test_create_persona()
    if not persona_id:
        print("Failed to create persona. Cannot continue with other tests.")
        return 1
    
    # Test retrieving all personas
    test_get_personas()
    
    # Test retrieving a specific persona
    test_get_persona(persona_id)
    
    # Test updating a persona
    test_update_persona(persona_id)
    
    # Test retrieving the updated persona
    test_get_persona(persona_id)
    
    # Test deleting the persona
    test_delete_persona(persona_id)
    
    # Verify the persona is deleted
    test_get_personas()
    
    print("\n=== All tests completed ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
