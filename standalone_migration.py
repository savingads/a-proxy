#!/usr/bin/env python3
"""
Standalone migration script to create the new persona_attributes table

This script is completely self-contained and doesn't depend on existing app modules.
"""
import argparse
import json
import logging
import os
import sys
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, DateTime, Text, Enum, create_engine,
    MetaData, Table, inspect
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import enum

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('migration')

# Create a standalone base
Base = declarative_base()

# Define models independently of the app
class AttributeCategory(enum.Enum):
    """Enum for persona attribute categories"""
    PSYCHOGRAPHIC = "psychographic"
    BEHAVIORAL = "behavioral"
    CONTEXTUAL = "contextual"

class PersonaAttributes(Base):
    """Dynamic attributes for a persona (psychographic, behavioral, contextual)"""
    __tablename__ = 'persona_attributes'
    
    id = Column(Integer, primary_key=True)
    persona_id = Column(Integer, ForeignKey('personas.id', ondelete='CASCADE'), nullable=False)
    category = Column(Enum(AttributeCategory), nullable=False)
    data = Column(Text, nullable=False, default='{}')  # JSON text blob

def create_schema(engine, dry_run=False):
    """Create the persona_attributes table"""
    if dry_run:
        logger.info("DRY RUN: Would create the persona_attributes table")
        return
        
    # Create the new table
    logger.info("Creating the persona_attributes table")
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    if 'persona_attributes' not in metadata.tables:
        PersonaAttributes.__table__.create(engine)
        logger.info("persona_attributes table created")
    else:
        logger.info("persona_attributes table already exists")

def check_database(engine):
    """Check what tables exist in the database"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    logger.info(f"Existing tables: {', '.join(tables)}")
    
    for table in ['personas', 'demographic_data', 'psychographic_data', 'behavioral_data', 'contextual_data']:
        if table in tables:
            logger.info(f"Table {table} exists")
        else:
            logger.info(f"Table {table} does not exist")

def main():
    """Main migration function"""
    parser = argparse.ArgumentParser(description='Create persona_attributes table')
    parser.add_argument('--db-uri', default='sqlite:///persona-service/persona_service.db', 
                      help='Database URI (default: sqlite:///persona-service/persona_service.db)')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no changes)')
    args = parser.parse_args()
    
    # Get database URI
    db_uri = args.db_uri
    logger.info(f"Using database: {db_uri}")
    
    # Create engine
    engine = create_engine(db_uri)
    
    try:
        # Check database
        check_database(engine)
        
        # Create schema
        create_schema(engine, args.dry_run)
        
        logger.info("Migration completed successfully")
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
