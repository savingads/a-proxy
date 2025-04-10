"""
Service layer for persona operations
"""
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Persona, DemographicData, PsychographicData, BehavioralData, ContextualData

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
        
        # Process each persona to ensure JSON strings are properly loaded
        for persona in personas:
            self._process_json_fields(persona)
        
        return {
            'personas': personas,
            'total': total,
            'page': page,
            'per_page': per_page
        }
        
    def _process_json_fields(self, persona):
        """
        Process JSON fields for serialization without modifying the database objects
        Instead of updating the actual database objects, we add decoded properties
        that will be used only for serialization
        """
        # Create temporary attributes for psychographic data JSON fields
        if persona.psychographic:
            try:
                for field in ['interests', 'personal_values', 'attitudes', 'opinions']:
                    value = getattr(persona.psychographic, field)
                    if isinstance(value, str) and value:
                        # Create a new attribute with _decoded suffix that won't be saved to DB
                        setattr(persona.psychographic, f"{field}_decoded", json.loads(value))
            except (json.JSONDecodeError, TypeError):
                # If JSON is invalid, just leave as string
                pass
                
        # Create temporary attributes for behavioral data JSON fields
        if persona.behavioral:
            try:
                for field in ['browsing_habits', 'purchase_history', 'brand_interactions', 
                             'device_usage', 'social_media_activity', 'content_consumption']:
                    value = getattr(persona.behavioral, field)
                    if isinstance(value, str) and value:
                        # Create a new attribute with _decoded suffix that won't be saved to DB
                        setattr(persona.behavioral, f"{field}_decoded", json.loads(value))
            except (json.JSONDecodeError, TypeError):
                # If JSON is invalid, just leave as string
                pass
    
    def get_persona_by_id(self, persona_id):
        """Get a specific persona by ID"""
        persona = self.session.query(Persona).filter(Persona.id == persona_id).first()
        if persona:
            self._process_json_fields(persona)
        return persona
    
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
            psycho_data = persona_data['psychographic']
            psychographic = PsychographicData(
                persona_id=persona.id,
                interests=json.dumps(psycho_data.get('interests', [])),
                personal_values=json.dumps(psycho_data.get('personal_values', [])),
                attitudes=json.dumps(psycho_data.get('attitudes', [])),
                lifestyle=psycho_data.get('lifestyle'),
                personality=psycho_data.get('personality'),
                opinions=json.dumps(psycho_data.get('opinions', []))
            )
            self.session.add(psychographic)
            persona.psychographic = psychographic
        
        # Create behavioral data if provided
        if 'behavioral' in persona_data:
            behav_data = persona_data['behavioral']
            behavioral = BehavioralData(
                persona_id=persona.id,
                browsing_habits=json.dumps(behav_data.get('browsing_habits', [])),
                purchase_history=json.dumps(behav_data.get('purchase_history', [])),
                brand_interactions=json.dumps(behav_data.get('brand_interactions', [])),
                device_usage=json.dumps(behav_data.get('device_usage', {})),
                social_media_activity=json.dumps(behav_data.get('social_media_activity', {})),
                content_consumption=json.dumps(behav_data.get('content_consumption', {}))
            )
            self.session.add(behavioral)
            persona.behavioral = behavioral
        
        # Create contextual data if provided
        if 'contextual' in persona_data:
            context_data = persona_data['contextual']
            contextual = ContextualData(
                persona_id=persona.id,
                time_of_day=context_data.get('time_of_day'),
                day_of_week=context_data.get('day_of_week'),
                season=context_data.get('season'),
                weather=context_data.get('weather'),
                device_type=context_data.get('device_type'),
                browser_type=context_data.get('browser_type'),
                screen_size=context_data.get('screen_size'),
                connection_type=context_data.get('connection_type')
            )
            self.session.add(contextual)
            persona.contextual = contextual
        
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
            psycho_data = persona_data['psychographic']
            
            # Create if it doesn't exist
            if not persona.psychographic:
                persona.psychographic = PsychographicData(persona_id=persona.id)
                self.session.add(persona.psychographic)
            
            # Update fields
            for field in ['lifestyle', 'personality']:
                if field in psycho_data:
                    setattr(persona.psychographic, field, psycho_data[field])
            
            # Update JSON fields
            for field in ['interests', 'personal_values', 'attitudes', 'opinions']:
                if field in psycho_data:
                    setattr(persona.psychographic, field, json.dumps(psycho_data[field]))
        
        # Update behavioral data if provided
        if 'behavioral' in persona_data:
            behav_data = persona_data['behavioral']
            
            # Create if it doesn't exist
            if not persona.behavioral:
                persona.behavioral = BehavioralData(persona_id=persona.id)
                self.session.add(persona.behavioral)
            
            # Update JSON fields
            for field in ['browsing_habits', 'purchase_history', 'brand_interactions',
                         'device_usage', 'social_media_activity', 'content_consumption']:
                if field in behav_data:
                    setattr(persona.behavioral, field, json.dumps(behav_data[field]))
        
        # Update contextual data if provided
        if 'contextual' in persona_data:
            context_data = persona_data['contextual']
            
            # Create if it doesn't exist
            if not persona.contextual:
                persona.contextual = ContextualData(persona_id=persona.id)
                self.session.add(persona.contextual)
            
            # Update fields
            for field in ['time_of_day', 'day_of_week', 'season', 'weather',
                         'device_type', 'browser_type', 'screen_size', 'connection_type']:
                if field in context_data:
                    setattr(persona.contextual, field, context_data[field])
        
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
    
    def update_psychographic_data(self, persona_id, psychographic_data):
        """Update psychographic data for a persona"""
        persona = self.get_persona_by_id(persona_id)
        if not persona:
            return None
        
        if not persona.psychographic:
            persona.psychographic = PsychographicData(persona_id=persona.id)
            self.session.add(persona.psychographic)
        
        # Update fields
        for field in ['lifestyle', 'personality']:
            if field in psychographic_data:
                setattr(persona.psychographic, field, psychographic_data[field])
        
        # Update JSON fields
        for field in ['interests', 'personal_values', 'attitudes', 'opinions']:
            if field in psychographic_data:
                setattr(persona.psychographic, field, json.dumps(psychographic_data[field]))
        
        persona.updated_at = datetime.utcnow()
        self.session.commit()
        return persona.psychographic
    
    def update_behavioral_data(self, persona_id, behavioral_data):
        """Update behavioral data for a persona"""
        persona = self.get_persona_by_id(persona_id)
        if not persona:
            return None
        
        if not persona.behavioral:
            persona.behavioral = BehavioralData(persona_id=persona.id)
            self.session.add(persona.behavioral)
        
        # Update JSON fields
        for field in ['browsing_habits', 'purchase_history', 'brand_interactions',
                     'device_usage', 'social_media_activity', 'content_consumption']:
            if field in behavioral_data:
                setattr(persona.behavioral, field, json.dumps(behavioral_data[field]))
        
        persona.updated_at = datetime.utcnow()
        self.session.commit()
        return persona.behavioral
    
    def update_contextual_data(self, persona_id, contextual_data):
        """Update contextual data for a persona"""
        persona = self.get_persona_by_id(persona_id)
        if not persona:
            return None
        
        if not persona.contextual:
            persona.contextual = ContextualData(persona_id=persona.id)
            self.session.add(persona.contextual)
        
        # Update fields
        for field in ['time_of_day', 'day_of_week', 'season', 'weather',
                     'device_type', 'browser_type', 'screen_size', 'connection_type']:
            if field in contextual_data:
                setattr(persona.contextual, field, contextual_data[field])
        
        persona.updated_at = datetime.utcnow()
        self.session.commit()
        return persona.contextual
