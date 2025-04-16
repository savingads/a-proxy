"""
Simple test script for Claude integration without agent_module dependencies.
"""

import os
import sys
import logging
from anthropic import Anthropic
import time

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load API key from config
def get_api_key():
    try:
        # Try to load from config.py
        sys.path.insert(0, os.getcwd())
        import config as app_config
        api_key = app_config.ANTHROPIC_API_KEY
        logger.info("Loaded API key from config.py")
        return api_key
    except (ImportError, AttributeError):
        logger.warning("Could not load API key from config.py")
        return os.environ.get('ANTHROPIC_API_KEY')

def test_claude_client():
    """Direct test of Claude API using the official client."""
    logger.info("Testing Claude API with the official client")
    
    # Get API key
    api_key = get_api_key()
    if not api_key:
        logger.error("No Claude API key found in config or environment variables")
        return False
    
    # List of models to try
    models = [
        'claude-3-sonnet-20240229',
        'claude-3-opus-20240229',
        'claude-3-haiku-20240307',
        'claude-2.1',
        'claude-2.0',
        'claude-instant-1.2'
    ]
    
    # Initialize Anthropic client
    client = Anthropic(api_key=api_key)
    
    # Try each model until one works
    for model in models:
        try:
            logger.info(f"Trying model: {model}")
            
            # Send a test message
            response = client.messages.create(
                model=model,
                system="You are a helpful assistant. Keep responses brief and concise.",
                messages=[
                    {"role": "user", "content": "Hello, what's your name?"}
                ],
                max_tokens=100
            )
            
            # Get and log the response
            content = response.content[0].text
            logger.info(f"Response from Claude ({model}): {content}")
            
            # Success!
            logger.info(f"✅ Successfully used model: {model}")
            
            # Try a message with context
            persona_context = """
            # Persona Context
            Name: Research Assistant
            Description: A helpful AI research assistant that specializes in academic research.
            Traits: knowledgeable, scholarly, detail-oriented
            """
            
            response_with_context = client.messages.create(
                model=model,
                system=persona_context,
                messages=[
                    {"role": "user", "content": "Can you help me research climate change?"}
                ],
                max_tokens=100
            )
            
            # Get and log the response
            context_content = response_with_context.content[0].text
            logger.info(f"Response with context: {context_content}")
            
            return True
        except Exception as e:
            logger.warning(f"Error with model {model}: {str(e)}")
    
    # If we get here, all models failed
    logger.error("❌ All Claude models failed")
    return False

if __name__ == "__main__":
    logger.info("Starting simple Claude API test")
    start_time = time.time()
    
    success = test_claude_client()
    
    end_time = time.time()
    duration = end_time - start_time
    
    if success:
        logger.info(f"✅ Test completed successfully in {duration:.2f} seconds!")
    else:
        logger.error(f"❌ Test failed after {duration:.2f} seconds")
