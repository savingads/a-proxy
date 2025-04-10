"""
Field configuration for persona attributes

This file defines the configuration for persona attributes, 
allowing for dynamic rendering and processing of persona data.
"""

PERSONA_FIELD_CONFIG = {
    "psychographic": {
        "label": "Psychographic",
        "description": "Psychological attributes, interests, and values",
        "fields": [
            {
                "name": "interests",
                "type": "list",
                "label": "Interests",
                "description": "Personal interests and hobbies"
            },
            {
                "name": "personal_values",
                "type": "list",
                "label": "Personal Values",
                "description": "Core values the persona prioritizes"
            },
            {
                "name": "attitudes",
                "type": "list",
                "label": "Attitudes",
                "description": "General outlook and attitudes"
            },
            {
                "name": "lifestyle",
                "type": "string",
                "label": "Lifestyle",
                "description": "Overall lifestyle description"
            },
            {
                "name": "personality",
                "type": "string",
                "label": "Personality",
                "description": "Personality traits and characteristics"
            },
            {
                "name": "opinions",
                "type": "list",
                "label": "Opinions",
                "description": "Specific viewpoints on relevant topics"
            }
        ]
    },
    "behavioral": {
        "label": "Behavioral",
        "description": "Online behavior and usage patterns",
        "fields": [
            {
                "name": "browsing_habits",
                "type": "list",
                "label": "Browsing Habits",
                "description": "Types of websites frequently visited"
            },
            {
                "name": "purchase_history",
                "type": "list",
                "label": "Purchase History",
                "description": "Types of products/services purchased"
            },
            {
                "name": "brand_interactions",
                "type": "list",
                "label": "Brand Interactions",
                "description": "Brands frequently engaged with"
            },
            {
                "name": "device_usage",
                "type": "dict",
                "label": "Device Usage",
                "description": "How different devices are used"
            },
            {
                "name": "social_media_activity",
                "type": "dict",
                "label": "Social Media Activity",
                "description": "Engagement with social platforms"
            },
            {
                "name": "content_consumption",
                "type": "dict",
                "label": "Content Consumption",
                "description": "Media consumption patterns"
            }
        ]
    },
    "contextual": {
        "label": "Contextual",
        "description": "Situational and environmental factors",
        "fields": [
            {
                "name": "time_of_day",
                "type": "string",
                "label": "Time of Day",
                "description": "When the persona is most active online",
                "options": ["morning", "afternoon", "evening", "night", "all day"]
            },
            {
                "name": "day_of_week",
                "type": "string",
                "label": "Day of Week",
                "description": "Which days the persona is most active",
                "options": ["weekday", "weekend", "all week"]
            },
            {
                "name": "season",
                "type": "string",
                "label": "Season",
                "description": "Seasonal context for the persona",
                "options": ["spring", "summer", "fall", "winter"]
            },
            {
                "name": "weather",
                "type": "string",
                "label": "Weather",
                "description": "Weather conditions affecting the persona"
            },
            {
                "name": "device_type",
                "type": "string",
                "label": "Device Type",
                "description": "Primary device used",
                "options": ["desktop", "laptop", "tablet", "mobile"]
            },
            {
                "name": "browser_type",
                "type": "string",
                "label": "Browser Type",
                "description": "Primary web browser used",
                "options": ["chrome", "firefox", "safari", "edge"]
            },
            {
                "name": "screen_size",
                "type": "string",
                "label": "Screen Size",
                "description": "Display resolution, e.g. 1920x1080"
            },
            {
                "name": "connection_type",
                "type": "string",
                "label": "Connection Type",
                "description": "Internet connection",
                "options": ["wifi", "ethernet", "4g", "5g", "3g"]
            }
        ]
    }
}

def get_field_config(category=None, field_name=None):
    """
    Get field configuration data
    
    Args:
        category (str, optional): Category to retrieve (psychographic, behavioral, contextual)
        field_name (str, optional): Specific field name to retrieve
        
    Returns:
        dict: Configuration data for the requested scope
    """
    if not category:
        return PERSONA_FIELD_CONFIG
        
    if category not in PERSONA_FIELD_CONFIG:
        return {}
        
    if not field_name:
        return PERSONA_FIELD_CONFIG[category]
        
    # Find specific field in category
    for field in PERSONA_FIELD_CONFIG[category]["fields"]:
        if field["name"] == field_name:
            return field
            
    return {}

def load_custom_config(config_path):
    """
    Load a custom field configuration from a file
    
    Args:
        config_path (str): Path to the JSON configuration file
        
    Returns:
        dict: Custom field configuration
    """
    import json
    import os
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
    try:
        with open(config_path, 'r') as file:
            custom_config = json.load(file)
            
        # Basic validation
        required_categories = ["psychographic", "behavioral", "contextual"]
        for category in required_categories:
            if category not in custom_config:
                raise ValueError(f"Missing required category: {category}")
                
            if "fields" not in custom_config[category]:
                raise ValueError(f"Missing 'fields' key in category: {category}")
                
        return custom_config
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON in configuration file")
