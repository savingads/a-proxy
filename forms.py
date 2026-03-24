from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, HiddenField
from wtforms.validators import Optional

class PersonaForm(FlaskForm):
    # Hidden field for persona ID
    persona_id = HiddenField()
    
    # Demographic fields
    persona_name = StringField('Persona Name')
    geolocation = StringField('Geolocation')
    language = StringField('Language')
    country = StringField('Country')
    city = StringField('City')
    region = StringField('Region')
    
    # Psychographic fields
    interests = StringField('Interests', validators=[Optional()])
    personal_values = StringField('Personal Values', validators=[Optional()])
    attitudes = StringField('Attitudes', validators=[Optional()])
    lifestyle = StringField('Lifestyle', validators=[Optional()])
    personality = StringField('Personality', validators=[Optional()])
    opinions = StringField('Opinions', validators=[Optional()])
    
    # Behavioral fields
    browsing_habits = StringField('Browsing Habits', validators=[Optional()])
    purchase_history = StringField('Purchase History', validators=[Optional()])
    brand_interactions = StringField('Brand Interactions', validators=[Optional()])
    device_usage = TextAreaField('Device Usage', validators=[Optional()])
    social_media_activity = TextAreaField('Social Media Activity', validators=[Optional()])
    content_consumption = TextAreaField('Content Consumption', validators=[Optional()])
    
    # Contextual fields
    time_of_day = SelectField('Time of Day', choices=[
        ('', 'Select time of day'), 
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        ('night', 'Night')
    ], validators=[Optional()])
    
    day_of_week = SelectField('Day of Week', choices=[
        ('', 'Select day of week'),
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday')
    ], validators=[Optional()])
    
    season = SelectField('Season', choices=[
        ('', 'Select season'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('fall', 'Fall'),
        ('winter', 'Winter')
    ], validators=[Optional()])
    
    weather = StringField('Weather', validators=[Optional()])
    
    device_type = SelectField('Device Type', choices=[
        ('', 'Select device type'),
        ('desktop', 'Desktop'),
        ('laptop', 'Laptop'),
        ('tablet', 'Tablet'),
        ('mobile', 'Mobile')
    ], validators=[Optional()])
    
    browser_type = SelectField('Browser Type', choices=[
        ('', 'Select browser type'),
        ('chrome', 'Chrome'),
        ('firefox', 'Firefox'),
        ('safari', 'Safari'),
        ('edge', 'Edge')
    ], validators=[Optional()])
    
    screen_size = StringField('Screen Size', validators=[Optional()])
    
    connection_type = SelectField('Connection Type', choices=[
        ('', 'Select connection type'),
        ('wifi', 'WiFi'),
        ('ethernet', 'Ethernet'),
        ('4g', '4G'),
        ('5g', '5G')
    ], validators=[Optional()])
