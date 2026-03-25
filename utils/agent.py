"""
Agent service module for LLM-powered conversations.

Provides a high-level interface for interacting with LLMs (local or cloud)
via the LLMClient, including conversation management and context handling.
"""
import logging
import json
from flask import current_app

logger = logging.getLogger(__name__)


class AgentService:
    """Service to handle interactions with LLMs via LLMClient."""

    def __init__(self, config=None):
        self.config = config or {}
        self._llm = None
        logger.info("AgentService initialized")

    @property
    def llm(self):
        if self._llm is None:
            from utils.llm_client import LLMClient
            self._llm = LLMClient()
            logger.info("LLMClient initialized for AgentService")
        return self._llm

    def send_message(self, message, context=None):
        try:
            logger.info(f"Sending message: {message[:50]}...")

            model = self.config.get('model')
            if context and 'model' in context:
                model = context['model']

            system_prompt = self._build_system_prompt(context)

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            if context and 'history' in context:
                for msg in context['history'][-10:]:
                    role = msg.get('role', '')
                    content = msg.get('content', '')

                    llm_role = 'user'
                    if role in ['agent', 'assistant', 'target']:
                        llm_role = 'assistant'
                    elif role in ['user', 'persona']:
                        llm_role = 'user'

                    if content and role:
                        messages.append({"role": llm_role, "content": content})

            messages.append({"role": "user", "content": message})

            logger.info(f"Calling LLM with {len(messages)} messages")
            response_content = self.llm.chat(messages, model_hint=model)
            logger.info(f"Received response: {response_content[:50]}...")

            return {
                "role": "assistant",
                "content": response_content
            }

        except Exception as e:
            logger.error(f"Error sending message: {e}", exc_info=True)
            return {
                "role": "assistant",
                "content": f"I'm sorry, but I encountered an error: {str(e)}"
            }

    def _build_system_prompt(self, context):
        if not context:
            return "You are a helpful assistant."

        if 'system_prompt' in context:
            return context['system_prompt']

        parts = []

        if 'persona' in context and context['persona']:
            persona = context['persona']
            parts.append(f"You are {persona.get('name', 'a persona')}.")

            if 'demographic' in persona:
                demo = persona['demographic']
                if demo.get('occupation'):
                    parts.append(f"Occupation: {demo['occupation']}")
                if demo.get('age'):
                    parts.append(f"Age: {demo['age']}")

        if 'journey' in context and context['journey']:
            journey = context['journey']
            parts.append(f"\nJourney: {journey.get('name', 'Unnamed')}")
            if journey.get('description'):
                parts.append(f"Description: {journey['description']}")

        if parts:
            return "\n".join(parts)

        return "You are a helpful assistant."

    def save_conversation(self, journey_id, conversation_data):
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
    if not hasattr(current_app, 'agent_service'):
        config = {
            'require_auth': current_app.config.get('AGENT_REQUIRE_AUTH', False),
        }
        logger.info(f"Initializing AgentService")
        current_app.agent_service = AgentService(config)

    return current_app.agent_service
