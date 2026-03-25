"""Service layer utilities for A-Proxy."""

from .persona_attribute_service import PersonaAttributeService  # noqa: E402,F401

# Re-export functions from the legacy services module (services.py was renamed)
# These are imported by routes/agent.py
import importlib
import sys
import os

# Load the legacy services.py as a separate module
_legacy_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'services.py')
if os.path.exists(_legacy_path):
    import importlib.util
    _spec = importlib.util.spec_from_file_location("_services_legacy", _legacy_path)
    _legacy = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_legacy)

    # Re-export the functions that routes/agent.py needs
    fetch_persona_context = _legacy.fetch_persona_context
    flatten_persona_context = _legacy.flatten_persona_context
    persona_context_to_system_prompt = _legacy.persona_context_to_system_prompt
    ContextManager = _legacy.ContextManager
    PersonaContextProvider = _legacy.PersonaContextProvider
    JourneyContextProvider = _legacy.JourneyContextProvider
    ContextProvider = _legacy.ContextProvider
    format_persona_system_prompt = _legacy.format_persona_system_prompt

__all__ = [
    "PersonaAttributeService",
    "fetch_persona_context",
    "flatten_persona_context",
    "persona_context_to_system_prompt",
    "ContextManager",
    "PersonaContextProvider",
    "JourneyContextProvider",
    "ContextProvider",
    "format_persona_system_prompt",
]
