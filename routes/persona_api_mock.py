"""
Routes for persona API integration with dynamic field support and mock client
"""
import json
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, abort, session
from utils.persona_client_mock import get_mock_persona_client
import persona_field_config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint definition
persona_bp = Blueprint('persona', __name__, url_prefix='')

# Use mock client instead of real API client
def get_persona_client():
    """Get mock persona client instance"""
    return get_mock_persona_client()

@persona_bp.route('/personas')
def list_personas():
    """List all personas"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 100, type=int)
    
    try:
        client = get_persona_client()
        result = client.get_personas(page=page, per_page=per_page)
        return render_template('personas.html', personas=result.get('personas', []))
    except Exception as e:
        logger.error(f"Error listing personas: {str(e)}")
        flash(f"Error listing personas: {str(e)}", 'danger')
        return render_template('personas.html', personas=[])

@persona_bp.route('/persona/<int:persona_id>')
def view_persona(persona_id):
    """View a specific persona"""
    try:
        client = get_persona_client()
        persona = client.get_persona(persona_id)
        
        # Handle non-existent persona
        if not persona:
            flash('Persona not found', 'danger')
            return redirect(url_for('persona.list_personas'))
        
        # Get geolocation and language for display
        geolocation = ""
        language = ""
        
        if 'demographic' in persona:
            if persona['demographic'].get('latitude') and persona['demographic'].get('longitude'):
                geolocation = f"{persona['demographic']['latitude']},{persona['demographic']['longitude']}"
            language = persona['demographic'].get('language', '')
        
        # Get field configuration
        field_config = persona_field_config.get_field_config()
        
        return render_template('persona_view_dynamic.html', 
                              persona=persona,
                              persona_id=persona_id,
                              persona_name=persona.get('name', 'Unnamed'),
                              geolocation=geolocation,
                              language=language,
                              field_config=field_config)
    except Exception as e:
        logger.error(f"Error viewing persona {persona_id}: {str(e)}")
        flash(f"Error viewing persona: {str(e)}", 'danger')
        return redirect(url_for('persona.list_personas'))

@persona_bp.route('/create-persona', methods=['GET', 'POST'])
def create_persona():
    """Create a new persona"""
    if request.method == 'POST':
        try:
            # Get form data
            data = request.form.to_dict()
            
            # Build persona data structure
            persona_data = {
                'name': data.get('persona_name', 'Unnamed Persona'),
                'demographic': {
                    'latitude': float(data.get('latitude')) if data.get('latitude') else None,
                    'longitude': float(data.get('longitude')) if data.get('longitude') else None,
                    'language': data.get('language'),
                    'country': data.get('country'),
                    'city': data.get('city'),
                    'region': data.get('region'),
                    'age': int(data.get('age')) if data.get('age') else None,
                    'gender': data.get('gender'),
                    'education': data.get('education'),
                    'income': data.get('income'),
                    'occupation': data.get('occupation')
                }
            }
            
            # Process dynamic field categories
            for category in ['psychographic', 'behavioral', 'contextual']:
                category_data = {}
                category_config = persona_field_config.get_field_config(category)
                
                if category_config and 'fields' in category_config:
                    for field_def in category_config['fields']:
                        field_name = field_def['name']
                        field_type = field_def['type']
                        form_field_name = f"{category}_{field_name}"
                        
                        if form_field_name in data and data[form_field_name]:
                            # Process based on field type
                            if field_type == 'list':
                                # Split comma-separated values and strip whitespace
                                value = [item.strip() for item in data[form_field_name].split(',') if item.strip()]
                                category_data[field_name] = value
                            elif field_type == 'dict':
                                # Try to parse as JSON, or leave as string
                                try:
                                    value = json.loads(data[form_field_name])
                                    category_data[field_name] = value
                                except json.JSONDecodeError:
                                    # Fallback to key:value parsing
                                    items = [item.strip() for item in data[form_field_name].split(',') if item.strip()]
                                    value_dict = {}
                                    for item in items:
                                        if ':' in item:
                                            k, v = item.split(':', 1)
                                            value_dict[k.strip()] = v.strip()
                                    category_data[field_name] = value_dict
                            else:
                                # String value
                                category_data[field_name] = data[form_field_name]
                
                # Add category data if not empty
                if category_data:
                    persona_data[category] = category_data
            
            # Create persona
            client = get_persona_client()
            result = client.create_persona(persona_data)
            
            flash('Persona created successfully', 'success')
            return redirect(url_for('persona.view_persona', persona_id=result['id']))
        
        except Exception as e:
            logger.error(f"Error creating persona: {str(e)}")
            flash(f"Error creating persona: {str(e)}", 'danger')
            return redirect(url_for('persona.list_personas'))
    
    # Handle GET request - render form template
    # Get field configuration
    field_config = persona_field_config.get_field_config()
    return render_template('persona_edit.html', 
                         persona=None,
                         form={},
                         persona_id=None,
                         field_config=field_config,
                         is_new=True)

@persona_bp.route('/edit-persona/<int:persona_id>', methods=['GET', 'POST'])
def edit_persona(persona_id):
    """Edit an existing persona"""
    client = get_persona_client()
    
    if request.method == 'POST':
        try:
            # Get form data
            data = request.form.to_dict()
            
            # Build persona data structure
            persona_data = {
                'name': data.get('persona_name', 'Unnamed Persona'),
                'demographic': {
                    'latitude': float(data.get('latitude')) if data.get('latitude') else None,
                    'longitude': float(data.get('longitude')) if data.get('longitude') else None,
                    'language': data.get('language'),
                    'country': data.get('country'),
                    'city': data.get('city'),
                    'region': data.get('region'),
                    'age': int(data.get('age')) if data.get('age') else None,
                    'gender': data.get('gender'),
                    'education': data.get('education'),
                    'income': data.get('income'),
                    'occupation': data.get('occupation')
                }
            }
            
            # Process dynamic field categories
            for category in ['psychographic', 'behavioral', 'contextual']:
                category_data = {}
                category_config = persona_field_config.get_field_config(category)
                
                if category_config and 'fields' in category_config:
                    for field_def in category_config['fields']:
                        field_name = field_def['name']
                        field_type = field_def['type']
                        form_field_name = f"{category}_{field_name}"
                        
                        if form_field_name in data:
                            # Process based on field type
                            if field_type == 'list':
                                if data[form_field_name]:
                                    # Split comma-separated values and strip whitespace
                                    value = [item.strip() for item in data[form_field_name].split(',') if item.strip()]
                                    category_data[field_name] = value
                                else:
                                    # Empty list
                                    category_data[field_name] = []
                            elif field_type == 'dict':
                                if data[form_field_name]:
                                    # Try to parse as JSON, or leave as string
                                    try:
                                        value = json.loads(data[form_field_name])
                                        category_data[field_name] = value
                                    except json.JSONDecodeError:
                                        # Fallback to key:value parsing
                                        items = [item.strip() for item in data[form_field_name].split(',') if item.strip()]
                                        value_dict = {}
                                        for item in items:
                                            if ':' in item:
                                                k, v = item.split(':', 1)
                                                value_dict[k.strip()] = v.strip()
                                        category_data[field_name] = value_dict
                                else:
                                    # Empty dict
                                    category_data[field_name] = {}
                            else:
                                # String value
                                category_data[field_name] = data[form_field_name]
                
                # Add category data if not empty
                if category_data:
                    persona_data[category] = category_data
            
            # Update persona
            result = client.update_persona(persona_id, persona_data)
            
            flash('Persona updated successfully', 'success')
            return redirect(url_for('persona.view_persona', persona_id=persona_id))
        
        except Exception as e:
            logger.error(f"Error updating persona {persona_id}: {str(e)}")
            flash(f"Error updating persona: {str(e)}", 'danger')
            return redirect(url_for('persona.view_persona', persona_id=persona_id))
    
    # Handle GET request
    try:
        # Get existing persona
        persona = client.get_persona(persona_id)
        
        # Prepare form data
        form = {
            'persona_name': persona.get('name', ''),
        }
        
        # Add demographic data
        if 'demographic' in persona:
            demographic = persona['demographic']
            for field in ['latitude', 'longitude', 'language', 'country', 'city', 
                         'region', 'age', 'gender', 'education', 'income', 'occupation']:
                form[field] = demographic.get(field, '')
        
        # Add dynamic category data
        for category in ['psychographic', 'behavioral', 'contextual']:
            if category in persona:
                category_data = persona[category]
                category_config = persona_field_config.get_field_config(category)
                
                if category_config and 'fields' in category_config:
                    for field_def in category_config['fields']:
                        field_name = field_def['name']
                        field_type = field_def['type']
                        form_field_name = f"{category}_{field_name}"
                        
                        if field_name in category_data:
                            value = category_data[field_name]
                            
                            # Format based on field type
                            if field_type == 'list' and isinstance(value, list):
                                form[form_field_name] = ', '.join(str(item) for item in value)
                            elif field_type == 'dict' and isinstance(value, dict):
                                # Convert dict to comma-separated key:value pairs
                                form[form_field_name] = ', '.join(f"{k}: {v}" for k, v in value.items())
                            else:
                                form[form_field_name] = value
        
        # Get field configuration
        field_config = persona_field_config.get_field_config()
        
        return render_template('persona_edit.html', 
                             persona=persona,
                             form=form,
                             persona_id=persona_id,
                             field_config=field_config,
                             is_new=False)
    except Exception as e:
        logger.error(f"Error getting persona {persona_id} for editing: {str(e)}")
        flash(f"Error loading persona: {str(e)}", 'danger')
        return redirect(url_for('persona.list_personas'))

@persona_bp.route('/delete-persona/<int:persona_id>', methods=['POST'])
def delete_persona(persona_id):
    """Delete a persona"""
    try:
        client = get_persona_client()
        result = client.delete_persona(persona_id)
        
        flash('Persona deleted successfully', 'success')
        return redirect(url_for('persona.list_personas'))
    except Exception as e:
        logger.error(f"Error deleting persona {persona_id}: {str(e)}")
        flash(f"Error deleting persona: {str(e)}", 'danger')
        return redirect(url_for('persona.list_personas'))

@persona_bp.route('/use-persona/<int:persona_id>')
def use_persona(persona_id):
    """Set a persona as active"""
    try:
        client = get_persona_client()
        persona = client.get_persona(persona_id)
        
        # Store active persona in session
        if 'active_persona' not in session:
            session['active_persona'] = {}
        session['active_persona'] = persona
        
        # Extract geolocation and language
        geolocation = None
        language = None
        
        if 'demographic' in persona:
            demographic = persona['demographic']
            if demographic.get('latitude') and demographic.get('longitude'):
                geolocation = f"{demographic['latitude']},{demographic['longitude']}"
            language = demographic.get('language')
        
        session['geolocation'] = geolocation
        session['language'] = language
        
        flash(f'Now using persona: {persona.get("name")}', 'success')
        return redirect(url_for('persona.view_persona', persona_id=persona_id))
    except Exception as e:
        logger.error(f"Error using persona {persona_id}: {str(e)}")
        flash(f"Error using persona: {str(e)}", 'danger')
        return redirect(url_for('persona.list_personas'))

@persona_bp.route('/field-config')
def get_field_config():
    """Get field configuration as JSON"""
    category = request.args.get('category')
    field_name = request.args.get('field')
    
    config = persona_field_config.get_field_config(category, field_name)
    return jsonify(config)
