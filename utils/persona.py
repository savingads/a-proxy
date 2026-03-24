import json

class FormObject:
    """A simple object to populate form fields from dictionary data."""
    def __init__(self, data=None):
        if data:
            for key, value in data.items():
                setattr(self, key, value)

def prepare_form_object(persona):
    """Create a form object from persona data for use with WTForms' obj parameter."""
    form_obj = FormObject()
    
    # Set basic fields
    form_obj.persona_id = persona.get('id', '')
    form_obj.persona_name = persona.get('name', '')
    
    # Set demographic data
    demographic = persona.get('demographic', {})
    
    # Combine latitude and longitude into geolocation string if they exist
    latitude = demographic.get('latitude')
    longitude = demographic.get('longitude')
    if latitude is not None and longitude is not None:
        form_obj.geolocation = f"{latitude}, {longitude}"
    else:
        form_obj.geolocation = demographic.get('geolocation', '')
    
    form_obj.language = demographic.get('language', 'en-US')
    form_obj.country = demographic.get('country', '')
    form_obj.city = demographic.get('city', '')
    form_obj.region = demographic.get('region', '')
    
    # Set psychographic data
    if 'psychographic' in persona:
        psycho = persona['psychographic']
        form_obj.interests = ', '.join(psycho.get('interests', []))
        form_obj.personal_values = ', '.join(psycho.get('personal_values', []))
        form_obj.attitudes = ', '.join(psycho.get('attitudes', []))
        form_obj.lifestyle = psycho.get('lifestyle', '')
        form_obj.personality = psycho.get('personality', '')
        form_obj.opinions = ', '.join(psycho.get('opinions', []))
    
    # Set behavioral data
    if 'behavioral' in persona:
        behav = persona['behavioral']
        form_obj.browsing_habits = ', '.join(behav.get('browsing_habits', []))
        form_obj.purchase_history = ', '.join(behav.get('purchase_history', []))
        form_obj.brand_interactions = ', '.join(behav.get('brand_interactions', []))
        form_obj.device_usage = json.dumps(behav.get('device_usage', {}), indent=2)
        form_obj.social_media_activity = json.dumps(behav.get('social_media_activity', {}), indent=2)
        form_obj.content_consumption = json.dumps(behav.get('content_consumption', {}), indent=2)
    
    # Set contextual data
    if 'contextual' in persona:
        context = persona['contextual']
        form_obj.time_of_day = context.get('time_of_day', '')
        form_obj.day_of_week = context.get('day_of_week', '')
        form_obj.season = context.get('season', '')
        form_obj.weather = context.get('weather', '')
        form_obj.device_type = context.get('device_type', '')
        form_obj.browser_type = context.get('browser_type', '')
        form_obj.screen_size = context.get('screen_size', '')
        form_obj.connection_type = context.get('connection_type', '')
    
    return form_obj
