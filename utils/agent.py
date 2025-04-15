import logging
import json
from flask import current_app
import sys
import os

# Add agent_module to the path
sys.path.append(os.path.join(os.getcwd(), 'agent_module'))

from agent_module import create_proethica_agent_blueprint
from agent_module.adapters.a_proxy_claude import AProxyClaudeAdapter

class AgentService:
    """Service to handle interactions with the agent module."""
    
    def __init__(self, config=None):
        """Initialize the agent service with configuration."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self._claude_adapter = None
        self.logger.info("AgentService initialized")
        
    @property
    def claude_adapter(self):
        """Get or initialize the Claude adapter."""
        if self._claude_adapter is None:
            try:
                # Initialize Claude adapter directly
                self.logger.info("Initializing Claude adapter")
                self._claude_adapter = AProxyClaudeAdapter(
                    adapter_type='claude'
                )
                self.logger.info(f"Claude adapter initialized with model: {self._claude_adapter.model}")
            except Exception as e:
                self.logger.error(f"Error initializing Claude adapter: {e}")
                raise
        return self._claude_adapter
    
    def send_message(self, message, context=None):
        """
        Send a message to Claude and get a response.
        
        Args:
            message: The message to send
            context: Optional context information (journey, persona, etc.)
                Can also include model selection and system prompt
            
        Returns:
            Response from Claude
        """
        try:
            self.logger.info(f"Sending message to Claude: {message[:50]}...")
            
            # Format context if provided
            formatted_context = {}
            if context:
                # Include model selection if provided
                if 'model' in context:
                    formatted_context['model'] = context['model']
                    self.logger.info(f"Using specified model: {context['model']}")
                
                # Include system prompt if provided  
                if 'system_prompt' in context:
                    formatted_context['system_prompt'] = context['system_prompt']
                    self.logger.info(f"Using custom system prompt: {context['system_prompt'][:50]}...")
                
                # Include journey information if available
                if 'journey' in context:
                    formatted_context['journey'] = {
                        'id': context['journey'].get('id'),
                        'name': context['journey'].get('name'),
                        'description': context['journey'].get('description'),
                        'type': context['journey'].get('journey_type')
                    }
                
                # Include persona information if available
                if 'persona' in context:
                    formatted_context['persona'] = context['persona']
                
                # Include waypoints if available
                if 'waypoints' in context:
                    formatted_context['waypoints'] = context['waypoints']
            
            # Get response from Claude
            response = self.claude_adapter.send_message(message, formatted_context)
            
            # Log and return the response
            self.logger.info(f"Received response from Claude: {response.get('content', '')[:50]}...")
            return response
        except Exception as e:
            self.logger.error(f"Error sending message to Claude: {e}")
            return {
                "role": "assistant",
                "content": f"I'm sorry, but I encountered an error: {str(e)}"
            }
    
    def create_agent_blueprint(self, url_prefix='/agent'):
        """Create a Flask blueprint for the agent routes."""
        try:
            # Create the agent blueprint with Claude configuration
            agent_bp = create_proethica_agent_blueprint(
                config={
                    'require_auth': self.config.get('require_auth', False),
                    'api_key': self.config.get('api_key', ''),
                    'use_claude': self.config.get('use_claude', True),
                    'adapter_type': 'a_proxy_claude',
                    'anthropic_api_key': self.config.get('anthropic_api_key', ''),
                    'claude_model': self.config.get('claude_model', 'claude-3-sonnet-20240229')
                },
                url_prefix=url_prefix
            )
            return agent_bp
        except Exception as e:
            self.logger.error(f"Error creating agent blueprint: {e}")
            raise

    def save_conversation(self, journey_id, conversation_data):
        """Save agent conversation data to the waypoint."""
        from database import add_waypoint
        
        try:
            # Format conversation for storage
            url = "agent://conversation"
            title = f"Agent Conversation #{conversation_data.get('id', 'unknown')}"
            notes = conversation_data.get('summary', 'Agent conversation')
            
            # Add the waypoint with type 'agent'
            waypoint_id = add_waypoint(
                journey_id=journey_id,
                url=url,
                title=title,
                notes=notes,
                type='agent',
                agent_data=json.dumps(conversation_data)
            )
            
            return waypoint_id
        except Exception as e:
            self.logger.error(f"Error saving agent conversation: {e}")
            raise

    def get_conversation(self, waypoint_id):
        """Get agent conversation data from a waypoint."""
        from database import get_waypoint
        
        try:
            waypoint = get_waypoint(waypoint_id)
            
            if not waypoint or waypoint.get('type') != 'agent':
                return None
            
            # Parse the agent data
            agent_data = json.loads(waypoint.get('agent_data', '{}'))
            return agent_data
        except Exception as e:
            self.logger.error(f"Error retrieving agent conversation: {e}")
            return None

# Helper to get the agent service instance
def get_agent_service():
    """Get the current agent service instance."""
    if not hasattr(current_app, 'agent_service'):
        # Get configuration from app config
        config = {
            'require_auth': current_app.config.get('AGENT_REQUIRE_AUTH', False),
            'api_key': current_app.config.get('AGENT_API_KEY', ''),
            'use_claude': current_app.config.get('AGENT_USE_CLAUDE', True),
            'anthropic_api_key': current_app.config.get('ANTHROPIC_API_KEY', ''),
            'claude_model': current_app.config.get('CLAUDE_MODEL', 'claude-3-sonnet-20240229'),
            'adapter_type': 'a_proxy_claude'
        }
        logging.info(f"Initializing AgentService with Claude API settings")
        current_app.agent_service = AgentService(config)
    
    return current_app.agent_service
