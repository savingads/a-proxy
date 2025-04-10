#!/usr/bin/env python3
"""
Migration utility to transfer personas from local SQLite database to the Persona API Service
"""
import os
import sys
import argparse
import logging
import sqlite3
import json
from datetime import datetime

# Add the current working directory to the path
sys.path.append(os.getcwd())

# Import the Persona client
from personaclient import PersonaClient
from personaclient.exceptions import PersonaClientError, PersonaValidationError
from persona_config import (
    PERSONA_API_BASE_URL,
    PERSONA_API_VERSION,
    PERSONA_API_TIMEOUT,
    PERSONA_API_AUTH_TOKEN
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('migration.log')
    ]
)
logger = logging.getLogger('persona_migration')

# Database path
DB_PATH = os.path.join('data', 'personas.db')

def get_db_connection():
    """Create a connection to the SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign key constraints support
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def get_persona_client():
    """Get a configured Persona API client instance"""
    return PersonaClient(
        base_url=PERSONA_API_BASE_URL,
        api_version=PERSONA_API_VERSION,
        timeout=PERSONA_API_TIMEOUT,
        auth_token=PERSONA_API_AUTH_TOKEN
    )

def get_all_personas_from_db():
    """Get all personas from the SQLite database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # First get all personas basic info
    cursor.execute("""
    SELECT p.id, p.name, p.created_at, p.updated_at
    FROM personas p
    ORDER BY p.updated_at DESC
    """)
    
    personas = [dict(row) for row in cursor.fetchall()]
    
    # Now for each persona, get their associated data
    for persona in personas:
        persona_id = persona['id']
        
        # Get demographic data
        cursor.execute("SELECT * FROM demographic_data WHERE persona_id = ?", (persona_id,))
        demographic = cursor.fetchone()
        if demographic:
            persona['demographic'] = dict(demographic)
        
        # Get psychographic data
        cursor.execute("SELECT * FROM psychographic_data WHERE persona_id = ?", (persona_id,))
        psychographic = cursor.fetchone()
        if psychographic:
            persona['psychographic'] = dict(psychographic)
            # Parse JSON fields
            for field in ['interests', 'personal_values', 'attitudes', 'opinions']:
                if persona['psychographic'][field]:
                    persona['psychographic'][field] = json.loads(persona['psychographic'][field])
        
        # Get behavioral data
        cursor.execute("SELECT * FROM behavioral_data WHERE persona_id = ?", (persona_id,))
        behavioral = cursor.fetchone()
        if behavioral:
            persona['behavioral'] = dict(behavioral)
            # Parse JSON fields
            for field in ['browsing_habits', 'purchase_history', 'brand_interactions', 
                         'device_usage', 'social_media_activity', 'content_consumption']:
                if persona['behavioral'][field]:
                    persona['behavioral'][field] = json.loads(persona['behavioral'][field])
        
        # Get contextual data
        cursor.execute("SELECT * FROM contextual_data WHERE persona_id = ?", (persona_id,))
        contextual = cursor.fetchone()
        if contextual:
            persona['contextual'] = dict(contextual)
    
    conn.close()
    return personas

def prepare_persona_for_api(persona):
    """
    Transform a persona from the database format to the format expected by the API
    """
    # Remove internal IDs and other fields not needed by API
    api_persona = {
        "name": persona['name']
    }
    
    # Add demographic data if present
    if 'demographic' in persona:
        api_persona['demographic'] = {
            "latitude": persona['demographic'].get('latitude'),
            "longitude": persona['demographic'].get('longitude'),
            "language": persona['demographic'].get('language'),
            "country": persona['demographic'].get('country'),
            "city": persona['demographic'].get('city'),
            "region": persona['demographic'].get('region'),
            "age": persona['demographic'].get('age'),
            "gender": persona['demographic'].get('gender'),
            "education": persona['demographic'].get('education'),
            "income": persona['demographic'].get('income'),
            "occupation": persona['demographic'].get('occupation')
        }
    
    # Add psychographic data if present
    if 'psychographic' in persona:
        api_persona['psychographic'] = {
            "interests": persona['psychographic'].get('interests', []),
            "personal_values": persona['psychographic'].get('personal_values', []),
            "attitudes": persona['psychographic'].get('attitudes', []),
            "lifestyle": persona['psychographic'].get('lifestyle'),
            "personality": persona['psychographic'].get('personality'),
            "opinions": persona['psychographic'].get('opinions', [])
        }
    
    # Add behavioral data if present
    if 'behavioral' in persona:
        api_persona['behavioral'] = {
            "browsing_habits": persona['behavioral'].get('browsing_habits', []),
            "purchase_history": persona['behavioral'].get('purchase_history', []),
            "brand_interactions": persona['behavioral'].get('brand_interactions', []),
            "device_usage": persona['behavioral'].get('device_usage', {}),
            "social_media_activity": persona['behavioral'].get('social_media_activity', {}),
            "content_consumption": persona['behavioral'].get('content_consumption', {})
        }
    
    # Add contextual data if present
    if 'contextual' in persona:
        api_persona['contextual'] = {
            "time_of_day": persona['contextual'].get('time_of_day'),
            "day_of_week": persona['contextual'].get('day_of_week'),
            "season": persona['contextual'].get('season'),
            "weather": persona['contextual'].get('weather'),
            "device_type": persona['contextual'].get('device_type'),
            "browser_type": persona['contextual'].get('browser_type'),
            "screen_size": persona['contextual'].get('screen_size'),
            "connection_type": persona['contextual'].get('connection_type')
        }
    
    return api_persona

def migrate_personas(personas, dry_run=False, limit=None):
    """
    Migrate personas from the database to the API
    
    Args:
        personas: List of personas to migrate
        dry_run: If True, don't actually send to API
        limit: Maximum number of personas to migrate
    
    Returns:
        dict: Migration statistics
    """
    if limit:
        personas = personas[:limit]
    
    client = get_persona_client()
    stats = {
        "total": len(personas),
        "successful": 0,
        "failed": 0,
        "skipped": 0,
        "errors": []
    }
    
    for i, persona in enumerate(personas):
        logger.info(f"Migrating persona {i+1}/{len(personas)}: {persona['name']} (ID: {persona['id']})")
        
        try:
            # Prepare persona data for API
            api_persona = prepare_persona_for_api(persona)
            
            # Skip in dry run mode
            if dry_run:
                logger.info(f"DRY RUN: Would migrate persona: {persona['name']}")
                stats["skipped"] += 1
                continue
            
            # Create in API
            result = client.create_persona(api_persona)
            logger.info(f"Successfully migrated persona: {persona['name']} to API ID: {result.get('id')}")
            stats["successful"] += 1
            
        except PersonaValidationError as e:
            logger.error(f"Validation error for persona {persona['id']}: {str(e)}")
            stats["failed"] += 1
            stats["errors"].append({
                "persona_id": persona['id'],
                "persona_name": persona['name'],
                "error": str(e),
                "type": "validation"
            })
        except PersonaClientError as e:
            logger.error(f"API error for persona {persona['id']}: {str(e)}")
            stats["failed"] += 1
            stats["errors"].append({
                "persona_id": persona['id'],
                "persona_name": persona['name'],
                "error": str(e),
                "type": "api"
            })
        except Exception as e:
            logger.error(f"Unexpected error for persona {persona['id']}: {str(e)}")
            stats["failed"] += 1
            stats["errors"].append({
                "persona_id": persona['id'],
                "persona_name": persona['name'],
                "error": str(e),
                "type": "unexpected"
            })
    
    return stats

def print_stats(stats):
    """Print migration statistics"""
    print("\n" + "="*50)
    print(f"Migration Results:")
    print(f"Total personas processed: {stats['total']}")
    print(f"Successfully migrated: {stats['successful']}")
    print(f"Failed: {stats['failed']}")
    print(f"Skipped (dry run): {stats['skipped']}")
    
    if stats['errors']:
        print("\nErrors:")
        for i, error in enumerate(stats['errors']):
            print(f"{i+1}. {error['persona_name']} (ID: {error['persona_id']}): {error['error']} ({error['type']})")
    
    print("="*50)

def main():
    """Main migration function"""
    parser = argparse.ArgumentParser(description='Migrate personas from SQLite database to Persona API')
    parser.add_argument('--dry-run', action='store_true', help='Simulate migration without sending to API')
    parser.add_argument('--limit', type=int, help='Limit the number of personas to migrate')
    parser.add_argument('--id', type=int, help='Migrate a specific persona by ID')
    args = parser.parse_args()
    
    # Show settings
    print(f"Persona API URL: {PERSONA_API_BASE_URL}")
    print(f"Database path: {DB_PATH}")
    
    # Check if database exists
    if not os.path.exists(DB_PATH):
        logger.error(f"Database file not found: {DB_PATH}")
        print(f"Error: Database file not found at {DB_PATH}")
        return 1
    
    # Get personas from database
    try:
        all_personas = get_all_personas_from_db()
        logger.info(f"Found {len(all_personas)} personas in the database")
        
        if args.id:
            # Find persona by ID
            persona = next((p for p in all_personas if p['id'] == args.id), None)
            if not persona:
                logger.error(f"Persona with ID {args.id} not found")
                print(f"Error: Persona with ID {args.id} not found")
                return 1
            personas_to_migrate = [persona]
        else:
            personas_to_migrate = all_personas
        
        # Migrate personas
        stats = migrate_personas(personas_to_migrate, args.dry_run, args.limit)
        
        # Print statistics
        print_stats(stats)
        
        if stats['failed'] > 0:
            return 1
        return 0
        
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
