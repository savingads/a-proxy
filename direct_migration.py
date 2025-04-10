#!/usr/bin/env python3
"""
Direct migration script that uses the API server format directly
"""
import requests
import json
import sqlite3
import os
from datetime import datetime

# API URL
API_URL = "http://localhost:5050/api/v1"
DB_PATH = "data/personas.db"

def get_persona_from_db(persona_id):
    """Get a specific persona directly from the database"""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database file not found: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Get the main persona record
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM personas WHERE id = ?", (persona_id,))
    persona_row = cursor.fetchone()
    
    if not persona_row:
        conn.close()
        return None
    
    # Convert to dict
    persona = dict(persona_row)
    
    # Get demographic data
    cursor.execute("SELECT * FROM demographic_data WHERE persona_id = ?", (persona_id,))
    demo_row = cursor.fetchone()
    if demo_row:
        persona["demographic"] = dict(demo_row)
    
    # Get psychographic data
    cursor.execute("SELECT * FROM psychographic_data WHERE persona_id = ?", (persona_id,))
    psycho_row = cursor.fetchone()
    if psycho_row:
        persona["psychographic"] = dict(psycho_row)
        
        # Parse JSON fields
        for field in ["interests", "personal_values", "attitudes", "opinions"]:
            if field in persona["psychographic"] and persona["psychographic"][field]:
                try:
                    persona["psychographic"][field] = json.loads(persona["psychographic"][field])
                except:
                    persona["psychographic"][field] = []
    
    # Get behavioral data
    cursor.execute("SELECT * FROM behavioral_data WHERE persona_id = ?", (persona_id,))
    behav_row = cursor.fetchone()
    if behav_row:
        persona["behavioral"] = dict(behav_row)
        
        # Parse JSON fields
        for field in ["browsing_habits", "purchase_history", "brand_interactions"]:
            if field in persona["behavioral"] and persona["behavioral"][field]:
                try:
                    persona["behavioral"][field] = json.loads(persona["behavioral"][field])
                except:
                    persona["behavioral"][field] = []
        
        # Parse dict JSON fields
        for field in ["device_usage", "social_media_activity", "content_consumption"]:
            if field in persona["behavioral"] and persona["behavioral"][field]:
                try:
                    persona["behavioral"][field] = json.loads(persona["behavioral"][field])
                except:
                    persona["behavioral"][field] = {}
    
    # Get contextual data
    cursor.execute("SELECT * FROM contextual_data WHERE persona_id = ?", (persona_id,))
    context_row = cursor.fetchone()
    if context_row:
        persona["contextual"] = dict(context_row)
    
    conn.close()
    return persona

def create_sample_persona():
    """Create a test persona directly using the API format"""
    # Create a simple persona with all required fields in the API format
    api_persona = {
        "name": "API Test Persona",
        "demographic": {
            "language": "en-US",
            "country": "United States",
            "city": "San Francisco",
            "region": "California",
            "latitude": 37.7749,
            "longitude": -122.4194
        }
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
        print(f"Successfully created test persona with ID: {result.get('id')}")
        return result
    except Exception as e:
        print(f"Error creating test persona: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return None

def migrate_persona(persona_id):
    """Migrate a specific persona from the database to the API"""
    # Get the persona from the database
    persona_data = get_persona_from_db(persona_id)
    if not persona_data:
        print(f"Persona with ID {persona_id} not found in database")
        return False, None
    
    # Convert to API format
    api_persona = {
        "name": persona_data["name"],
    }
    
    # Add demographic data
    if "demographic" in persona_data:
        demo = persona_data["demographic"]
        api_persona["demographic"] = {
            "language": demo.get("language"),
            "country": demo.get("country"),
            "city": demo.get("city"),
            "region": demo.get("region"),
            "latitude": demo.get("latitude"),
            "longitude": demo.get("longitude"),
            "age": demo.get("age"),
            "gender": demo.get("gender"),
            "education": demo.get("education"),
            "income": demo.get("income"),
            "occupation": demo.get("occupation")
        }
    
    # Add psychographic data
    if "psychographic" in persona_data:
        psycho = persona_data["psychographic"]
        interests = psycho.get("interests", [])
        personal_values = psycho.get("personal_values", [])
        attitudes = psycho.get("attitudes", [])
        opinions = psycho.get("opinions", [])
        
        api_persona["psychographic"] = {
            "interests": interests if isinstance(interests, list) else [],
            "personal_values": personal_values if isinstance(personal_values, list) else [],
            "attitudes": attitudes if isinstance(attitudes, list) else [],
            "lifestyle": psycho.get("lifestyle"),
            "personality": psycho.get("personality"),
            "opinions": opinions if isinstance(opinions, list) else []
        }
    
    # Add behavioral data
    if "behavioral" in persona_data:
        behav = persona_data["behavioral"]
        browsing_habits = behav.get("browsing_habits", [])
        purchase_history = behav.get("purchase_history", [])
        brand_interactions = behav.get("brand_interactions", [])
        device_usage = behav.get("device_usage", {})
        social_media_activity = behav.get("social_media_activity", {})
        content_consumption = behav.get("content_consumption", {})
        
        api_persona["behavioral"] = {
            "browsing_habits": browsing_habits if isinstance(browsing_habits, list) else [],
            "purchase_history": purchase_history if isinstance(purchase_history, list) else [],
            "brand_interactions": brand_interactions if isinstance(brand_interactions, list) else [],
            "device_usage": device_usage if isinstance(device_usage, dict) else {},
            "social_media_activity": social_media_activity if isinstance(social_media_activity, dict) else {},
            "content_consumption": content_consumption if isinstance(content_consumption, dict) else {}
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
    
    # Print what we're sending
    print(f"Sending persona data: {json.dumps(api_persona, indent=2)}")
    
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

def update_create_sample_script():
    """Create an updated version of create_sample_personas.py"""
    script_path = "create_sample_personas_api.py"
    script_content = """#!/usr/bin/env python3
\"\"\"
Script to create sample personas using the Persona API
\"\"\"
from personaclient import PersonaClient

def create_sample_personas():
    \"\"\"Create sample personas for each region\"\"\"
    
    # Create a client
    client = PersonaClient(base_url="http://localhost:5050")
    
    # Sample personas for different regions
    personas = [
        # North America (US) Persona
        {
            "name": "Alex Johnson",
            "demographic": {
                "latitude": 37.7749,
                "longitude": -122.4194,  # San Francisco
                "language": "en-US",
                "country": "US",
                "city": "San Francisco",
                "region": "California",
                "age": 32,
                "gender": "Male",
                "education": "Master's Degree",
                "income": "High",
                "occupation": "Software Engineer"
            },
            "psychographic": {
                "interests": ["technology", "hiking", "craft beer", "photography"],
                "personal_values": ["innovation", "work-life balance", "environmental sustainability"],
                "attitudes": ["optimistic", "progressive", "tech-savvy"],
                "lifestyle": "Urban professional",
                "personality": "Analytical, creative",
                "opinions": ["privacy-focused", "pro-innovation"]
            },
            "behavioral": {
                "browsing_habits": ["tech news", "social media", "productivity tools"],
                "purchase_history": ["electronics", "outdoor gear", "subscription services"],
                "brand_interactions": ["Apple", "Patagonia", "Spotify"],
                "device_usage": {"mobile": "4 hours/day", "desktop": "8 hours/day", "tablet": "1 hour/day"},
                "social_media_activity": {"twitter": "daily", "instagram": "weekly", "linkedin": "daily"},
                "content_consumption": {"videos": "2 hours/day", "articles": "10/day", "podcasts": "5/week"}
            },
            "contextual": {
                "time_of_day": "morning",
                "day_of_week": "weekday",
                "season": "spring",
                "weather": "sunny",
                "device_type": "desktop",
                "browser_type": "chrome",
                "screen_size": "1920x1080",
                "connection_type": "wifi"
            }
        },
        
        # South America (Brazil) Persona
        {
            "name": "Isabela Santos",
            "demographic": {
                "latitude": -23.5505,
                "longitude": -46.6333,  # São Paulo
                "language": "pt-BR",
                "country": "BR",
                "city": "São Paulo",
                "region": "São Paulo",
                "age": 28,
                "gender": "Female",
                "education": "Bachelor's Degree",
                "income": "Medium",
                "occupation": "Marketing Specialist"
            },
            "psychographic": {
                "interests": ["fashion", "travel", "cooking", "social media"],
                "personal_values": ["family", "community", "cultural heritage"],
                "attitudes": ["social", "expressive", "trend-conscious"],
                "lifestyle": "Urban socialite",
                "personality": "Extroverted, creative",
                "opinions": ["community-focused", "culturally proud"]
            },
            "behavioral": {
                "browsing_habits": ["social media", "fashion blogs", "travel sites"],
                "purchase_history": ["clothing", "cosmetics", "travel experiences"],
                "brand_interactions": ["Havaianas", "Natura", "Instagram"],
                "device_usage": {"mobile": "6 hours/day", "desktop": "4 hours/day", "tablet": "2 hours/day"},
                "social_media_activity": {"instagram": "hourly", "facebook": "daily", "tiktok": "daily"},
                "content_consumption": {"videos": "3 hours/day", "articles": "5/day", "social media": "4 hours/day"}
            },
            "contextual": {
                "time_of_day": "evening",
                "day_of_week": "all week",
                "season": "summer",
                "weather": "warm",
                "device_type": "mobile",
                "browser_type": "chrome",
                "screen_size": "375x812",
                "connection_type": "4g"
            }
        },
        
        # Europe (Germany) Persona
        {
            "name": "Lukas Schmidt",
            "demographic": {
                "latitude": 52.5200,
                "longitude": 13.4050,  # Berlin
                "language": "de-DE",
                "country": "DE",
                "city": "Berlin",
                "region": "Berlin",
                "age": 35,
                "gender": "Male",
                "education": "PhD",
                "income": "High",
                "occupation": "Research Scientist"
            },
            "psychographic": {
                "interests": ["classical music", "literature", "environmental issues", "cycling"],
                "personal_values": ["precision", "efficiency", "environmental responsibility"],
                "attitudes": ["analytical", "detail-oriented", "environmentally conscious"],
                "lifestyle": "Eco-conscious urban dweller",
                "personality": "Methodical, thoughtful",
                "opinions": ["pro-environment", "pro-EU", "privacy advocate"]
            },
            "behavioral": {
                "browsing_habits": ["news sites", "academic journals", "environmental blogs"],
                "purchase_history": ["books", "sustainable products", "quality electronics"],
                "brand_interactions": ["Bosch", "Deutsche Bahn", "Birkenstock"],
                "device_usage": {"mobile": "2 hours/day", "desktop": "7 hours/day", "e-reader": "1 hour/day"},
                "social_media_activity": {"twitter": "weekly", "linkedin": "daily", "facebook": "rarely"},
                "content_consumption": {"articles": "15/day", "books": "2/week", "documentaries": "3/week"}
            },
            "contextual": {
                "time_of_day": "morning",
                "day_of_week": "weekday",
                "season": "fall",
                "weather": "cloudy",
                "device_type": "desktop",
                "browser_type": "firefox",
                "screen_size": "2560x1440",
                "connection_type": "ethernet"
            }
        },
        
        # Asia (Japan) Persona
        {
            "name": "Yuki Tanaka",
            "demographic": {
                "latitude": 35.6762,
                "longitude": 139.6503,  # Tokyo
                "language": "ja-JP",
                "country": "JP",
                "city": "Tokyo",
                "region": "Tokyo",
                "age": 24,
                "gender": "Female",
                "education": "Bachelor's Degree",
                "income": "Medium",
                "occupation": "UX Designer"
            },
            "psychographic": {
                "interests": ["anime", "technology", "minimalist design", "photography"],
                "personal_values": ["harmony", "innovation", "aesthetics"],
                "attitudes": ["tech-forward", "detail-oriented", "trend-conscious"],
                "lifestyle": "Urban tech enthusiast",
                "personality": "Creative, meticulous",
                "opinions": ["design-focused", "tech-optimist"]
            },
            "behavioral": {
                "browsing_habits": ["design blogs", "tech news", "social media", "anime streaming"],
                "purchase_history": ["digital content", "tech gadgets", "design books"],
                "brand_interactions": ["Nintendo", "Muji", "Uniqlo"],
                "device_usage": {"mobile": "5 hours/day", "desktop": "6 hours/day", "gaming console": "2 hours/day"},
                "social_media_activity": {"twitter": "hourly", "instagram": "daily", "line": "hourly"},
                "content_consumption": {"anime": "2 hours/day", "tech articles": "8/day", "design tutorials": "3/week"}
            },
            "contextual": {
                "time_of_day": "night",
                "day_of_week": "all week",
                "season": "spring",
                "weather": "mild",
                "device_type": "laptop",
                "browser_type": "chrome",
                "screen_size": "1440x900",
                "connection_type": "wifi"
            }
        },
        
        # Africa (South Africa) Persona
        {
            "name": "Thabo Ndlovu",
            "demographic": {
                "latitude": -26.2041,
                "longitude": 28.0473,  # Johannesburg
                "language": "en-ZA",
                "country": "ZA",
                "city": "Johannesburg",
                "region": "Gauteng",
                "age": 30,
                "gender": "Male",
                "education": "Bachelor's Degree",
                "income": "Medium",
                "occupation": "Entrepreneur"
            },
            "psychographic": {
                "interests": ["business", "football", "music", "community development"],
                "personal_values": ["community", "ambition", "cultural heritage"],
                "attitudes": ["optimistic", "resourceful", "community-minded"],
                "lifestyle": "Ambitious professional",
                "personality": "Outgoing, determined",
                "opinions": ["pro-development", "community-focused"]
            },
            "behavioral": {
                "browsing_habits": ["business news", "sports sites", "educational content"],
                "purchase_history": ["business tools", "mobile data", "local products"],
                "brand_interactions": ["MTN", "Vodacom", "Standard Bank"],
                "device_usage": {"mobile": "7 hours/day", "laptop": "5 hours/day"},
                "social_media_activity": {"whatsapp": "hourly", "facebook": "daily", "twitter": "daily"},
                "content_consumption": {"news": "multiple times/day", "business articles": "5/day", "sports": "daily"}
            },
            "contextual": {
                "time_of_day": "all day",
                "day_of_week": "weekday",
                "season": "summer",
                "weather": "sunny",
                "device_type": "mobile",
                "browser_type": "chrome",
                "screen_size": "412x915",
                "connection_type": "4g"
            }
        }
    ]
    
    # Create each persona via the API
    for persona_data in personas:
        try:
            result = client.create_persona(persona_data)
            print(f"Created persona: {persona_data['name']} (ID: {result.get('id')})")
        except Exception as e:
            print(f"Error creating persona {persona_data['name']}: {str(e)}")
    
    print("Sample personas created successfully!")

if __name__ == "__main__":
    create_sample_personas()
"""
    
    # Write the script to a file
    with open(script_path, "w") as f:
        f.write(script_content)
    
    print(f"Created updated sample persona script: {script_path}")
    return script_path

def main():
    """Main function"""
    print("=== Migrating personas from the database to the API ===")
    
    # Create a test sample to verify the API is working
    print("\nCreating a test persona to verify API is working...")
    test_result = create_sample_persona()
    
    if not test_result:
        print("Failed to create test persona. API might not be working correctly.")
        return 1
    
    # Try to migrate each persona from the database
    print("\nMigrating personas from database to API:")
    for persona_id in range(1, 6):  # IDs from 1 to 5
        print(f"\nMigrating persona ID: {persona_id}")
        success, result = migrate_persona(persona_id)
        
        if success:
            print(f"  Successfully migrated. New API ID: {result.get('id')}")
        else:
            print(f"  Failed to migrate")
    
    # Create an updated create_sample_personas.py for future use
    print("\nCreating updated create_sample_personas script for API use...")
    script_path = update_create_sample_script()
    
    print("\nMigration process completed.")
    return 0

if __name__ == "__main__":
    main()
