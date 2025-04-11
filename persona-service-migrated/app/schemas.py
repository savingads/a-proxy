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

class DynamicAttributeSchema(Schema):
    """Schema for dynamic attribute data"""
    id = fields.Int(dump_only=True)
    persona_id = fields.Int(dump_only=True)
    data = fields.Dict(allow_none=True)
    
    # This is a flexible schema that adapts to the field configuration

class PersonaSchema(Schema):
    """Schema for persona data"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Related data
    demographic = fields.Nested(DemographicDataSchema(), allow_none=True)
    
    # Dynamic attribute categories
    psychographic = fields.Dict(allow_none=True)
    behavioral = fields.Dict(allow_none=True)
    contextual = fields.Dict(allow_none=True)
    
    # Override load/dump to handle dynamic attributes
    def dump(self, obj, **kwargs):
        """Override dump to handle dynamic attributes"""
        result = super().dump(obj, **kwargs)
        
        # Dynamic attributes are already handled in obj.to_dict()
        # which is used in the serialization process
        
        return result

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
error_schema = ErrorSchema()
