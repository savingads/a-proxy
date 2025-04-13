import logging
import json
from flask import current_app
import sys
import os

# Add agent_module to the path
sys.path.append(os.path.join(os.getcwd(), 'agent_module'))

from agent_module import create_proethica_agent_blueprint

class AgentService:
    """Service to handle interactions with the agent module."""
    
    def __init__(self, config=None):
        """Initialize the agent service with configuration."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.logger.info("AgentService initialized")
    
    def create_agent_blueprint(self, url_prefix='/agent'):
        """Create a Flask blueprint for the agent routes."""
        try:
            # Create the agent blueprint
            agent_bp = create_proethica_agent_blueprint(
                config={
                    'require_auth': self.config.get('require_auth', False),
                    'api_key': self.config.get('api_key', ''),
                    'use_claude': self.config.get('use_claude', True)
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
            'use_claude': current_app.config.get('AGENT_USE_CLAUDE', True)
        }
        current_app.agent_service = AgentService(config)
    
    return current_app.agent_service
