"""
Persona Service - An API for managing user personas
"""
import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Create db object to be imported by other modules
db = type('DB', (), {'session': None, 'engine': None})

def create_app(config_filename=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    if config_filename:
        app.config.from_pyfile(config_filename)
    else:
        from app.config import (
            SQLALCHEMY_DATABASE_URI, 
            JWT_SECRET_KEY, 
            JWT_ACCESS_TOKEN_EXPIRES,
            JWT_REFRESH_TOKEN_EXPIRES,
            CORS_ORIGINS
        )
        
        app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
        app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = JWT_ACCESS_TOKEN_EXPIRES
        app.config['JWT_REFRESH_TOKEN_EXPIRES'] = JWT_REFRESH_TOKEN_EXPIRES
    
    # Configure logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    
    # Initialize extensions
    CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}})
    jwt = JWTManager(app)
    
    # Initialize database
    init_db(app.config.get('SQLALCHEMY_DATABASE_URI'))
    
    # Import routes here to avoid circular imports
    from app.routes import api_blueprint
    
    # Register blueprints
    app.register_blueprint(api_blueprint)
    
    # Register error handlers
    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({'message': 'Not found', 'status_code': 404}), 404
    
    @app.errorhandler(500)
    def handle_500(e):
        app.logger.error(f"Server error: {str(e)}")
        return jsonify({'message': 'Internal server error', 'status_code': 500}), 500
    
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring"""
        return jsonify({'status': 'healthy'})
    
    return app

def init_db(database_uri):
    """Initialize database connection"""
    # Create engine and session
    engine = create_engine(database_uri)
    session_factory = sessionmaker(bind=engine)
    session = scoped_session(session_factory)
    
    # Store in db object
    db.engine = engine
    db.session = session
    
    # Import models to ensure they're registered with the engine
    from app.models import Base, Persona, DemographicData, PsychographicData, BehavioralData, ContextualData
    
    # Create tables if they don't exist
    Base.metadata.create_all(engine)
