#!/usr/bin/env python3
"""
Migration script to move from specific tables to dynamic attributes

This script will:
1. Create the new persona_attributes table
2. Copy data from psychographic, behavioral, and contextual tables to the new format
3. Verify the migration was successful
"""
import argparse
import json
import logging
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the parent directory to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import SQLALCHEMY_DATABASE_URI
from app.models_updated import Base, Persona, PersonaAttributes, AttributeCategory
from app.models import PsychographicData, BehavioralData, ContextualData

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('migration')

def create_schema(engine):
    """Create new schema with persona_attributes table"""
    logger.info("Creating new schema with persona_attributes table")
    
    # Create the new table
    Base.metadata.create_all(engine, tables=[PersonaAttributes.__table__])
    
    logger.info("Schema creation completed")

def migrate_psychographic_data(session):
    """Migrate data from psychographic_data to persona_attributes"""
    logger.info("Migrating psychographic data")
    
    # Get all psychographic data
    psychographic_records = session.query(PsychographicData).all()
    logger.info(f"Found {len(psychographic_records)} psychographic records")
    
    for record in psychographic_records:
        try:
            # Convert to dictionary format
            data = {
                'interests': json.loads(record.interests) if record.interests else [],
                'personal_values': json.loads(record.personal_values) if record.personal_values else [],
                'attitudes': json.loads(record.attitudes) if record.attitudes else [],
                'lifestyle': record.lifestyle,
                'personality': record.personality,
                'opinions': json.loads(record.opinions) if record.opinions else []
            }
            
            # Create new attribute record
            new_attr = PersonaAttributes(
                persona_id=record.persona_id,
                category=AttributeCategory.PSYCHOGRAPHIC,
                data=data
            )
            
            session.add(new_attr)
            logger.info(f"Migrated psychographic data for persona {record.persona_id}")
        except Exception as e:
            logger.error(f"Error migrating psychographic data for persona {record.persona_id}: {str(e)}")
    
    session.commit()
    logger.info("Psychographic data migration completed")

def migrate_behavioral_data(session):
    """Migrate data from behavioral_data to persona_attributes"""
    logger.info("Migrating behavioral data")
    
    # Get all behavioral data
    behavioral_records = session.query(BehavioralData).all()
    logger.info(f"Found {len(behavioral_records)} behavioral records")
    
    for record in behavioral_records:
        try:
            # Convert to dictionary format
            data = {
                'browsing_habits': json.loads(record.browsing_habits) if record.browsing_habits else [],
                'purchase_history': json.loads(record.purchase_history) if record.purchase_history else [],
                'brand_interactions': json.loads(record.brand_interactions) if record.brand_interactions else [],
                'device_usage': json.loads(record.device_usage) if record.device_usage else {},
                'social_media_activity': json.loads(record.social_media_activity) if record.social_media_activity else {},
                'content_consumption': json.loads(record.content_consumption) if record.content_consumption else {}
            }
            
            # Create new attribute record
            new_attr = PersonaAttributes(
                persona_id=record.persona_id,
                category=AttributeCategory.BEHAVIORAL,
                data=data
            )
            
            session.add(new_attr)
            logger.info(f"Migrated behavioral data for persona {record.persona_id}")
        except Exception as e:
            logger.error(f"Error migrating behavioral data for persona {record.persona_id}: {str(e)}")
    
    session.commit()
    logger.info("Behavioral data migration completed")

def migrate_contextual_data(session):
    """Migrate data from contextual_data to persona_attributes"""
    logger.info("Migrating contextual data")
    
    # Get all contextual data
    contextual_records = session.query(ContextualData).all()
    logger.info(f"Found {len(contextual_records)} contextual records")
    
    for record in contextual_records:
        try:
            # Convert to dictionary format
            data = {
                'time_of_day': record.time_of_day,
                'day_of_week': record.day_of_week,
                'season': record.season,
                'weather': record.weather,
                'device_type': record.device_type,
                'browser_type': record.browser_type,
                'screen_size': record.screen_size,
                'connection_type': record.connection_type
            }
            
            # Create new attribute record
            new_attr = PersonaAttributes(
                persona_id=record.persona_id,
                category=AttributeCategory.CONTEXTUAL,
                data=data
            )
            
            session.add(new_attr)
            logger.info(f"Migrated contextual data for persona {record.persona_id}")
        except Exception as e:
            logger.error(f"Error migrating contextual data for persona {record.persona_id}: {str(e)}")
    
    session.commit()
    logger.info("Contextual data migration completed")

def verify_migration(session):
    """Verify that all data was migrated correctly"""
    logger.info("Verifying migration")
    
    # Count records in old and new tables
    psycho_count = session.query(PsychographicData).count()
    behav_count = session.query(BehavioralData).count()
    context_count = session.query(ContextualData).count()
    
    new_psycho_count = session.query(PersonaAttributes).filter_by(category=AttributeCategory.PSYCHOGRAPHIC).count()
    new_behav_count = session.query(PersonaAttributes).filter_by(category=AttributeCategory.BEHAVIORAL).count()
    new_context_count = session.query(PersonaAttributes).filter_by(category=AttributeCategory.CONTEXTUAL).count()
    
    logger.info(f"Psychographic data: {psycho_count} old records, {new_psycho_count} new records")
    logger.info(f"Behavioral data: {behav_count} old records, {new_behav_count} new records")
    logger.info(f"Contextual data: {context_count} old records, {new_context_count} new records")
    
    # Check a few random records to make sure data was migrated correctly
    logger.info("Checking sample records...")
    
    for category in [AttributeCategory.PSYCHOGRAPHIC, AttributeCategory.BEHAVIORAL, AttributeCategory.CONTEXTUAL]:
        attr = session.query(PersonaAttributes).filter_by(category=category).first()
        if attr:
            logger.info(f"Sample {category.value} record for persona {attr.persona_id}: {attr.get_data()}")
        else:
            logger.warning(f"No {category.value} records found to check")
    
    logger.info("Migration verification completed")

def main():
    """Main migration function"""
    parser = argparse.ArgumentParser(description='Migrate persona data to new schema')
    parser.add_argument('--db-uri', help='Database URI')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no changes)')
    args = parser.parse_args()
    
    # Get database URI
    db_uri = args.db_uri or SQLALCHEMY_DATABASE_URI
    logger.info(f"Using database: {db_uri}")
    
    # Create engine and session
    engine = create_engine(db_uri)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        if args.dry_run:
            logger.info("DRY RUN MODE - No changes will be made")
            
            # Check if we can access the database
            session.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            
            # Check existing tables
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            logger.info(f"Existing tables: {', '.join(tables)}")
            
            # Count personas
            persona_count = session.query(Persona).count()
            logger.info(f"Found {persona_count} personas")
            
            logger.info("Dry run completed")
        else:
            # Create new schema
            create_schema(engine)
            
            # Migrate data
            migrate_psychographic_data(session)
            migrate_behavioral_data(session)
            migrate_contextual_data(session)
            
            # Verify migration
            verify_migration(session)
            
            logger.info("Migration completed successfully")
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return 1
    finally:
        session.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
