#!/usr/bin/env python3
"""
Create sample personas for testing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import save_persona

def create_sample_personas():
    """Create sample personas for testing"""
    
    # Sample personas for different regions
    personas = [
        # North America (US) Persona
        {
            "name": "Alex Johnson",
            "demographic": {
                "geolocation": "37.7749,-122.4194",  # San Francisco
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
        
        # Europe (UK) Persona
        {
            "name": "Emma Thompson",
            "demographic": {
                "geolocation": "51.5074,-0.1278",  # London
                "language": "en-GB",
                "country": "GB",
                "city": "London",
                "region": "England",
                "age": 28,
                "gender": "Female",
                "education": "Bachelor's Degree",
                "income": "Medium",
                "occupation": "Marketing Manager"
            },
            "psychographic": {
                "interests": ["fashion", "travel", "fitness", "art"],
                "personal_values": ["authenticity", "community", "cultural diversity"],
                "attitudes": ["curious", "socially conscious", "globally minded"],
                "lifestyle": "Urban cosmopolitan",
                "personality": "Outgoing, creative",
                "opinions": ["sustainability-focused", "equality advocate"]
            },
            "behavioral": {
                "browsing_habits": ["fashion blogs", "travel sites", "news"],
                "purchase_history": ["clothing", "travel", "beauty products"],
                "brand_interactions": ["Zara", "Airbnb", "BBC"],
                "device_usage": {"mobile": "6 hours/day", "desktop": "6 hours/day", "tablet": "2 hours/day"},
                "social_media_activity": {"instagram": "daily", "facebook": "weekly", "twitter": "occasional"},
                "content_consumption": {"videos": "3 hours/day", "articles": "15/day", "podcasts": "3/week"}
            },
            "contextual": {
                "time_of_day": "afternoon",
                "day_of_week": "weekday",
                "season": "autumn",
                "weather": "cloudy",
                "device_type": "mobile",
                "browser_type": "safari",
                "screen_size": "375x812",
                "connection_type": "4g"
            }
        },
        
        # Asia (Japan) Persona
        {
            "name": "Hiroshi Tanaka",
            "demographic": {
                "geolocation": "35.6762,139.6503",  # Tokyo
                "language": "ja-JP",
                "country": "JP",
                "city": "Tokyo",
                "region": "Kanto",
                "age": 35,
                "gender": "Male",
                "education": "Bachelor's Degree",
                "income": "Medium-High",
                "occupation": "Business Analyst"
            },
            "psychographic": {
                "interests": ["anime", "gaming", "technology", "traditional culture"],
                "personal_values": ["respect", "efficiency", "tradition"],
                "attitudes": ["detail-oriented", "respectful", "technology-forward"],
                "lifestyle": "Urban traditional-modern blend",
                "personality": "Methodical, respectful",
                "opinions": ["quality-focused", "tradition-respecting"]
            },
            "behavioral": {
                "browsing_habits": ["tech reviews", "gaming sites", "news"],
                "purchase_history": ["electronics", "games", "traditional items"],
                "brand_interactions": ["Sony", "Nintendo", "Uniqlo"],
                "device_usage": {"mobile": "8 hours/day", "desktop": "4 hours/day", "gaming": "3 hours/day"},
                "social_media_activity": {"line": "daily", "twitter": "daily", "instagram": "weekly"},
                "content_consumption": {"videos": "4 hours/day", "manga": "2 hours/day", "news": "1 hour/day"}
            },
            "contextual": {
                "time_of_day": "evening",
                "day_of_week": "weekday",
                "season": "summer",
                "weather": "humid",
                "device_type": "mobile",
                "browser_type": "chrome",
                "screen_size": "390x844",
                "connection_type": "5g"
            }
        }
    ]
    
    # Create each persona
    for persona_data in personas:
        try:
            persona_id = save_persona(persona_data)
            print(f"Created persona '{persona_data['name']}' with ID: {persona_id}")
        except Exception as e:
            print(f"Error creating persona '{persona_data['name']}': {str(e)}")

if __name__ == "__main__":
    print("Creating sample personas...")
    create_sample_personas()
    print("Sample personas created successfully!")