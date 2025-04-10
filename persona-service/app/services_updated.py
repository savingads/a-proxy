"""
Service layer for persona operations with dynamic attribute support
"""
import json
import sys
import os
from datetime import datetime
from sqlalchemy.orm import Session
from app.models_updated import (
    Persona, DemographicData, PersonaAttributes, 
    AttributeCategory, PsychographicData, BehavioralData, ContextualData
)

# Add the parent directory to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import persona_field_config

class PersonaService:
    """Service class for persona operations"""
    
    def __init__(self, session: Session):
        """Initialize with database session"""
        self.session = session
    
    def get_all_personas(self, page=1, per_page=20):
        """Get all personas with pagination"""
        personas = self.session.query(Persona).order_by(
            Persona.updated_at.desc()
        ).offset((page - 1) * per_page).limit(per_page).all()
        
        total = self.session.query(Persona).count()
        
        return {
            'personas': personas,
            'total': total,
            'page': page,
            'per_page': per_page
        }
    
    def get_persona_by_id(self, persona_id):
        """Get a specific persona by ID"""
        return self.session.query(Persona).filter(Persona.id == persona_id).first()
    
    def _create_attribute(self, persona_id, category, data):
        """Create a new attribute record for a persona"""
        attr = PersonaAttributes(
            persona_id=persona_id,
            category=category,
            data=data or {}
        )
        self.session.add(attr)
        return attr
    
    def create_persona(self, persona_data):
        """Create a new persona with related data"""
        # Create main persona
        persona = Persona(
            name=persona_data.get('name', 'Unnamed Persona'),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.session.add(persona)
        self.session.flush()  # To get the persona ID
        
        # Create demographic data if provided
        if 'demographic' in persona_data:
            demo_data = persona_data['demographic']
            demographic = DemographicData(
                persona_id=persona.id,
                latitude=demo_data.get('latitude'),
                longitude=demo_data.get('longitude'),
                language=demo_data.get('language'),
                country=demo_data.get('country'),
                city=demo_data.get('city'),
                region=demo_data.get('region'),
                age=demo_data.get('age'),
                gender=demo_data.get('gender'),
                education=demo_data.get('education'),
                income=demo_data.get('income'),
                occupation=demo_data.get('occupation')
            )
            self.session.add(demographic)
            persona.demographic = demographic
        
        # Create psychographic data if provided
        if 'psychographic' in persona_data:
            self._create_attribute(
                persona_id=persona.id,
                category=AttributeCategory.PSYCHOGRAPHIC,
                data=persona_data['psychographic']
            )
        
        # Create behavioral data if provided
        if 'behavioral' in persona_data:
            self._create_attribute(
                persona_id=persona.id,
                category=AttributeCategory.BEHAVIORAL,
                data=persona_data['behavioral']
            )
        
        # Create contextual data if provided
        if 'contextual' in persona_data:
            self._create_attribute(
                persona_id=persona.id,
                category=AttributeCategory.CONTEXTUAL,
                data=persona_data['contextual']
            )
        
        self.session.commit()
        return persona
    
    def update_persona(self, persona_id, persona_data):
        """Update an existing persona"""
        persona = self.get_persona_by_id(persona_id)
        if not persona:
            return None
        
        # Update main persona attributes
        if 'name' in persona_data:
            persona.name = persona_data['name']
        
        persona.updated_at = datetime.utcnow()
        
        # Update demographic data if provided
        if 'demographic' in persona_data:
            demo_data = persona_data['demographic']
            
            # Create if it doesn't exist
            if not persona.demographic:
                persona.demographic = DemographicData(persona_id=persona.id)
                self.session.add(persona.demographic)
            
            # Update fields
            for field in ['latitude', 'longitude', 'language', 'country', 'city', 
                         'region', 'age', 'gender', 'education', 'income', 'occupation']:
                if field in demo_data:
                    setattr(persona.demographic, field, demo_data[field])
        
        # Update psychographic data if provided
        if 'psychographic' in persona_data:
            self.update_attribute_data(
                persona_id=persona.id,
                category=AttributeCategory.PSYCHOGRAPHIC,
                data=persona_data['psychographic']
            )
        
        # Update behavioral data if provided
        if 'behavioral' in persona_data:
            self.update_attribute_data(
                persona_id=persona.id,
                category=AttributeCategory.BEHAVIORAL,
                data=persona_data['behavioral']
            )
        
        # Update contextual data if provided
        if 'contextual' in persona_data:
            self.update_attribute_data(
                persona_id=persona.id,
                category=AttributeCategory.CONTEXTUAL,
                data=persona_data['contextual']
            )
        
        self.session.commit()
        return persona
    
    def delete_persona(self, persona_id):
        """Delete a persona and all its associated data"""
        persona = self.get_persona_by_id(persona_id)
        if not persona:
            return False
        
        self.session.delete(persona)
        self.session.commit()
        return True
    
    def update_demographic_data(self, persona_id, demographic_data):
        """Update demographic data for a persona"""
        persona = self.get_persona_by_id(persona_id)
        if not persona:
            return None
        
        if not persona.demographic:
            persona.demographic = DemographicData(persona_id=persona.id)
            self.session.add(persona.demographic)
        
        # Update fields
        for field in ['latitude', 'longitude', 'language', 'country', 'city', 
                     'region', 'age', 'gender', 'education', 'income', 'occupation']:
            if field in demographic_data:
                setattr(persona.demographic, field, demographic_data[field])
        
        persona.updated_at = datetime.utcnow()
        self.session.commit()
        return persona.demographic
    
    def get_attribute_data(self, persona_id, category):
        """Get attribute data for a specific category"""
        persona = self.get_persona_by_id(persona_id)
        if not persona:
            return None
        
        # Find attribute for category
        attr = persona.get_attribute_by_category(category)
        if not attr:
            return {}
        
        return attr.get_data()
    
    def update_attribute_data(self, persona_id, category, data):
        """Update attribute data for a specific category"""
        persona = self.get_persona_by_id(persona_id)
        if not persona:
            return None
        
        # Find or create attribute for category
        attr = persona.get_attribute_by_category(category)
        if not attr:
            attr = self._create_attribute(persona_id, category, {})
            
        # Update data
        if data:
            current_data = attr.get_data()
            # Merge with existing data
            for key, value in data.items():
                current_data[key] = value
                
            attr.set_data(current_data)
        
        persona.updated_at = datetime.utcnow()
        self.session.commit()
        return attr
    
    def get_field_config(self, category=None, field_name=None):
        """Get field configuration"""
        return persona_field_config.get_field_config(category, field_name)
    
    def validate_category_data(self, category, data):
        """Validate data against field configuration"""
        if category not in ['psychographic', 'behavioral', 'contextual']:
            return False, f"Invalid category: {category}"
        
        if not isinstance(data, dict):
            return False, "Data must be a dictionary"
        
        # Get configuration for this category
        config = self.get_field_config(category)
        if not config:
            return False, f"No configuration found for category: {category}"
        
        # Validate each field
        errors = []
        for field_def in config.get('fields', []):
            field_name = field_def.get('name')
            field_type = field_def.get('type')
            
            # Skip validation if field is not in data
            if field_name not in data:
                continue
                
            value = data[field_name]
            
            # Validate field based on type
            if field_type == 'list' and not isinstance(value, list):
                errors.append(f"Field '{field_name}' must be a list")
            elif field_type == 'dict' and not isinstance(value, dict):
                errors.append(f"Field '{field_name}' must be a dictionary")
            elif field_type == 'string' and value is not None and not isinstance(value, str):
                errors.append(f"Field '{field_name}' must be a string")
                
            # Validate options if defined
            if 'options' in field_def and value is not None and value not in field_def['options']:
                errors.append(f"Field '{field_name}' must be one of: {', '.join(field_def['options'])}")
        
        if errors:
            return False, errors
        
        return True, None
    
    # Legacy methods for backward compatibility
    def update_psychographic_data(self, persona_id, psychographic_data):
        """Update psychographic data for a persona"""
        return self.update_attribute_data(persona_id, AttributeCategory.PSYCHOGRAPHIC, psychographic_data)
    
    def update_behavioral_data(self, persona_id, behavioral_data):
        """Update behavioral data for a persona"""
        return self.update_attribute_data(persona_id, AttributeCategory.BEHAVIORAL, behavioral_data)
    
    def update_contextual_data(self, persona_id, contextual_data):
        """Update contextual data for a persona"""
        return self.update_attribute_data(persona_id, AttributeCategory.CONTEXTUAL, contextual_data)
