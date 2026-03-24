"""
Test script for the Claude adapter integration.
"""

import os
import sys
import logging
import json
from flask import Flask

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add current directory to path to ensure imports work
sys.path.insert(0, os.getcwd())

# Import the adapter
logger.info("Importing required modules...")

try:
    from agent_module.adapters.a_proxy_claude import AProxyClaudeAdapter
    from agent_module.services.config_service import ConfigService
    logger.info("Successfully imported modules from agent_module")
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Check module path and ensure all dependencies are installed")
    sys.exit(1)

def test_direct_adapter():
    """Test the Claude adapter directly."""
    logger.info("Testing Claude adapter directly...")
    
    # Create a simple config service with the API key
    class TestConfigService(ConfigService):
        def get_value(self, key, default=None):
            config = {
                'ANTHROPIC_API_KEY': os.environ.get('ANTHROPIC_API_KEY', ''),  # API key must be in environment
                'CLAUDE_MODEL': 'claude-3-sonnet-20240229',
                'CLAUDE_MAX_TOKENS': 1024
            }
            return config.get(key, default)
    
    # Create the adapter
    adapter = AProxyClaudeAdapter(config_service=TestConfigService())
    
    # Test a simple message
    message = "Hello, can you tell me about yourself?"
    
    logger.info(f"Sending message to Claude: {message}")
    response = adapter.send_message(message)
    
    logger.info(f"Response from Claude: {response.get('content', '')[:100]}...")
    
    # Test with persona context
    persona_context = {
        'persona': {
            'name': 'Research Assistant',
            'description': 'A helpful AI research assistant that specializes in academic research.',
            'traits': ['knowledgeable', 'scholarly', 'detail-oriented']
        }
    }
    
    message_with_context = "Can you help me research climate change?"
    
    logger.info(f"Sending message with persona context: {message_with_context}")
    response_with_context = adapter.send_message(message_with_context, persona_context)
    
    logger.info(f"Response with context: {response_with_context.get('content', '')[:100]}...")
    
    return response, response_with_context

def test_with_flask_app():
    """Test the adapter within a Flask app context."""
    logger.info("Testing Claude adapter with Flask app...")
    
    # Create a simple Flask app
    app = Flask(__name__)
    
    # Load config from our config.py
    app.config.from_pyfile('config.py')
    
    # Create the context
    with app.app_context():
        # Import the agent service within app context
        from utils.agent import get_agent_service
        
        # Get the agent service
        agent_service = get_agent_service()
        
        logger.info("Agent service initialized")
        
        # Create the blueprint
        blueprint = agent_service.create_agent_blueprint()
        
        logger.info("Agent blueprint created")
        
    return True

if __name__ == "__main__":
    logger.info("Starting Claude adapter test")
    
    # Set environment variable for API key from config if not set
    if not os.environ.get('ANTHROPIC_API_KEY'):
        try:
            # Try to load from config.py
            sys.path.insert(0, os.getcwd())
            import config as app_config
            os.environ['ANTHROPIC_API_KEY'] = app_config.ANTHROPIC_API_KEY
            logger.info("Loaded API key from config.py")
        except (ImportError, AttributeError):
            logger.warning("Could not load API key from config.py")
    
    # Test direct adapter interaction
    try:
        direct_response, context_response = test_direct_adapter()
        logger.info("Direct adapter test successful")
        logger.info(f"Sample response: {direct_response.get('content', '')[:100]}...")
    except Exception as e:
        logger.error(f"Direct adapter test failed: {e}", exc_info=True)
    
    # Test with Flask app
    try:
        app_test_result = test_with_flask_app()
        logger.info("Flask app test successful")
    except Exception as e:
        logger.error(f"Flask app test failed: {e}", exc_info=True)
    
    logger.info("All tests completed")
