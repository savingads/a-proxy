"""
Persona Service - An API for managing user personas
"""
import os
import logging
import datetime
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
        try:
            # Check database connectivity
            if db.session:
                from sqlalchemy import text
                db.session.execute(text("SELECT 1")).first()
                db_status = "connected"
            else:
                db_status = "disconnected"
                
            return jsonify({
                'status': 'healthy',
                'database': db_status,
                'timestamp': datetime.datetime.utcnow().isoformat()
            })
        except Exception as e:
            app.logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.datetime.utcnow().isoformat()
            }), 500
    
    return app

def init_db(database_uri):
    """Initialize database connection"""
    try:
        # Make sure we have an absolute path for SQLite URI
        if database_uri.startswith('sqlite:///') and not database_uri.startswith('sqlite:////'):
            # Convert to absolute path in the data directory
            import os
            data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
            os.makedirs(data_dir, exist_ok=True)
            db_file = database_uri.replace('sqlite:///', '')
            database_uri = f'sqlite:///{os.path.join(data_dir, db_file)}'
            print(f"Using database at: {database_uri}")
            
        # Create engine and session
        engine = create_engine(database_uri)
        session_factory = sessionmaker(bind=engine)
        session = scoped_session(session_factory)
        
        # Store in db object
        db.engine = engine
        db.session = session
        
        # Import models to ensure they're registered with the engine
        from app.models import Base, Persona, DemographicData, PersonaAttributes
        
        # Create tables if they don't exist
        Base.metadata.create_all(engine)
        
        # Test if database is actually working
        from sqlalchemy import text
        session.execute(text("SELECT 1"))
        print("Database connection successful")
        
    except Exception as e:
        import traceback
        print(f"Database initialization failed: {str(e)}")
        print(traceback.format_exc())
        raise
