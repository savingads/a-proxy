"""
Marshmallow schemas for request/response validation and serialization
"""
from marshmallow import Schema, fields, validate, validates, ValidationError, post_load
import re

class DemographicDataSchema(Schema):
    """Schema for demographic data"""
    id = fields.Int(dump_only=True)
    persona_id = fields.Int(dump_only=True)
    latitude = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)
    language = fields.Str(allow_none=True)
    country = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    region = fields.Str(allow_none=True)
    age = fields.Int(allow_none=True, validate=validate.Range(min=0, max=120))
    gender = fields.Str(allow_none=True)
    education = fields.Str(allow_none=True)
    income = fields.Str(allow_none=True)
    occupation = fields.Str(allow_none=True)
    
    # Special handling for geolocation string (used in request)
    geolocation = fields.Str(allow_none=True, load_only=True)
    
    @validates('geolocation')
    def validate_geolocation(self, value):
        """Validate geolocation string"""
        if not value:
            return
        
        # Regex to match latitude,longitude format
        geo_pattern = r'^-?\d+(\.\d+)?,\s*-?\d+(\.\d+)?$'
        if not re.match(geo_pattern, value):
            raise ValidationError('Geolocation must be in format "latitude,longitude"')
    
    @post_load
    def process_geolocation(self, data, **kwargs):
        """Process geolocation string into latitude and longitude"""
        geolocation = data.pop('geolocation', None)
        if geolocation and ',' in geolocation:
            try:
                lat_str, lng_str = geolocation.split(',', 1)
                data['latitude'] = float(lat_str.strip())
                data['longitude'] = float(lng_str.strip())
            except (ValueError, TypeError):
                pass
        
        return data

class PsychographicDataSchema(Schema):
    """Schema for psychographic data"""
    id = fields.Int(dump_only=True)
    persona_id = fields.Int(dump_only=True)
    interests = fields.List(fields.Str(), allow_none=True)
    personal_values = fields.List(fields.Str(), allow_none=True)
    attitudes = fields.List(fields.Str(), allow_none=True)
    lifestyle = fields.Str(allow_none=True)
    personality = fields.Str(allow_none=True)
    opinions = fields.List(fields.Str(), allow_none=True)
    
    def dump(self, obj, **kwargs):
        """Override dump to use decoded fields if available"""
        result = super().dump(obj, **kwargs)
        
        # Use decoded fields if they exist
        for field in ['interests', 'personal_values', 'attitudes', 'opinions']:
            decoded_field = f"{field}_decoded"
            if hasattr(obj, decoded_field) and getattr(obj, decoded_field) is not None:
                result[field] = getattr(obj, decoded_field)
        
        return result

class BehavioralDataSchema(Schema):
    """Schema for behavioral data"""
    id = fields.Int(dump_only=True)
    persona_id = fields.Int(dump_only=True)
    browsing_habits = fields.List(fields.Str(), allow_none=True)
    purchase_history = fields.List(fields.Str(), allow_none=True)
    brand_interactions = fields.List(fields.Str(), allow_none=True)
    device_usage = fields.Dict(keys=fields.Str(), values=fields.Str(), allow_none=True)
    social_media_activity = fields.Dict(keys=fields.Str(), values=fields.Str(), allow_none=True)
    content_consumption = fields.Dict(keys=fields.Str(), values=fields.Str(), allow_none=True)
    
    def dump(self, obj, **kwargs):
        """Override dump to use decoded fields if available"""
        result = super().dump(obj, **kwargs)
        
        # Use decoded fields if they exist
        for field in ['browsing_habits', 'purchase_history', 'brand_interactions',
                     'device_usage', 'social_media_activity', 'content_consumption']:
            decoded_field = f"{field}_decoded"
            if hasattr(obj, decoded_field) and getattr(obj, decoded_field) is not None:
                result[field] = getattr(obj, decoded_field)
        
        return result

class ContextualDataSchema(Schema):
    """Schema for contextual data"""
    id = fields.Int(dump_only=True)
    persona_id = fields.Int(dump_only=True)
    time_of_day = fields.Str(allow_none=True)
    day_of_week = fields.Str(allow_none=True)
    season = fields.Str(allow_none=True)
    weather = fields.Str(allow_none=True)
    device_type = fields.Str(allow_none=True)
    browser_type = fields.Str(allow_none=True)
    screen_size = fields.Str(allow_none=True)
    connection_type = fields.Str(allow_none=True)

class PersonaSchema(Schema):
    """Schema for persona data"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Related data
    demographic = fields.Nested(DemographicDataSchema(), allow_none=True)
    psychographic = fields.Nested(PsychographicDataSchema(), allow_none=True)
    behavioral = fields.Nested(BehavioralDataSchema(), allow_none=True)
    contextual = fields.Nested(ContextualDataSchema(), allow_none=True)

# Schemas for API requests/responses
class PersonaListResponseSchema(Schema):
    """Schema for list of personas response"""
    personas = fields.List(fields.Nested(PersonaSchema()))
    total = fields.Int()
    page = fields.Int()
    per_page = fields.Int()
    
class ErrorSchema(Schema):
    """Schema for error responses"""
    message = fields.Str(required=True)
    errors = fields.Dict(keys=fields.Str(), values=fields.List(fields.Str()))
    status_code = fields.Int()

# Create specific instances for common use
persona_schema = PersonaSchema()
personas_schema = PersonaSchema(many=True)
demographic_schema = DemographicDataSchema()
psychographic_schema = PsychographicDataSchema()
behavioral_schema = BehavioralDataSchema()
contextual_schema = ContextualDataSchema()
error_schema = ErrorSchema()
