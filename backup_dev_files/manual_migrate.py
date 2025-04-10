#!/usr/bin/env python3
"""
Simple script to manually migrate the sample personas to the API
"""
import requests
import json
import database

# API URL
API_URL = "http://localhost:5050/api/v1"

def get_personas_from_db():
    """Get all personas from the SQLite database"""
    return database.get_all_personas()

def create_persona_in_api(persona_data):
    """Create a persona in the API"""
    # Simplify the persona data to match API format
    # The API expects direct data structures, not JSON strings
    api_persona = {
        "name": persona_data["name"],
        "demographic": {}
    }
    
    # Add demographic data
    if "demographic" in persona_data:
        demo = persona_data["demographic"]
        api_persona["demographic"] = {
            "language": demo.get("language"),
            "country": demo.get("country"),
            "city": demo.get("city"),
            "region": demo.get("region"),
            "age": demo.get("age"),
            "gender": demo.get("gender"),
            "education": demo.get("education"),
            "income": demo.get("income"),
            "occupation": demo.get("occupation")
        }
        
        # Handle geolocation
        if "geolocation" in demo and demo["geolocation"]:
            try:
                lat, lng = demo["geolocation"].split(",")
                api_persona["demographic"]["latitude"] = float(lat)
                api_persona["demographic"]["longitude"] = float(lng)
            except (ValueError, AttributeError):
                pass
    
    # Add psychographic data
    if "psychographic" in persona_data:
        psycho = persona_data["psychographic"]
        api_persona["psychographic"] = {
            "interests": psycho.get("interests", []),
            "personal_values": psycho.get("personal_values", []),
            "attitudes": psycho.get("attitudes", []),
            "lifestyle": psycho.get("lifestyle"),
            "personality": psycho.get("personality"),
            "opinions": psycho.get("opinions", [])
        }
    
    # Add behavioral data
    if "behavioral" in persona_data:
        behav = persona_data["behavioral"]
        api_persona["behavioral"] = {
            "browsing_habits": behav.get("browsing_habits", []),
            "purchase_history": behav.get("purchase_history", []),
            "brand_interactions": behav.get("brand_interactions", []),
            "device_usage": behav.get("device_usage", {}),
            "social_media_activity": behav.get("social_media_activity", {}),
            "content_consumption": behav.get("content_consumption", {})
        }
    
    # Add contextual data
    if "contextual" in persona_data:
        context = persona_data["contextual"]
        api_persona["contextual"] = {
            "time_of_day": context.get("time_of_day"),
            "day_of_week": context.get("day_of_week"),
            "season": context.get("season"),
            "weather": context.get("weather"),
            "device_type": context.get("device_type"),
            "browser_type": context.get("browser_type"),
            "screen_size": context.get("screen_size"),
            "connection_type": context.get("connection_type")
        }
    
    # Send to API
    try:
        response = requests.post(
            f"{API_URL}/personas",
            json=api_persona,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        result = response.json()
        return True, result
    except Exception as e:
        print(f"Error creating persona {persona_data['name']}: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return False, None

def migrate_personas():
    """Migrate all personas from database to API"""
    # Get personas from database
    personas = get_personas_from_db()
    print(f"Found {len(personas)} personas in the database")
    
    # Migrate each persona
    success_count = 0
    fail_count = 0
    
    for persona in personas:
        print(f"Migrating persona: {persona['name']} (ID: {persona['id']})")
        success, result = create_persona_in_api(persona)
        
        if success:
            success_count += 1
            print(f"  Success! New API ID: {result['id']}")
        else:
            fail_count += 1
            print(f"  Failed to migrate")
    
    print(f"\nMigration completed: {success_count} succeeded, {fail_count} failed")

if __name__ == "__main__":
    migrate_personas()
