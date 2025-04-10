"""
Database models for the Persona Service
"""
from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

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
    psychographic = relationship("PsychographicData", uselist=False, back_populates="persona",
                                cascade="all, delete-orphan")
    behavioral = relationship("BehavioralData", uselist=False, back_populates="persona",
                             cascade="all, delete-orphan")
    contextual = relationship("ContextualData", uselist=False, back_populates="persona",
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
        
        if self.psychographic:
            result['psychographic'] = self.psychographic.to_dict()
            
        if self.behavioral:
            result['behavioral'] = self.behavioral.to_dict()
            
        if self.contextual:
            result['contextual'] = self.contextual.to_dict()
            
        return result

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

class PsychographicData(Base):
    """Psychographic data associated with a persona"""
    __tablename__ = 'psychographic_data'
    
    id = Column(Integer, primary_key=True)
    persona_id = Column(Integer, ForeignKey('personas.id', ondelete='CASCADE'), nullable=False)
    interests = Column(String)  # JSON string
    personal_values = Column(String)  # JSON string
    attitudes = Column(String)  # JSON string
    lifestyle = Column(String)
    personality = Column(String)
    opinions = Column(String)  # JSON string
    
    # Relationship
    persona = relationship("Persona", back_populates="psychographic")
    
    def to_dict(self):
        """Convert psychographic data to dictionary representation"""
        return {
            'id': self.id,
            'persona_id': self.persona_id,
            'interests': json.loads(self.interests) if self.interests else [],
            'personal_values': json.loads(self.personal_values) if self.personal_values else [],
            'attitudes': json.loads(self.attitudes) if self.attitudes else [],
            'lifestyle': self.lifestyle,
            'personality': self.personality,
            'opinions': json.loads(self.opinions) if self.opinions else []
        }

class BehavioralData(Base):
    """Behavioral data associated with a persona"""
    __tablename__ = 'behavioral_data'
    
    id = Column(Integer, primary_key=True)
    persona_id = Column(Integer, ForeignKey('personas.id', ondelete='CASCADE'), nullable=False)
    browsing_habits = Column(String)  # JSON string
    purchase_history = Column(String)  # JSON string
    brand_interactions = Column(String)  # JSON string
    device_usage = Column(String)  # JSON string
    social_media_activity = Column(String)  # JSON string
    content_consumption = Column(String)  # JSON string
    
    # Relationship
    persona = relationship("Persona", back_populates="behavioral")
    
    def to_dict(self):
        """Convert behavioral data to dictionary representation"""
        return {
            'id': self.id,
            'persona_id': self.persona_id,
            'browsing_habits': json.loads(self.browsing_habits) if self.browsing_habits else [],
            'purchase_history': json.loads(self.purchase_history) if self.purchase_history else [],
            'brand_interactions': json.loads(self.brand_interactions) if self.brand_interactions else [],
            'device_usage': json.loads(self.device_usage) if self.device_usage else {},
            'social_media_activity': json.loads(self.social_media_activity) if self.social_media_activity else {},
            'content_consumption': json.loads(self.content_consumption) if self.content_consumption else {}
        }

class ContextualData(Base):
    """Contextual data associated with a persona"""
    __tablename__ = 'contextual_data'
    
    id = Column(Integer, primary_key=True)
    persona_id = Column(Integer, ForeignKey('personas.id', ondelete='CASCADE'), nullable=False)
    time_of_day = Column(String)
    day_of_week = Column(String)
    season = Column(String)
    weather = Column(String)
    device_type = Column(String)
    browser_type = Column(String)
    screen_size = Column(String)
    connection_type = Column(String)
    
    # Relationship
    persona = relationship("Persona", back_populates="contextual")
    
    def to_dict(self):
        """Convert contextual data to dictionary representation"""
        return {
            'id': self.id,
            'persona_id': self.persona_id,
            'time_of_day': self.time_of_day,
            'day_of_week': self.day_of_week,
            'season': self.season,
            'weather': self.weather,
            'device_type': self.device_type,
            'browser_type': self.browser_type,
            'screen_size': self.screen_size,
            'connection_type': self.connection_type
        }

def init_db(db_uri=None):
    """Initialize the database and create tables"""
    from app.config import SQLALCHEMY_DATABASE_URI
    engine = create_engine(db_uri or SQLALCHEMY_DATABASE_URI)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
