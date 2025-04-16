#!/bin/bash

# Script to restore the persona-service/init_db.py file if it gets deleted during git operations

INIT_DB_PATH="persona-service/init_db.py"

# Check if the file exists
if [ ! -f "$INIT_DB_PATH" ]; then
    echo "Restoring persona-service/init_db.py file..."
    
    # Create the init_db.py file
    cat > "$INIT_DB_PATH" << 'EOF'
#!/usr/bin/env python3
"""
Database initialization script for the Persona Service
"""
import os
import sys
from pathlib import Path

# Ensure the data directory exists
data_dir = Path(__file__).resolve().parent / 'data'
data_dir.mkdir(exist_ok=True)

# Import initialization function from models
from app.models import init_db
from app.config import SQLALCHEMY_DATABASE_URI

def main():
    print("Starting database initialization...")
    print(f"Initializing database with URI: {SQLALCHEMY_DATABASE_URI}")
    
    # Initialize the database
    session = init_db()
    
    # Check if tables were created
    from sqlalchemy import inspect
    inspector = inspect(session.bind)
    tables = inspector.get_table_names()
    print(f"Existing tables: {' '.join(tables)}")
    
    # Close session
    session.close()
    
    print("Database initialized successfully!")

if __name__ == "__main__":
    main()
EOF

    # Make the file executable
    chmod +x "$INIT_DB_PATH"
    
    echo "Persona service init_db.py file has been restored!"
else
    echo "Persona service init_db.py file already exists."
fi
