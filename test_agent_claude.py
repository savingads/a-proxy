"""
Test script to verify the agent_message endpoint with Claude integration.
"""

import os
import sys
import requests
import json
import logging
import argparse

logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_agent_endpoint(journey_id, message, base_url="http://localhost:5002"):
    """Test the agent/message endpoint with Claude."""
    try:
        endpoint = f"{base_url}/journey/{journey_id}/agent/message"
        logger.info(f"Testing endpoint: {endpoint}")
        
        # Prepare the request
        payload = {
            "message": message,
            "conversation_id": "test_" + str(journey_id)
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        # Send the request
        logger.info(f"Sending message: {message}")
        response = requests.post(
            endpoint,
            json=payload,
            headers=headers
        )
        
        # Log the status code
        logger.info(f"Response status code: {response.status_code}")
        
        # Parse and validate the response
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                logger.info("Test successful!")
                logger.info(f"Claude response: {data.get('response')}")
                return True
            else:
                logger.error(f"API error: {data.get('error')}")
                return False
        else:
            logger.error(f"HTTP error: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"Error testing agent endpoint: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test the agent_message endpoint with Claude')
    parser.add_argument('--journey-id', type=int, default=1, help='Journey ID to use for testing')
    parser.add_argument('--message', type=str, default='Hello, Claude! How are you today?', help='Message to send')
    parser.add_argument('--base-url', type=str, default='http://localhost:5002', help='Base URL for the API')
    
    args = parser.parse_args()
    
    logger.info("Starting test for agent_message endpoint with Claude")
    success = test_agent_endpoint(args.journey_id, args.message, args.base_url)
    
    if success:
        logger.info("✅ Test completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Test failed!")
        sys.exit(1)
