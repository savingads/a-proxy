import json
import logging
from typing import Any, Dict, List, Optional

from database.repositories.journey import JourneyRepository
from database.repositories.persona import PersonaRepository
from utils.llm_client import LLMClient

logger = logging.getLogger(__name__)


EXTRACTION_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "demographic": {
            "type": "object",
            "properties": {
                "country": {"type": ["string", "null"]},
                "region": {"type": ["string", "null"]},
                "city": {"type": ["string", "null"]},
                "language": {"type": ["string", "null"]},
                "age": {"type": ["integer", "null"]},
                "gender": {"type": ["string", "null"]},
                "education": {"type": ["string", "null"]},
                "income": {"type": ["string", "null"]},
                "occupation": {"type": ["string", "null"]},
            },
            "additionalProperties": False,
        },
        "psychographic": {
            "type": "object",
            "properties": {
                "interests": {"type": "array", "items": {"type": "string"}},
                "personal_values": {"type": "array", "items": {"type": "string"}},
                "attitudes": {"type": "array", "items": {"type": "string"}},
                "opinions": {"type": "array", "items": {"type": "string"}},
                "lifestyle": {"type": ["string", "null"]},
                "personality": {"type": ["string", "null"]},
            },
            "additionalProperties": False,
        },
    },
    "required": ["demographic", "psychographic"],
    "additionalProperties": False,
}


class PersonaAttributeService:
    """Extract and apply persona attributes from saved conversations."""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        persona_repo: Optional[PersonaRepository] = None,
        journey_repo: Optional[JourneyRepository] = None,
    ):
        self.llm_client = llm_client or LLMClient()
        self.persona_repo = persona_repo or PersonaRepository()
        self.journey_repo = journey_repo or JourneyRepository()

    def process_waypoint(self, waypoint_id: int) -> Optional[int]:
        """
        Analyze a saved agent conversation waypoint and update the linked persona.

        Returns the persona ID if updates were applied, otherwise None.
        """
        waypoint = self.journey_repo.get_waypoint(waypoint_id)
        if not waypoint:
            raise ValueError(f"Waypoint {waypoint_id} was not found")

        journey = self.journey_repo.get(waypoint["journey_id"])
        if not journey or not journey.get("persona_id"):
            logger.info("Skipping persona update; journey has no linked persona")
            return None

        persona = self.persona_repo.get(journey["persona_id"])
        if not persona:
            logger.warning("Persona %s not found for journey %s", journey.get("persona_id"), journey.get("id"))
            return None

        agent_data = self._parse_agent_data(waypoint.get("agent_data"))
        conversation = self._flatten_conversation(agent_data)
        if not conversation:
            logger.info("No conversation content available on waypoint %s", waypoint_id)
            return None

        prompt = self._build_prompt(conversation, persona.get("name"))
        extraction = self.llm_client.generate_structured(prompt, EXTRACTION_SCHEMA)
        updates = self._prepare_updates(persona, extraction)

        if not updates:
            logger.info("LLM returned no usable persona updates for waypoint %s", waypoint_id)
            return None

        self.persona_repo.save(updates)
        logger.info("Persona %s updated from waypoint %s", journey.get("persona_id"), waypoint_id)
        return journey.get("persona_id")

    @staticmethod
    def _parse_agent_data(agent_data_raw: Optional[str]) -> Dict[str, Any]:
        if not agent_data_raw:
            return {}
        try:
            return json.loads(agent_data_raw)
        except json.JSONDecodeError:
            logger.warning("Failed to decode agent_data; ignoring content")
            return {}

    @staticmethod
    def _flatten_conversation(agent_data: Dict[str, Any]) -> List[Dict[str, str]]:
        if not agent_data:
            return []

        if agent_data.get("history"):
            return [m for m in agent_data.get("history", []) if m.get("content")]

        combined: List[Dict[str, str]] = []
        for key in ("with_history", "as_history"):
            combined.extend([m for m in agent_data.get(key, []) if m.get("content")])
        return combined

    @staticmethod
    def _build_prompt(conversation: List[Dict[str, str]], persona_name: Optional[str]) -> str:
        transcript = "\n".join(
            [f"{msg.get('role', 'user')}: {msg.get('content', '').strip()}" for msg in conversation]
        )
        persona_label = persona_name or "the persona"
        return (
            "You are an analyst who extracts persona attributes from a dialogue. "
            "Identify demographic and psychographic details that are explicitly stated or strongly implied. "
            "If a field is unknown, leave it null (for strings) or an empty list (for arrays).\n\n"
            f"Conversation with {persona_label}:\n{transcript}"
        )

    def _prepare_updates(self, persona: Dict[str, Any], extraction: Dict[str, Any]) -> Dict[str, Any]:
        if not extraction:
            return {}

        demographic_updates = self._merge_category(
            persona.get("demographic", {}), extraction.get("demographic", {})
        )
        psychographic_updates = self._merge_category(
            persona.get("psychographic", {}), extraction.get("psychographic", {})
        )

        updates: Dict[str, Any] = {"id": persona.get("id"), "name": persona.get("name")}
        if demographic_updates:
            updates["demographic"] = demographic_updates
        if psychographic_updates:
            updates["psychographic"] = psychographic_updates

        return updates

    @staticmethod
    def _merge_category(existing: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
        merged: Dict[str, Any] = {}

        for key, value in incoming.items():
            if value is None:
                continue
            if isinstance(value, list):
                merged_values = list(dict.fromkeys((existing.get(key) or []) + value))
                if merged_values:
                    merged[key] = merged_values
            else:
                merged[key] = value

        for key, value in existing.items():
            if key not in merged and value is not None:
                merged[key] = value

        return merged
