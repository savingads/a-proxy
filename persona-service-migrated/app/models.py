"""
Database models for the Persona Service
"""
from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Enum, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import enum

Base = declarative_base()

class AttributeCategory(enum.Enum):
    """Enum for persona attribute categories"""
    PSYCHOGRAPHIC = "psychographic"
    BEHAVIORAL = "behavioral"
    CONTEXTUAL = "contextual"

class Persona(Base):
    """Persona model representing a user profile"""
    __tablename__ = 'personas'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    demographic = relationship("DemographicData", uselist=False, back_populates="persona",
                               cascade="all, delete-orphan")
    
    # Relationship to PersonaAttributes
    attributes = relationship("PersonaAttributes", back_populates="persona",
                           cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert persona to dictionary representation"""
        result = {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if self.demographic:
            result['demographic'] = self.demographic.to_dict()
        
        # Group attributes by category
        attributes_by_category = {}
        for attr in self.attributes:
            category = attr.category.value if isinstance(attr.category, AttributeCategory) else attr.category
            attributes_by_category[category] = attr.to_dict()
        
        # Add each category to the result
        for category in ['psychographic', 'behavioral', 'contextual']:
            if category in attributes_by_category:
                result[category] = attributes_by_category[category]
            
        return result
    
    def get_attribute_by_category(self, category):
        """Get persona attributes by category"""
        if isinstance(category, str):
            category = category.lower()
            for attr in self.attributes:
                if attr.category.value == category:
                    return attr
        else:
            for attr in self.attributes:
                if attr.category == category:
                    return attr
        return None

class DemographicData(Base):
    """Demographic data associated with a persona"""
    __tablename__ = 'demographic_data'
    
    id = Column(Integer, primary_key=True)
    persona_id = Column(Integer, ForeignKey('personas.id', ondelete='CASCADE'), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    language = Column(String)
    country = Column(String)
    city = Column(String)
    region = Column(String)
    age = Column(Integer)
    gender = Column(String)
    education = Column(String)
    income = Column(String)
    occupation = Column(String)
    
    # Relationship
    persona = relationship("Persona", back_populates="demographic")
    
    def to_dict(self):
        """Convert demographic data to dictionary representation"""
        return {
            'id': self.id,
            'persona_id': self.persona_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'language': self.language,
            'country': self.country,
            'city': self.city,
            'region': self.region,
            'age': self.age,
            'gender': self.gender,
            'education': self.education,
            'income': self.income,
            'occupation': self.occupation
        }

class PersonaAttributes(Base):
    """Dynamic attributes for a persona (psychographic, behavioral, contextual)"""
    __tablename__ = 'persona_attributes'
    
    id = Column(Integer, primary_key=True)
    persona_id = Column(Integer, ForeignKey('personas.id', ondelete='CASCADE'), nullable=False)
    category = Column(Enum(AttributeCategory), nullable=False)
    data = Column(Text, nullable=False, default='{}')  # JSON text blob
    
    # Relationship
    persona = relationship("Persona", back_populates="attributes")
    
    def __init__(self, persona_id, category, data=None):
        """Initialize with persona_id, category and optional data"""
        self.persona_id = persona_id
        
        # Handle string or enum for category
        if isinstance(category, str):
            category = category.lower()
            if category == 'psychographic':
                self.category = AttributeCategory.PSYCHOGRAPHIC
            elif category == 'behavioral':
                self.category = AttributeCategory.BEHAVIORAL
            elif category == 'contextual':
                self.category = AttributeCategory.CONTEXTUAL
            else:
                raise ValueError(f"Invalid category: {category}")
        else:
            self.category = category
            
        # Handle data initialization
        if data is None:
            self.data = '{}'
        elif isinstance(data, str):
            # Validate it's a JSON string
            try:
                json.loads(data)
                self.data = data
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON data")
        elif isinstance(data, dict):
            self.data = json.dumps(data)
        else:
            raise TypeError("Data must be a dictionary or JSON string")
    
    def get_data(self):
        """Get data as a Python dictionary"""
        try:
            return json.loads(self.data)
        except json.JSONDecodeError:
            return {}
    
    def set_data(self, data):
        """Set data from a Python dictionary"""
        if isinstance(data, dict):
            self.data = json.dumps(data)
        elif isinstance(data, str):
            try:
                # Validate it's a proper JSON string
                json.loads(data)
                self.data = data
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON data")
        else:
            raise TypeError("Data must be a dictionary or JSON string")
    
    def get_value(self, field_name):
        """Get a specific field value from the data"""
        data_dict = self.get_data()
        return data_dict.get(field_name)
    
    def set_value(self, field_name, value):
        """Set a specific field value in the data"""
        data_dict = self.get_data()
        data_dict[field_name] = value
        self.set_data(data_dict)
    
    def to_dict(self):
        """Convert to dictionary representation"""
        return self.get_data()

def init_db(db_uri=None):
    """Initialize the database and create tables"""
    from app.config import SQLALCHEMY_DATABASE_URI
    engine = create_engine(db_uri or SQLALCHEMY_DATABASE_URI)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
