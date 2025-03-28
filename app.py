from flask import Flask
import logging
import argparse
from config import SECRET_KEY, SESSION_COOKIE_SECURE, SESSION_COOKIE_HTTPONLY, SESSION_COOKIE_SAMESITE

# Import blueprints
from routes.home import home_bp
from routes.vpn import vpn_bp
from routes.persona import persona_bp
from routes.browsing import browsing_bp
from routes.archives import archives_bp

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
    
    return app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the Flask application')
    parser.add_argument('--port', type=int, default=5001, help='Port to run the application on')
    args = parser.parse_args()
    
    app = create_app()
    app.run(debug=True, use_reloader=True, port=args.port)
