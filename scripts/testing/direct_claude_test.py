"""
Direct test for Claude API integration without module dependencies.
"""

import os
import sys
import requests
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_claude_api():
    """Test the Claude API directly."""
    logger.info("Testing Claude API directly...")
    
    # Get the API key from environment or config.py
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        # Try to load from config.py
        try:
            sys.path.insert(0, os.getcwd())
            import config as app_config
            api_key = app_config.ANTHROPIC_API_KEY
            logger.info("Loaded API key from config.py")
        except (ImportError, AttributeError):
            logger.error("Could not load API key from config.py")
            return False

    # Claude API configuration
    api_url = "https://api.anthropic.com/v1/messages"
    model = "claude-instant-1.2"  # Try a different model
    max_tokens = 1024
    
    # Prepare headers
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    # Test message
    message = "Hello, Claude! Can you tell me about yourself?"
    
    # Prepare request data
    data = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": message}]
    }
    
    # Make request to Claude API
    try:
        logger.info(f"Sending message to Claude API: {message}")
        response = requests.post(
            api_url,
            headers=headers,
            json=data,
            timeout=30
        )
        
        # Handle API response
        if response.status_code == 200:
            response_data = response.json()
            content = response_data.get('content', [{}])[0].get('text', '')
            
            logger.info(f"Response from Claude API: {content[:100]}...")
            logger.info("Claude API test passed!")
            return True
        else:
            error_msg = f"Claude API error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            return False
                
    except Exception as e:
        logger.error(f"Error calling Claude API: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("Starting direct Claude API test")
    
    success = test_claude_api()
    
    if success:
        logger.info("✅ Test completed successfully!")
    else:
        logger.error("❌ Test failed!")
