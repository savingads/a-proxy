"""
Test script for the Claude adapter integration using the official Anthropic library.
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

def test_claude_adapter_direct():
    """Test the Claude adapter directly."""
    logger.info("Testing Claude adapter with the official Anthropic library...")
    
    try:
        # Import the adapter
        from agent_module.adapters.a_proxy_claude import AProxyClaudeAdapter
        from agent_module.services.config_service import ConfigService
        
        # Create a custom config service with API key
        class TestConfigService(ConfigService):
            def get_value(self, key, default=None):
                config = {
                    'ANTHROPIC_API_KEY': os.environ.get('ANTHROPIC_API_KEY', 
                                                      None),
                    'CLAUDE_MODEL': 'claude-3-sonnet-20240229',
                    'CLAUDE_MAX_TOKENS': 1024
                }
                return config.get(key, default)
        
        # Create the adapter with our test config
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
        
        # Test generating suggestions
        logger.info("Testing suggestion generation...")
        suggestions = adapter.generate_options(persona_context)
        
        logger.info(f"Generated {len(suggestions)} suggestions:")
        for suggestion in suggestions:
            logger.info(f"  - {suggestion.get('text', '')}")
        
        return True, "All tests passed successfully!"
    except Exception as e:
        logger.error(f"Error during Claude adapter test: {e}", exc_info=True)
        return False, f"Test failed with error: {str(e)}"

def test_with_flask_app():
    """Test the adapter within a Flask app context."""
    logger.info("Testing Claude adapter with Flask app...")
    
    try:
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
            
        return True, "Flask integration test passed!"
    except Exception as e:
        logger.error(f"Flask app test failed: {e}", exc_info=True)
        return False, f"Flask integration test failed: {str(e)}"

if __name__ == "__main__":
    logger.info("Starting Claude adapter test with official Anthropic library")
    
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
    success, message = test_claude_adapter_direct()
    if success:
        logger.info(f"✅ Direct test: {message}")
    else:
        logger.error(f"❌ Direct test failed: {message}")
    
    # Test with Flask app
    app_success, app_message = test_with_flask_app()
    if app_success:
        logger.info(f"✅ Flask app test: {app_message}")
    else:
        logger.error(f"❌ Flask app test failed: {app_message}")
    
    logger.info("All tests completed")
