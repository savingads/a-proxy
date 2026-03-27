import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from database.repositories.journey import JourneyRepository
from database.repositories.persona import PersonaRepository
from utils.llm_client import LLMClient

_EXTRACTED_FILE = Path(os.environ.get("DATA_DIR", "data")) / "chat_extracted.json"

logger = logging.getLogger(__name__)

PERSONA_CATEGORIES = ("demographic", "psychographic", "behavioral", "contextual")

# Reserve tokens for the system prompt and expected JSON output
_MAX_TRANSCRIPT_CHARS = 12000


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
        "behavioral": {
            "type": "object",
            "properties": {
                "browsing_habits": {"type": "array", "items": {"type": "string"}},
                "purchase_history": {"type": "array", "items": {"type": "string"}},
                "brand_interactions": {"type": "array", "items": {"type": "string"}},
                "device_usage": {"type": "object", "additionalProperties": {"type": "string"}},
                "social_media_activity": {"type": "object", "additionalProperties": {"type": "string"}},
                "content_consumption": {"type": "object", "additionalProperties": {"type": "string"}},
            },
            "additionalProperties": False,
        },
        "contextual": {
            "type": "object",
            "properties": {
                "time_of_day": {"type": ["string", "null"]},
                "day_of_week": {"type": ["string", "null"]},
                "season": {"type": ["string", "null"]},
                "weather": {"type": ["string", "null"]},
                "device_type": {"type": ["string", "null"]},
                "browser_type": {"type": ["string", "null"]},
                "screen_size": {"type": ["string", "null"]},
                "connection_type": {"type": ["string", "null"]},
            },
            "additionalProperties": False,
        },
    },
    "required": ["demographic", "psychographic", "behavioral", "contextual"],
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
    def _collect_extracted_items(extraction: Dict[str, Any]) -> Dict[str, Dict[str, list]]:
        """Collect all non-empty list and dict-key values from an LLM extraction."""
        result: Dict[str, Dict[str, list]] = {}
        for category in PERSONA_CATEGORIES:
            cat_data = extraction.get(category, {})
            if not cat_data:
                continue
            cat_items: Dict[str, list] = {}
            for key, value in cat_data.items():
                if isinstance(value, list) and value:
                    cat_items[key] = value
                elif isinstance(value, dict) and value:
                    cat_items[key] = list(value.keys())
            if cat_items:
                result[category] = cat_items
        return result

    @staticmethod
    def _save_extracted_metadata(persona_id: str, new_items: Dict[str, Dict[str, list]]) -> None:
        """Persist which attribute values were extracted from chat."""
        all_data: Dict[str, Any] = {}
        if _EXTRACTED_FILE.exists():
            try:
                all_data = json.loads(_EXTRACTED_FILE.read_text())
            except (json.JSONDecodeError, OSError):
                pass

        existing = all_data.get(persona_id, {})
        for cat, fields in new_items.items():
            if cat not in existing:
                existing[cat] = {}
            for field, items in fields.items():
                prev = existing[cat].get(field, [])
                existing[cat][field] = list(dict.fromkeys(prev + items))
        all_data[persona_id] = existing
        _EXTRACTED_FILE.parent.mkdir(parents=True, exist_ok=True)
        _EXTRACTED_FILE.write_text(json.dumps(all_data, indent=2))

    @staticmethod
    def get_extracted_metadata(persona_id: int) -> Dict[str, Dict[str, list]]:
        """Load chat-extracted attribute metadata for a persona."""
        if not _EXTRACTED_FILE.exists():
            return {}
        try:
            all_data = json.loads(_EXTRACTED_FILE.read_text())
            return all_data.get(str(persona_id), {})
        except (json.JSONDecodeError, OSError):
            return {}

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
        if len(transcript) > _MAX_TRANSCRIPT_CHARS:
            transcript = transcript[-_MAX_TRANSCRIPT_CHARS:]
        persona_label = persona_name or "the persona"
        return (
            "You are an analyst who extracts persona attributes from a dialogue. "
            "Extract details across four categories:\n"
            "1. Demographic: age, gender, location, language, education, income, occupation.\n"
            "2. Psychographic: interests, values, attitudes, opinions, lifestyle, personality.\n"
            "3. Behavioral: browsing habits, purchase history, brand interactions, "
            "device usage, social media activity, content consumption patterns.\n"
            "4. Contextual: preferred time of day, day of week, season, weather conditions, "
            "device type, browser type, screen size, connection type.\n\n"
            "Only include details that are explicitly stated or strongly implied. "
            "If a field is unknown, leave it null (for strings/objects) or an empty list (for arrays).\n\n"
            f"Conversation with {persona_label}:\n{transcript}"
        )

    def _prepare_updates(self, persona: Dict[str, Any], extraction: Dict[str, Any]) -> Dict[str, Any]:
        if not extraction:
            return {}

        updates: Dict[str, Any] = {"id": persona.get("id"), "name": persona.get("name")}
        all_new_items: Dict[str, Dict[str, list]] = {}

        for category in PERSONA_CATEGORIES:
            merged, new_items = self._merge_category(
                persona.get(category, {}), extraction.get(category, {})
            )
            if merged:
                updates[category] = merged
            if new_items:
                all_new_items[category] = new_items

        # Store provenance: record all values the LLM found in the conversation
        extracted_items = self._collect_extracted_items(extraction)
        if extracted_items:
            self._save_extracted_metadata(str(persona.get("id")), extracted_items)

        return updates

    @staticmethod
    def _merge_category(
        existing: Dict[str, Any], incoming: Dict[str, Any]
    ) -> tuple:
        merged: Dict[str, Any] = {}
        new_items: Dict[str, list] = {}

        for key, value in incoming.items():
            if value is None:
                continue
            if isinstance(value, list):
                existing_list = existing.get(key) or []
                existing_lower = {v.lower() for v in existing_list if isinstance(v, str)}
                new_values = [v for v in value if (v.lower() if isinstance(v, str) else v) not in existing_lower]
                # Only add truly new values (case-insensitive dedup)
                merged_values = list(existing_list)
                for v in new_values:
                    merged_values.append(v)
                if merged_values:
                    merged[key] = merged_values
                if new_values:
                    new_items[key] = new_values
            elif isinstance(value, dict):
                existing_dict = existing.get(key) or {}
                if isinstance(existing_dict, dict):
                    new_keys = [k for k in value if k not in existing_dict]
                    combined = {**existing_dict, **value}
                else:
                    new_keys = list(value.keys())
                    combined = value
                if combined:
                    merged[key] = combined
                if new_keys:
                    new_items[key] = new_keys
            else:
                merged[key] = value

        for key, value in existing.items():
            if key not in merged and value is not None:
                merged[key] = value

        return merged, new_items
