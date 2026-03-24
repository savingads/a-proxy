from flask import Flask
import logging
import argparse
from config import SECRET_KEY, SESSION_COOKIE_SECURE, SESSION_COOKIE_HTTPONLY, SESSION_COOKIE_SAMESITE
from flask_login import LoginManager
from database import get_user_by_email
from routes.auth import User, user_from_row

# Import blueprints
from routes.home import home_bp
from routes.vpn import vpn_bp
# Choose which persona implementation to use (API or direct DB access)
from routes.persona_api_db import persona_bp  # Using direct database implementation
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
    
    # Add custom Jinja2 filters
    import json
    @app.template_filter('fromjson')
    def fromjson_filter(value):
        """Convert a JSON string to a Python object"""
        try:
            return json.loads(value)
        except:
            return {}
    
    # --- Flask-Login setup ---
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Custom unauthorized handler for AJAX requests
    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import request, jsonify, redirect, url_for
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return JSON response for AJAX requests
            return jsonify({
                'success': False,
                'error': 'Session expired. Please refresh the page and log in again.'
            }), 401
        # For regular requests, redirect to login page
        return redirect(url_for('auth.login'))

    @login_manager.user_loader
    def load_user(user_id):
        # Load user from database
        from database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (int(user_id),))
        row = cursor.fetchone()
        conn.close()
        return user_from_row(row) if row else None
    # --- End Flask-Login setup ---
    
    # Register blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(vpn_bp)
    app.register_blueprint(persona_bp)
    app.register_blueprint(browsing_bp)
    app.register_blueprint(archives_bp)
    app.register_blueprint(journey_bp)
    
    # Import agent_bp here to prevent circular imports
    from routes.agent import agent_bp
    app.register_blueprint(agent_bp)
    
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    return app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the Flask application')
    parser.add_argument('--port', type=int, default=5002, help='Port to run the application on')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host address to run the application on')
    args = parser.parse_args()
    
    # Initialize default user if needed
    try:
        from init_default_user import init_default_user
        init_default_user()
    except Exception as e:
        logging.error(f"Failed to initialize default user: {e}")
    
    app = create_app()
    app.run(debug=True, use_reloader=True, port=args.port, host=args.host)
