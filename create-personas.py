#!/usr/bin/env python3

"""
Utility script to create sample personas using the Persona API.

This script can be used to create a set of sample personas with realistic
profiles representing different regions of the world. It uses the Persona API
to create the personas and can be configured to use different API endpoints.

Usage:
    python3 create-personas.py [--api-url URL] [--count NUM] [--reset]

Options:
    --api-url URL    Base URL of the Persona API (default: http://localhost:5050)
    --count NUM      Number of personas to create (default: all)
    --reset          Reset (delete all existing personas) before creating new ones
    --help           Show this help message and exit
"""

import argparse
import sys
import json
from personaclient import PersonaClient


def create_sample_personas(api_url="http://localhost:5050", count=None, reset=False):
    """
    Create sample personas for each region.
    
    Args:
        api_url (str): Base URL of the Persona API
        count (int): Number of personas to create (None for all)
        reset (bool): Whether to reset (delete all personas) before creating new ones
    """
    # Create a client
    client = PersonaClient(base_url=api_url)
    
    # Reset if requested
    if reset:
        try:
            print("Deleting all existing personas...")
            personas = client.get_all_personas()
            for persona in personas.get('personas', []):
                client.delete_persona(persona['id'])
                print(f"Deleted persona ID: {persona['id']} (Name: {persona['name']})")
            print(f"Deleted {len(personas.get('personas', []))} personas.")
        except Exception as e:
            print(f"Error resetting personas: {str(e)}")

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
                "personality": "Analytical creative",
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
                "personality": "Extroverted creative",
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
                "personality": "Methodical thoughtful",
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
                "personality": "Creative meticulous",
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
                "personality": "Outgoing determined",
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

    # Apply count limit if specified
    if count is not None:
        count = min(count, len(personas))
        personas = personas[:count]

    created_count = 0
    # Create each persona via the API
    for persona_data in personas:
        try:
            result = client.create_persona(persona_data)
            created_count += 1
            print(f"Created persona: {persona_data['name']} (ID: {result.get('id')})")
        except Exception as e:
            print(f"Error creating persona {persona_data['name']}: {str(e)}")

    print(f"\nSummary: Created {created_count} sample personas successfully!")


def list_personas(api_url="http://localhost:5050"):
    """List all personas in the API."""
    client = PersonaClient(base_url=api_url)
    try:
        response = client.get_all_personas()
        personas = response.get('personas', [])
        
        if not personas:
            print("No personas found.")
            return
        
        print(f"\nFound {len(personas)} personas:")
        print("-" * 50)
        for persona in personas:
            print(f"ID: {persona['id']} | Name: {persona['name']} | Country: {persona.get('demographic', {}).get('country', 'N/A')}")
        print("-" * 50)
        
    except Exception as e:
        print(f"Error listing personas: {str(e)}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Create sample personas using the Persona API.',
        formatter_class=argparse.RawTextHelpFormatter)
    
    parser.add_argument('--api-url', type=str, default='http://localhost:5050',
                        help='Base URL of the Persona API (default: %(default)s)')
    parser.add_argument('--count', type=int, 
                        help='Number of personas to create (default: all)')
    parser.add_argument('--reset', action='store_true',
                        help='Reset (delete all existing personas) before creating new ones')
    parser.add_argument('--list', action='store_true',
                        help='List all existing personas instead of creating new ones')
    
    # Print help if no arguments are provided
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    args = parser.parse_args()
    
    if args.list:
        list_personas(api_url=args.api_url)
    else:
        create_sample_personas(api_url=args.api_url, count=args.count, reset=args.reset)


if __name__ == "__main__":
    main()
