"""
API routes for the Persona Service
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.config import SQLALCHEMY_DATABASE_URI, API_VERSION
from app.models import init_db, Persona
from app.services import PersonaService
from app.schemas import (
    persona_schema, 
    personas_schema, 
    demographic_schema, 
    psychographic_schema, 
    behavioral_schema, 
    contextual_schema,
    error_schema
)

# Create blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix=f'/api/{API_VERSION}')

# Database session
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

# Helper functions
def get_service():
    """Get a new service instance with a fresh session"""
    session = Session()
    return PersonaService(session)

def handle_error(error_msg, status_code=400, errors=None):
    """Create a standardized error response"""
    response = {
        'message': error_msg,
        'status_code': status_code
    }
    if errors:
        response['errors'] = errors
    
    return jsonify(error_schema.dump(response)), status_code

# Routes for personas
@api_bp.route('/personas', methods=['GET'])
def get_personas():
    """Get all personas with pagination"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Input validation
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20
        
        session = Session()
        
        try:
            # Get personas directly from the database
            personas = session.query(Persona).order_by(
                Persona.updated_at.desc()
            ).offset((page - 1) * per_page).limit(per_page).all()
            
            total = session.query(Persona).count()
            
            # Manually serialize each persona using the schema
            serialized_personas = []
            for persona in personas:
                try:
                    serialized = persona_schema.dump(persona)
                    serialized_personas.append(serialized)
                except Exception as e:
                    current_app.logger.error(f"Error serializing persona {persona.id}: {str(e)}")
            
            # Return the serialized data
            return jsonify({
                'personas': serialized_personas,
                'total': total,
                'page': page,
                'per_page': per_page
            }), 200
        finally:
            session.close()
    
    except Exception as e:
        current_app.logger.error(f"Error getting personas: {str(e)}")
        return handle_error("Failed to retrieve personas", 500)

@api_bp.route('/personas/<int:persona_id>', methods=['GET'])
def get_persona(persona_id):
    """Get a specific persona by ID"""
    try:
        service = get_service()
        persona = service.get_persona_by_id(persona_id)
        
        if not persona:
            return handle_error(f"Persona with ID {persona_id} not found", 404)
        
        return jsonify(persona_schema.dump(persona)), 200
    
    except Exception as e:
        current_app.logger.error(f"Error getting persona {persona_id}: {str(e)}")
        return handle_error(f"Failed to retrieve persona with ID {persona_id}", 500)

@api_bp.route('/personas', methods=['POST'])
#@jwt_required()  # Uncomment when JWT is set up
def create_persona():
    """Create a new persona"""
    try:
        # Parse the request data
        json_data = request.get_json()
        if not json_data:
            return handle_error("No input data provided", 400)
        
        # Validate the data
        persona_data = persona_schema.load(json_data)
        
        # Create the persona
        service = get_service()
        persona = service.create_persona(persona_data)
        
        return jsonify(persona_schema.dump(persona)), 201
    
    except ValidationError as err:
        return handle_error("Validation error", 400, err.messages)
    
    except Exception as e:
        current_app.logger.error(f"Error creating persona: {str(e)}")
        return handle_error("Failed to create persona", 500)

@api_bp.route('/personas/<int:persona_id>', methods=['PUT'])
#@jwt_required()  # Uncomment when JWT is set up
def update_persona(persona_id):
    """Update an existing persona"""
    try:
        # Parse the request data
        json_data = request.get_json()
        if not json_data:
            return handle_error("No input data provided", 400)
        
        # Validate the data
        persona_data = persona_schema.load(json_data, partial=True)
        
        # Update the persona
        service = get_service()
        persona = service.update_persona(persona_id, persona_data)
        
        if not persona:
            return handle_error(f"Persona with ID {persona_id} not found", 404)
        
        return jsonify(persona_schema.dump(persona)), 200
    
    except ValidationError as err:
        return handle_error("Validation error", 400, err.messages)
    
    except Exception as e:
        current_app.logger.error(f"Error updating persona {persona_id}: {str(e)}")
        return handle_error(f"Failed to update persona with ID {persona_id}", 500)

@api_bp.route('/personas/<int:persona_id>', methods=['DELETE'])
#@jwt_required()  # Uncomment when JWT is set up
def delete_persona(persona_id):
    """Delete a persona"""
    try:
        service = get_service()
        success = service.delete_persona(persona_id)
        
        if not success:
            return handle_error(f"Persona with ID {persona_id} not found", 404)
        
        return jsonify({'message': f"Persona with ID {persona_id} deleted successfully"}), 200
    
    except Exception as e:
        current_app.logger.error(f"Error deleting persona {persona_id}: {str(e)}")
        return handle_error(f"Failed to delete persona with ID {persona_id}", 500)

# Routes for demographic data
@api_bp.route('/personas/<int:persona_id>/demographic', methods=['GET'])
def get_demographic_data(persona_id):
    """Get demographic data for a persona"""
    try:
        service = get_service()
        persona = service.get_persona_by_id(persona_id)
        
        if not persona:
            return handle_error(f"Persona with ID {persona_id} not found", 404)
        
        if not persona.demographic:
            return jsonify({}), 200
        
        return jsonify(demographic_schema.dump(persona.demographic)), 200
    
    except Exception as e:
        current_app.logger.error(f"Error getting demographic data for persona {persona_id}: {str(e)}")
        return handle_error(f"Failed to retrieve demographic data for persona with ID {persona_id}", 500)

@api_bp.route('/personas/<int:persona_id>/demographic', methods=['PUT'])
#@jwt_required()  # Uncomment when JWT is set up
def update_demographic_data(persona_id):
    """Update demographic data for a persona"""
    try:
        # Parse the request data
        json_data = request.get_json()
        if not json_data:
            return handle_error("No input data provided", 400)
        
        # Validate the data
        demographic_data = demographic_schema.load(json_data)
        
        # Update the demographic data
        service = get_service()
        demographic = service.update_demographic_data(persona_id, demographic_data)
        
        if not demographic:
            return handle_error(f"Persona with ID {persona_id} not found", 404)
        
        return jsonify(demographic_schema.dump(demographic)), 200
    
    except ValidationError as err:
        return handle_error("Validation error", 400, err.messages)
    
    except Exception as e:
        current_app.logger.error(f"Error updating demographic data for persona {persona_id}: {str(e)}")
        return handle_error(f"Failed to update demographic data for persona with ID {persona_id}", 500)

# Routes for psychographic data
@api_bp.route('/personas/<int:persona_id>/psychographic', methods=['GET'])
def get_psychographic_data(persona_id):
    """Get psychographic data for a persona"""
    try:
        service = get_service()
        persona = service.get_persona_by_id(persona_id)
        
        if not persona:
            return handle_error(f"Persona with ID {persona_id} not found", 404)
        
        if not persona.psychographic:
            return jsonify({}), 200
        
        return jsonify(psychographic_schema.dump(persona.psychographic)), 200
    
    except Exception as e:
        current_app.logger.error(f"Error getting psychographic data for persona {persona_id}: {str(e)}")
        return handle_error(f"Failed to retrieve psychographic data for persona with ID {persona_id}", 500)

@api_bp.route('/personas/<int:persona_id>/psychographic', methods=['PUT'])
#@jwt_required()  # Uncomment when JWT is set up
def update_psychographic_data(persona_id):
    """Update psychographic data for a persona"""
    try:
        # Parse the request data
        json_data = request.get_json()
        if not json_data:
            return handle_error("No input data provided", 400)
        
        # Validate the data
        psychographic_data = psychographic_schema.load(json_data)
        
        # Update the psychographic data
        service = get_service()
        psychographic = service.update_psychographic_data(persona_id, psychographic_data)
        
        if not psychographic:
            return handle_error(f"Persona with ID {persona_id} not found", 404)
        
        return jsonify(psychographic_schema.dump(psychographic)), 200
    
    except ValidationError as err:
        return handle_error("Validation error", 400, err.messages)
    
    except Exception as e:
        current_app.logger.error(f"Error updating psychographic data for persona {persona_id}: {str(e)}")
        return handle_error(f"Failed to update psychographic data for persona with ID {persona_id}", 500)

# Routes for behavioral data
@api_bp.route('/personas/<int:persona_id>/behavioral', methods=['GET'])
def get_behavioral_data(persona_id):
    """Get behavioral data for a persona"""
    try:
        service = get_service()
        persona = service.get_persona_by_id(persona_id)
        
        if not persona:
            return handle_error(f"Persona with ID {persona_id} not found", 404)
        
        if not persona.behavioral:
            return jsonify({}), 200
        
        return jsonify(behavioral_schema.dump(persona.behavioral)), 200
    
    except Exception as e:
        current_app.logger.error(f"Error getting behavioral data for persona {persona_id}: {str(e)}")
        return handle_error(f"Failed to retrieve behavioral data for persona with ID {persona_id}", 500)

@api_bp.route('/personas/<int:persona_id>/behavioral', methods=['PUT'])
#@jwt_required()  # Uncomment when JWT is set up
def update_behavioral_data(persona_id):
    """Update behavioral data for a persona"""
    try:
        # Parse the request data
        json_data = request.get_json()
        if not json_data:
            return handle_error("No input data provided", 400)
        
        # Validate the data
        behavioral_data = behavioral_schema.load(json_data)
        
        # Update the behavioral data
        service = get_service()
        behavioral = service.update_behavioral_data(persona_id, behavioral_data)
        
        if not behavioral:
            return handle_error(f"Persona with ID {persona_id} not found", 404)
        
        return jsonify(behavioral_schema.dump(behavioral)), 200
    
    except ValidationError as err:
        return handle_error("Validation error", 400, err.messages)
    
    except Exception as e:
        current_app.logger.error(f"Error updating behavioral data for persona {persona_id}: {str(e)}")
        return handle_error(f"Failed to update behavioral data for persona with ID {persona_id}", 500)

# Routes for contextual data
@api_bp.route('/personas/<int:persona_id>/contextual', methods=['GET'])
def get_contextual_data(persona_id):
    """Get contextual data for a persona"""
    try:
        service = get_service()
        persona = service.get_persona_by_id(persona_id)
        
        if not persona:
            return handle_error(f"Persona with ID {persona_id} not found", 404)
        
        if not persona.contextual:
            return jsonify({}), 200
        
        return jsonify(contextual_schema.dump(persona.contextual)), 200
    
    except Exception as e:
        current_app.logger.error(f"Error getting contextual data for persona {persona_id}: {str(e)}")
        return handle_error(f"Failed to retrieve contextual data for persona with ID {persona_id}", 500)

@api_bp.route('/personas/<int:persona_id>/contextual', methods=['PUT'])
#@jwt_required()  # Uncomment when JWT is set up
def update_contextual_data(persona_id):
    """Update contextual data for a persona"""
    try:
        # Parse the request data
        json_data = request.get_json()
        if not json_data:
            return handle_error("No input data provided", 400)
        
        # Validate the data
        contextual_data = contextual_schema.load(json_data)
        
        # Update the contextual data
        service = get_service()
        contextual = service.update_contextual_data(persona_id, contextual_data)
        
        if not contextual:
            return handle_error(f"Persona with ID {persona_id} not found", 404)
        
        return jsonify(contextual_schema.dump(contextual)), 200
    
    except ValidationError as err:
        return handle_error("Validation error", 400, err.messages)
    
    except Exception as e:
        current_app.logger.error(f"Error updating contextual data for persona {persona_id}: {str(e)}")
        return handle_error(f"Failed to update contextual data for persona with ID {persona_id}", 500)
