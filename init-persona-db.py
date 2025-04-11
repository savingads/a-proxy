#!/usr/bin/env python3

"""
Script to initialize the persona service database.
This script fixes the syntax errors in the models.py file and
initializes the database.
"""

import os
import sys
import re

def fix_models_file():
    """Fix syntax errors in the models.py file"""
    models_path = "persona-service/app/models.py"
    
    print(f"Fixing syntax errors in {models_path}...")
    
    # Read the file content
    with open(models_path, 'r') as f:
        content = f.read()
    
    # Fix missing commas in imports
    content = re.sub(r'from sqlalchemy import Column Integer', 'from sqlalchemy import Column, Integer', content)
    content = re.sub(r'String Float ForeignKey', 'String, Float, ForeignKey', content)
    content = re.sub(r'DateTime Text Enum', 'DateTime, Text, Enum', content)
    
    # Fix missing commas in class properties
    content = re.sub(r"'id': self.id\n", "'id': self.id,\n", content)
    content = re.sub(r"'name': self.name\n", "'name': self.name,\n", content)
    content = re.sub(r"'created_at': self.created_at", "'created_at': self.created_at,", content)
    
    # Fix other missing commas
    content = re.sub(r'demographic = relationship\("DemographicData" uselist=False', 
                     'demographic = relationship("DemographicData", uselist=False', content)
    content = re.sub(r'back_populates="persona"\n', 'back_populates="persona",\n', content)
    content = re.sub(r'attributes = relationship\("PersonaAttributes" back_populates="persona"',
                     'attributes = relationship("PersonaAttributes", back_populates="persona"', content)
    
    content = re.sub(r"primary_key=True\)", "primary_key=True)", content)
    content = re.sub(r"Column\(String nullable=False\)", "Column(String, nullable=False)", content)
    content = re.sub(r"Column\(DateTime default=datetime.utcnow\)", 
                    "Column(DateTime, default=datetime.utcnow)", content)
    content = re.sub(r"default=datetime.utcnow onupdate=datetime.utcnow", 
                    "default=datetime.utcnow, onupdate=datetime.utcnow", content)
    
    content = re.sub(r"attributes_by_category\['psychographic' 'behavioral' 'contextual'\]", 
                    "attributes_by_category['psychographic', 'behavioral', 'contextual']", content)
    
    content = re.sub(r"get_attribute_by_category\(self category\):", 
                    "get_attribute_by_category(self, category):", content)
    content = re.sub(r"if isinstance\(category str\):", 
                    "if isinstance(category, str):", content)
    
    content = re.sub(r"ForeignKey\('personas.id' ondelete='CASCADE'\)", 
                    "ForeignKey('personas.id', ondelete='CASCADE')", content)
    content = re.sub(r"nullable=False\)", "nullable=False)", content)
    
    content = re.sub(r"persona = relationship\(\"Persona\" back_populates=", 
                    "persona = relationship(\"Persona\", back_populates=", content)
    
    content = re.sub(r"persona_id = Column\(Integer ForeignKey\('personas.id' ondelete='CASCADE'\)", 
                    "persona_id = Column(Integer, ForeignKey('personas.id', ondelete='CASCADE')", content)
    content = re.sub(r"category = Column\(Enum\(AttributeCategory\) nullable=False\)", 
                    "category = Column(Enum(AttributeCategory), nullable=False)", content)
    content = re.sub(r"data = Column\(Text nullable=False default='\{\}'\)", 
                    "data = Column(Text, nullable=False, default='{}')", content)
    
    content = re.sub(r"def __init__\(self persona_id category data=None\):", 
                    "def __init__(self, persona_id, category, data=None):", content)
    content = re.sub(r"if isinstance\(category str\):", 
                    "if isinstance(category, str):", content)
    content = re.sub(r"isinstance\(self.category AttributeCategory\)", 
                    "isinstance(self.category, AttributeCategory)", content)
    
    content = re.sub(r"def set_data\(self data\):", 
                    "def set_data(self, data):", content)
    content = re.sub(r"if isinstance\(data dict\):", 
                    "if isinstance(data, dict):", content)
    content = re.sub(r"elif isinstance\(data str\):", 
                    "elif isinstance(data, str):", content)
    
    content = re.sub(r"def get_value\(self field_name\):", 
                    "def get_value(self, field_name):", content)
    content = re.sub(r"def set_value\(self field_name value\):", 
                    "def set_value(self, field_name, value):", content)
    
    # Write the updated content back to the file
    with open(models_path, 'w') as f:
        f.write(content)
    
    print("Syntax errors fixed!")

def init_database():
    """Initialize the database"""
    print("Initializing database...")
    
    # Set the necessary environment variables
    db_path = os.path.abspath(os.path.join("persona-service", "instance", "persona_service.db"))
    os.environ["DATABASE_URI"] = f"sqlite:///{db_path}"
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Create a simple Python script to import and run the init_db function
    init_script = """
import sys
sys.path.insert(0, 'persona-service')
from app.models import init_db

# Initialize the database
session = init_db()
print("Database initialized successfully!")
session.close()
"""
    
    # Write the script to a temporary file
    with open("temp_init_db.py", "w") as f:
        f.write(init_script)
    
    # Execute the script
    try:
        os.system(f"{sys.executable} temp_init_db.py")
        print(f"Database created at: {db_path}")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        # Clean up the temporary script
        try:
            os.remove("temp_init_db.py")
        except:
            pass

if __name__ == "__main__":
    print("Starting initialization process...")
    fix_models_file()
    init_database()
    print("Initialization complete!")
