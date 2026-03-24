from flask import Flask
import logging
import argparse
from config import SECRET_KEY, SESSION_COOKIE_SECURE, SESSION_COOKIE_HTTPONLY, SESSION_COOKIE_SAMESITE

# Import blueprints
from routes.home import home_bp
from routes.vpn import vpn_bp
# Use the mock implementation instead of the real API
from routes.persona_api_mock import persona_bp  # Mock implementation that doesn't require API service
from routes.browsing import browsing_bp
from routes.archives import archives_bp
from routes.journey import journey_bp

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure Flask application
    app.secret_key = SECRET_KEY
    app.config['SESSION_COOKIE_SECURE'] = SESSION_COOKIE_SECURE
    app.config['SESSION_COOKIE_HTTPONLY'] = SESSION_COOKIE_HTTPONLY
    app.config['SESSION_COOKIE_SAMESITE'] = SESSION_COOKIE_SAMESITE
    
    # Register blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(vpn_bp)
    app.register_blueprint(persona_bp)
    app.register_blueprint(browsing_bp)
    app.register_blueprint(archives_bp)
    app.register_blueprint(journey_bp)
    
    return app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the Flask application')
    parser.add_argument('--port', type=int, default=5002, help='Port to run the application on')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host address to run the application on')
    args = parser.parse_args()
    
    app = create_app()
    app.run(debug=True, use_reloader=True, port=args.port, host=args.host)
