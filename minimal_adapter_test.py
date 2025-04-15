"""
Minimal test for the AProxyClaudeAdapter without full agent_module dependencies.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MinimalConfigService:
    """Minimal implementation of ConfigService for testing."""
    
    def __init__(self, config_dict=None):
        """Initialize with an optional config dictionary."""
        # Get API key from environment or use the one provided
        self.config = config_dict or {}
        if not self.config.get('ANTHROPIC_API_KEY'):
            # Try to load from config.py
            try:
                sys.path.insert(0, os.getcwd())
                import config as app_config
                self.config['ANTHROPIC_API_KEY'] = app_config.ANTHROPIC_API_KEY
                self.config['CLAUDE_MODEL'] = app_config.CLAUDE_MODEL
                self.config['CLAUDE_MAX_TOKENS'] = app_config.CLAUDE_MAX_TOKENS
                logger.info("Loaded config from config.py")
            except (ImportError, AttributeError) as e:
                logger.warning(f"Could not load from config.py: {e}")
    
    def get_value(self, key: str, default=None) -> Any:
        """Get a configuration value by key."""
        return self.config.get(key, default)

class MinimalAdapter:
    """Minimalist version of AProxyClaudeAdapter for testing."""
    
    def __init__(self):
        """Initialize adapter with minimal dependencies."""
        from anthropic import Anthropic
        
        # Create config service
        self.config_service = MinimalConfigService()
        
        # Get API key from config or environment
        self.api_key = self.config_service.get_value('ANTHROPIC_API_KEY') or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            logger.error("No Claude API key found in config or environment variables")
            raise ValueError("Anthropic API key is required")
            
        # Get primary model from config
        self.model = self.config_service.get_value('CLAUDE_MODEL', 'claude-3-opus-20240229')
        
        # Fallback models to try if the primary model isn't available
        self.fallback_models = [
            'claude-3-opus-20240229',
            'claude-3-sonnet-20240229',
            'claude-3-haiku-20240307',
            'claude-2.1',
            'claude-2.0',
            'claude-instant-1.2'
        ]
        
        self.max_tokens = int(self.config_service.get_value('CLAUDE_MAX_TOKENS', 4096))
        
        # Initialize Anthropic client
        try:
            self.client = Anthropic(api_key=self.api_key)
            logger.info(f"Anthropic client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Anthropic client: {str(e)}")
            raise
            
        # Store conversation history
        self.conversation_history = []
        logger.info(f"Adapter initialized with primary model {self.model}")
    
    def send_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a message to Claude and get a response."""
        context = context or {}
        
        # Process context information
        system_prompt = self._build_system_prompt(context)
        
        # Add current user message
        user_message = {"role": "user", "content": message}
        
        # Format Claude messages
        formatted_messages = self.conversation_history + [user_message]
        
        logger.debug(f"Sending request to Claude API with system prompt: {system_prompt[:100]}...")
        
        # Try the primary model first, then fallbacks if needed
        models_to_try = [self.model] + [m for m in self.fallback_models if m != self.model]
        
        last_error = None
        for current_model in models_to_try:
            try:
                # Make request to Claude API using official client
                logger.info(f"Trying model: {current_model}")
                response = self.client.messages.create(
                    model=current_model,
                    system=system_prompt,
                    messages=formatted_messages,
                    max_tokens=self.max_tokens
                )
                
                # Success! Parse the response
                content = response.content[0].text
                
                # Update conversation history
                self.conversation_history.append(user_message)
                self.conversation_history.append({"role": "assistant", "content": content})
                
                # If this isn't our primary model, update it for future use
                if current_model != self.model:
                    logger.info(f"Switching primary model from {self.model} to {current_model}")
                    self.model = current_model
                
                logger.info(f"Received response from Claude API: {content[:100]}...")
                return {
                    "role": "assistant",
                    "content": content
                }
                
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Error with model {current_model}: {error_msg}")
                last_error = error_msg
                
                # Check if this is a model-not-found error
                if "model" in error_msg.lower() and "not found" in error_msg.lower():
                    # Try the next model
                    continue
                elif "status code: 404" in error_msg.lower():
                    # Likely a model-not-found error, try next model
                    continue
                else:
                    # For other errors, we might want to stop trying
                    # But for now, we'll continue with fallbacks
                    pass
        
        # If we get here, all models failed
        logger.error(f"All Claude models failed. Last error: {last_error}")
        return {
            "role": "assistant",
            "content": f"I apologize, but I encountered an error processing your request."
        }
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build a system prompt from the context."""
        system_prompt_parts = []
        
        # Extract persona context if available
        if 'persona' in context:
            persona = context.get('persona', {})
            if persona:
                persona_prompt = f"""
# Persona Context
Name: {persona.get('name', 'Unknown')}
Description: {persona.get('description', '')}
"""
                if 'traits' in persona and persona['traits']:
                    if isinstance(persona['traits'], list):
                        persona_prompt += f"Traits: {', '.join(persona['traits'])}\n"
                    elif isinstance(persona['traits'], str):
                        persona_prompt += f"Traits: {persona['traits']}\n"
                
                system_prompt_parts.append(persona_prompt)
        
        # Add general instructions
        system_prompt_parts.append(
            "You are a helpful assistant providing information and assistance. "
            "Respond in a natural conversational manner, being concise but thorough."
        )
        
        return "\n\n".join(system_prompt_parts)
    
    def reset_conversation(self) -> None:
        """Reset the current conversation state."""
        logger.debug("Resetting conversation history")
        self.conversation_history = []

def test_minimal_adapter():
    """Test the minimal adapter."""
    try:
        # Initialize the adapter
        adapter = MinimalAdapter()
        
        # Test a simple message
        message1 = "Hello, what's your name?"
        logger.info(f"Sending message: {message1}")
        
        response1 = adapter.send_message(message1)
        logger.info(f"Response: {response1['content']}")
        
        # Test a message with persona context
        persona_context = {
            'persona': {
                'name': 'Research Assistant',
                'description': 'A helpful AI research assistant that specializes in academic research.',
                'traits': ['knowledgeable', 'scholarly', 'detail-oriented']
            }
        }
        
        message2 = "Can you help me with my research project?"
        logger.info(f"Sending message with persona context: {message2}")
        
        response2 = adapter.send_message(message2, persona_context)
        logger.info(f"Response with context: {response2['content']}")
        
        return True
    except Exception as e:
        logger.error(f"Error during minimal adapter test: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("Starting minimal adapter test")
    
    success = test_minimal_adapter()
    
    if success:
        logger.info("✅ Test completed successfully!")
    else:
        logger.error("❌ Test failed!")
