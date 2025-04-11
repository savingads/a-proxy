#!/usr/bin/env python3
"""
Simple script to recreate basic personas directly via the API
"""
import requests
import json

# API URL
API_URL = "http://localhost:5050/api/v1"

def create_persona(name, language, country, city, lat, lng):
    """Create a basic persona with minimal information"""
    # Create simple persona data
    persona_data = {
        "name": name,
        "demographic": {
            "language": language,
            "country": country,
            "city": city,
            "latitude": lat,
            "longitude": lng
        }
    }
    
    # Send to API
    try:
        print(f"Creating persona: {name}")
        response = requests.post(
            f"{API_URL}/personas",
            json=persona_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        result = response.json()
        print(f"  Success! New ID: {result.get('id')}")
        return True
    except Exception as e:
        print(f"  Error: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"  Response: {e.response.text}")
        return False

def main():
    """Create all sample personas"""
    # Create the 5 sample personas with basic information
    personas = [
        {
            "name": "Alex Johnson",
            "language": "en-US",
            "country": "US",
            "city": "San Francisco",
            "lat": 37.7749,
            "lng": -122.4194
        },
        {
            "name": "Isabela Santos",
            "language": "pt-BR",
            "country": "BR",
            "city": "São Paulo",
            "lat": -23.5505,
            "lng": -46.6333
        },
        {
            "name": "Lukas Schmidt",
            "language": "de-DE",
            "country": "DE",
            "city": "Berlin",
            "lat": 52.5200,
            "lng": 13.4050
        },
        {
            "name": "Yuki Tanaka",
            "language": "ja-JP",
            "country": "JP",
            "city": "Tokyo",
            "lat": 35.6762,
            "lng": 139.6503
        },
        {
            "name": "Thabo Ndlovu",
            "language": "en-ZA",
            "country": "ZA",
            "city": "Johannesburg",
            "lat": -26.2041,
            "lng": 28.0473
        }
    ]
    
    # Create each persona
    success_count = 0
    for p in personas:
        success = create_persona(
            p["name"], 
            p["language"], 
            p["country"], 
            p["city"], 
            p["lat"], 
            p["lng"]
        )
        if success:
            success_count += 1
    
    print(f"\nCreated {success_count} of {len(personas)} personas")

if __name__ == "__main__":
    main()
