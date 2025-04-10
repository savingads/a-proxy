#!/usr/bin/env python3
"""
Test script using the Persona Client library directly
"""
import sys
import json
from personaclient import PersonaClient
from personaclient.exceptions import PersonaClientError

def main():
    """Test the Persona client library"""
    print("=== Testing Persona Client Library ===")
    
    # Create a client
    client = PersonaClient(base_url="http://localhost:5050")
    
    # Test creating a persona
    try:
        print("\nCreating test persona...")
        persona_data = {
            "name": "Client Library Test Persona",
            "demographic": {
                "language": "en-US",
                "country": "UK",
                "city": "London",
                "region": "England",
                "latitude": 51.5074,
                "longitude": -0.1278
            }
        }
        
        result = client.create_persona(persona_data)
        persona_id = result.get('id')
        print(f"Successfully created persona with ID: {persona_id}")
        
        # Test getting the persona
        print("\nRetrieving persona...")
        persona = client.get_persona(persona_id)
        print(f"Retrieved persona: {persona.get('name')}")
        
        # Test listing personas
        print("\nListing all personas...")
        results = client.get_all_personas()
        print(f"Found {len(results.get('personas', []))} personas")
        
        # Test deleting the persona
        print("\nDeleting persona...")
        delete_result = client.delete_persona(persona_id)
        print(f"Deleted persona: {delete_result.get('message')}")
        
        print("\n=== Tests completed successfully ===")
        return 0
        
    except PersonaClientError as e:
        print(f"Client error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
