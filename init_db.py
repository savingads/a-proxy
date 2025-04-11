#!/usr/bin/env python3

"""
Script to initialize the persona service database.
"""

import os
import sys

# Make sure the persona-service directory is in the Python path
sys.path.insert(0, 'persona-service')

def init_database():
    """Initialize the database with the proper schema"""
    # Set the database path environment variable
    db_path = os.path.abspath('persona-service/instance/persona_service.db')
    os.environ['DATABASE_URI'] = f'sqlite:///{db_path}'
    
    print(f"Initializing database at: {db_path}")
    
    # Make sure the directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Import the init_db function from the models module
    from app.models import init_db
    
    # Initialize the database
    session = init_db()
    print("Database initialization complete!")
    session.close()

if __name__ == "__main__":
    init_database()
