"""
Agent service module for Claude AI integration.

This module provides a high-level interface for interacting with Claude
via the Anthropic API, including conversation management and context handling.
"""
import logging
import json
from flask import current_app

logger = logging.getLogger(__name__)


class AgentService:
    """Service to handle interactions with Claude via Anthropic API."""

    def __init__(self, config=None):
        """Initialize the agent service with configuration."""
        self.config = config or {}
        self._client = None
        logger.info("AgentService initialized")

    @property
    def client(self):
        """Get or initialize the Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                from config import ANTHROPIC_API_KEY

                if not ANTHROPIC_API_KEY:
                    logger.error("ANTHROPIC_API_KEY is not set in the environment or config")
                    raise ValueError("ANTHROPIC_API_KEY is required to initialize Claude client")

                logger.info("Initializing Anthropic client")
                self._client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
                logger.info("Anthropic client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Anthropic client: {e}", exc_info=True)
                raise
        return self._client

    def send_message(self, message, context=None):
        """
        Send a message to Claude and get a response.

        Args:
            message: The message to send
            context: Optional context information (journey, persona, etc.)
                Can also include model selection and system prompt

        Returns:
            Response dict with 'role' and 'content' keys
        """
        try:
            logger.info(f"Sending message to Claude: {message[:50]}...")

            # Get model from context or use default
            model = self.config.get('claude_model', 'claude-3-opus-20240229')
            if context and 'model' in context:
                model = context['model']
                logger.info(f"Using specified model: {model}")

            # Build system prompt
            system_prompt = self._build_system_prompt(context)

            # Build messages array
            messages = []

            # Add conversation history if provided
            if context and 'history' in context:
                for msg in context['history'][-10:]:  # Limit history
                    role = msg.get('role', '')
                    content = msg.get('content', '')

                    # Map roles to Claude's expected format
                    claude_role = 'user'
                    if role in ['agent', 'assistant', 'target']:
                        claude_role = 'assistant'
                    elif role in ['user', 'persona']:
                        claude_role = 'user'

                    if content and role:
                        messages.append({"role": claude_role, "content": content})

            # Add current message
            messages.append({"role": "user", "content": message})

            # Send to Claude
            logger.info(f"Calling Claude API with model: {model} and {len(messages)} messages")
            response = self.client.messages.create(
                model=model,
                system=system_prompt,
                messages=messages,
                max_tokens=4096
            )

            # Extract content from response
            response_content = response.content[0].text
            logger.info(f"Received response from Claude: {response_content[:50]}...")

            return {
                "role": "assistant",
                "content": response_content
            }

        except Exception as e:
            logger.error(f"Error sending message to Claude: {e}", exc_info=True)
            return {
                "role": "assistant",
                "content": f"I'm sorry, but I encountered an error: {str(e)}"
            }

    def _build_system_prompt(self, context):
        """Build the system prompt from context."""
        if not context:
            return "You are a helpful assistant."

        # Use custom system prompt if provided
        if 'system_prompt' in context:
            return context['system_prompt']

        # Build from persona and journey context
        parts = []

        # Add persona context
        if 'persona' in context and context['persona']:
            persona = context['persona']
            parts.append(f"You are {persona.get('name', 'a persona')}.")

            # Add demographic info
            if 'demographic' in persona:
                demo = persona['demographic']
                if demo.get('occupation'):
                    parts.append(f"Occupation: {demo['occupation']}")
                if demo.get('age'):
                    parts.append(f"Age: {demo['age']}")

        # Add journey context
        if 'journey' in context and context['journey']:
            journey = context['journey']
            parts.append(f"\nJourney: {journey.get('name', 'Unnamed')}")
            if journey.get('description'):
                parts.append(f"Description: {journey['description']}")

        if parts:
            return "\n".join(parts)

        return "You are a helpful assistant."

    def save_conversation(self, journey_id, conversation_data):
        """Save agent conversation data to the waypoint."""
        from database import add_waypoint

        try:
            url = "agent://conversation"
            title = f"Agent Conversation #{conversation_data.get('id', 'unknown')}"
            notes = conversation_data.get('summary', 'Agent conversation')

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
            logger.error(f"Error saving agent conversation: {e}")
            raise

    def get_conversation(self, waypoint_id):
        """Get agent conversation data from a waypoint."""
        from database import get_waypoint

        try:
            waypoint = get_waypoint(waypoint_id)

            if not waypoint or waypoint.get('type') != 'agent':
                return None

            agent_data = json.loads(waypoint.get('agent_data', '{}'))
            return agent_data
        except Exception as e:
            logger.error(f"Error retrieving agent conversation: {e}")
            return None


def get_agent_service():
    """Get the current agent service instance."""
    if not hasattr(current_app, 'agent_service'):
        config = {
            'require_auth': current_app.config.get('AGENT_REQUIRE_AUTH', False),
            'api_key': current_app.config.get('AGENT_API_KEY', ''),
            'anthropic_api_key': current_app.config.get('ANTHROPIC_API_KEY', ''),
            'claude_model': current_app.config.get('CLAUDE_MODEL', 'claude-3-opus-20240229'),
        }

        # Log configuration (without API key)
        safe_config = config.copy()
        if 'anthropic_api_key' in safe_config:
            safe_config['anthropic_api_key'] = 'REDACTED' if safe_config['anthropic_api_key'] else 'NOT SET'
        if 'api_key' in safe_config:
            safe_config['api_key'] = 'REDACTED' if safe_config['api_key'] else 'NOT SET'

        logger.info(f"Initializing AgentService with config: {safe_config}")
        current_app.agent_service = AgentService(config)

    return current_app.agent_service
