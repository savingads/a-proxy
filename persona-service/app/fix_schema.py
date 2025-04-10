#!/usr/bin/env python3
"""
Script to fix the Persona API server schema issue
"""
import json
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.config import SQLALCHEMY_DATABASE_URI
from app.models import Persona
from app.schemas import persona_schema

# Database session
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

def verify_schema():
    """Verify that the schema serialization works correctly"""
    print("Checking schema serialization...")
    
    # Create a session
    session = Session()
    
    # Get personas
    personas = session.query(Persona).all()
    
    print(f"Found {len(personas)} personas")
    
    # Try to serialize them
    for persona in personas:
        try:
            # Test serializing individual persona
            serialized = persona_schema.dump(persona)
            print(f"Successfully serialized persona {persona.id}: {serialized.get('name')}")
        except Exception as e:
            print(f"Error serializing persona {persona.id}: {str(e)}")
            
    # Close session
    session.close()
    
    print("Schema check completed")

if __name__ == "__main__":
    verify_schema()
