"""
API routes for persona service with dynamic field support
"""
import json
import logging
from flask import Blueprint, jsonify, request, current_app
from http import HTTPStatus
from app.services_updated import PersonaService
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
api_blueprint = Blueprint('api', __name__, url_prefix='/api/v1')

# Helper function to get database session
def get_db_session():
    """Get a database session"""
    return db.session

@api_blueprint.route('/personas', methods=['GET'])
def get_personas():
    """Get all personas with pagination"""
    # Parse pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Get personas from service
    try:
        service = PersonaService(get_db_session())
        result = service.get_all_personas(page=page, per_page=per_page)
        
        # Convert personas to dictionaries
        personas_dict = []
        for persona in result['personas']:
            try:
                personas_dict.append(persona.to_dict())
            except Exception as e:
                logger.error(f"Error serializing persona {persona.id}: {str(e)}")
        
        return jsonify({
            'personas': personas_dict,
            'total': result['total'],
            'page': result['page'],
            'per_page': result['per_page'],
            'pages': (result['total'] + per_page - 1) // per_page
        }), HTTPStatus.OK
    except Exception as e:
        logger.error(f"Error getting personas: {str(e)}")
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@api_blueprint.route('/personas/<int:persona_id>', methods=['GET'])
def get_persona(persona_id):
    """Get a specific persona by ID"""
    try:
        service = PersonaService(get_db_session())
        persona = service.get_persona_by_id(persona_id)
        
        if not persona:
            return jsonify({'error': 'Persona not found'}), HTTPStatus.NOT_FOUND
            
        return jsonify(persona.to_dict()), HTTPStatus.OK
    except Exception as e:
        logger.error(f"Error getting persona {persona_id}: {str(e)}")
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@api_blueprint.route('/personas', methods=['POST'])
def create_persona():
    """Create a new persona"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), HTTPStatus.BAD_REQUEST
        
        # Basic validation
        if 'name' not in data:
            return jsonify({'error': 'Name is required'}), HTTPStatus.BAD_REQUEST
            
        # Validate data for categories if provided
        service = PersonaService(get_db_session())
        for category in ['psychographic', 'behavioral', 'contextual']:
            if category in data:
                is_valid, error = service.validate_category_data(category, data[category])
                if not is_valid:
                    return jsonify({'error': f'Invalid {category} data', 'details': error}), HTTPStatus.BAD_REQUEST
        
        # Create persona
        persona = service.create_persona(data)
        
        return jsonify(persona.to_dict()), HTTPStatus.CREATED
    except Exception as e:
        logger.error(f"Error creating persona: {str(e)}")
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@api_blueprint.route('/personas/<int:persona_id>', methods=['PUT', 'PATCH'])
def update_persona(persona_id):
    """Update a persona"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), HTTPStatus.BAD_REQUEST
            
        # Validate data for categories if provided
        service = PersonaService(get_db_session())
        for category in ['psychographic', 'behavioral', 'contextual']:
            if category in data:
                is_valid, error = service.validate_category_data(category, data[category])
                if not is_valid:
                    return jsonify({'error': f'Invalid {category} data', 'details': error}), HTTPStatus.BAD_REQUEST
        
        # Update persona
        persona = service.update_persona(persona_id, data)
        
        if not persona:
            return jsonify({'error': 'Persona not found'}), HTTPStatus.NOT_FOUND
            
        return jsonify(persona.to_dict()), HTTPStatus.OK
    except Exception as e:
        logger.error(f"Error updating persona {persona_id}: {str(e)}")
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@api_blueprint.route('/personas/<int:persona_id>', methods=['DELETE'])
def delete_persona(persona_id):
    """Delete a persona"""
    try:
        service = PersonaService(get_db_session())
        result = service.delete_persona(persona_id)
        
        if not result:
            return jsonify({'error': 'Persona not found'}), HTTPStatus.NOT_FOUND
            
        return jsonify({'message': f'Persona {persona_id} deleted successfully'}), HTTPStatus.OK
    except Exception as e:
        logger.error(f"Error deleting persona {persona_id}: {str(e)}")
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@api_blueprint.route('/field-config', methods=['GET'])
def get_field_config():
    """Get field configuration"""
    try:
        category = request.args.get('category')
        field_name = request.args.get('field')
        
        service = PersonaService(get_db_session())
        config = service.get_field_config(category, field_name)
        
        return jsonify(config), HTTPStatus.OK
    except Exception as e:
        logger.error(f"Error getting field config: {str(e)}")
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@api_blueprint.route('/personas/<int:persona_id>/attributes/<category>', methods=['GET'])
def get_persona_attributes(persona_id, category):
    """Get attributes for a persona by category"""
    try:
        if category not in ['psychographic', 'behavioral', 'contextual']:
            return jsonify({'error': f'Invalid category: {category}'}), HTTPStatus.BAD_REQUEST
            
        service = PersonaService(get_db_session())
        data = service.get_attribute_data(persona_id, category)
        
        if data is None:
            return jsonify({'error': 'Persona not found'}), HTTPStatus.NOT_FOUND
            
        return jsonify(data), HTTPStatus.OK
    except Exception as e:
        logger.error(f"Error getting {category} data for persona {persona_id}: {str(e)}")
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@api_blueprint.route('/personas/<int:persona_id>/attributes/<category>', methods=['PUT', 'PATCH'])
def update_persona_attributes(persona_id, category):
    """Update attributes for a persona by category"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), HTTPStatus.BAD_REQUEST
            
        if category not in ['psychographic', 'behavioral', 'contextual']:
            return jsonify({'error': f'Invalid category: {category}'}), HTTPStatus.BAD_REQUEST
            
        # Validate data
        service = PersonaService(get_db_session())
        is_valid, error = service.validate_category_data(category, data)
        if not is_valid:
            return jsonify({'error': f'Invalid {category} data', 'details': error}), HTTPStatus.BAD_REQUEST
            
        # Update data
        attr = service.update_attribute_data(persona_id, category, data)
        
        if attr is None:
            return jsonify({'error': 'Persona not found'}), HTTPStatus.NOT_FOUND
            
        return jsonify(attr.get_data()), HTTPStatus.OK
    except Exception as e:
        logger.error(f"Error updating {category} data for persona {persona_id}: {str(e)}")
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
