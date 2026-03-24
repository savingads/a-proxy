import subprocess
import logging
import os
import requests
import json
from abc import ABC, abstractmethod
import tiktoken  # For token counting

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Context management system
class ContextProvider(ABC):
    """Base interface for context providers"""
    
    @abstractmethod
    def get_context(self, **kwargs):
        """Return context as formatted text"""
        pass
        
    def get_token_estimate(self, text):
        """Estimate tokens used by text"""
        try:
            # Use cl100k_base encoding which is close to what Claude uses
            encoding = tiktoken.get_encoding("cl100k_base")
            tokens = len(encoding.encode(text))
            return tokens
        except Exception as e:
            logger.warning(f"Error estimating tokens: {e}")
            # Fallback: rough estimate based on whitespace-split words × 1.3
            return int(len(text.split()) * 1.3)

class PersonaContextProvider(ContextProvider):
    """Provides persona context"""
    
    def get_context(self, persona_id=None, mode="with", **kwargs):
        """Get formatted persona context"""
        if not persona_id:
            return "You are a helpful assistant."
            
        try:
            raw_context = fetch_persona_context(persona_id)
            if not raw_context:
                return "You are a helpful assistant."
                
            persona_context = flatten_persona_context(raw_context)
            return persona_context_to_system_prompt(persona_context, mode)
        except Exception as e:
            logger.error(f"Error in PersonaContextProvider: {e}")
            return "You are a helpful assistant."
            
class JourneyContextProvider(ContextProvider):
    """Provides journey context"""
    
    def get_context(self, journey_id=None, **kwargs):
        """Get formatted journey context"""
        if not journey_id:
            return ""
            
        try:
            import database
            journey = database.get_journey(journey_id)
            if not journey:
                return ""
                
            # Format journey info
            context_lines = [
                "## Journey Context",
                f"Journey: {journey.get('name', 'Unnamed Journey')}",
            ]
            
            if journey.get('description'):
                context_lines.append(f"Description: {journey['description']}")
                
            if journey.get('journey_type'):
                context_lines.append(f"Type: {journey['journey_type']}")
                
            # Add waypoints summary (limited to avoid token overload)
            try:
                waypoints = database.get_waypoints(journey_id)
                if waypoints:
                    context_lines.append(f"\nThis journey contains {len(waypoints)} waypoints:")
                    # Include just the most recent 3 waypoints
                    for wp in waypoints[-3:]:
                        title = wp.get('title', 'Untitled waypoint')
                        context_lines.append(f"- {title}")
                        if wp.get('notes'):
                            # Truncate notes if too long
                            notes = wp['notes']
                            if len(notes) > 100:
                                notes = notes[:97] + "..."
                            context_lines.append(f"  Note: {notes}")
            except Exception as wp_error:
                logger.error(f"Error getting waypoints: {wp_error}")
            
            return "\n".join(context_lines)
        except Exception as e:
            logger.error(f"Error in JourneyContextProvider: {e}")
            return ""

class ContextManager:
    """Manages multiple context providers and handles token limits"""
    
    def __init__(self, max_tokens=8000):
        self.providers = []
        self.max_tokens = max_tokens
        
    def add_provider(self, provider):
        self.providers.append(provider)
        
    def get_combined_context(self, **kwargs):
        """Get combined context from all providers, respecting token limits"""
        contexts = []
        total_tokens = 0
        
        for provider in self.providers:
            context = provider.get_context(**kwargs)
            if not context:
                continue
                
            token_estimate = provider.get_token_estimate(context)
            
            # If adding this context would exceed our limit, skip it
            if total_tokens + token_estimate > self.max_tokens:
                logger.warning(f"Skipping context from {provider.__class__.__name__} due to token limits")
                continue
                
            contexts.append(context)
            total_tokens += token_estimate
            
        # Combine all contexts
        combined = "\n\n".join(contexts)
        
        # If we have a conversation mode specified, add a clear instruction at the end
        mode = kwargs.get("mode")
        if mode == "with":
            combined += "\n\nYou are the persona described above. Respond to the user's messages accordingly."
        elif mode == "as":
            combined += "\n\nThe user is roleplaying as the persona described above. You are responding to them, not as the persona."
        
        return combined

def start_vpn(region):
    vpn_config_path = f"nordvpn/ovpn_udp/{region}.nordvpn.com.udp.ovpn"
    if not os.path.exists(vpn_config_path):
        logging.error(f"VPN configuration file not found: {vpn_config_path}")
        return
    auth_file_path = "nordvpn/auth.txt"
    if not os.path.exists(auth_file_path):
        logging.error(f"VPN authentication file not found: {auth_file_path}")
        return
    logging.debug(f"Starting VPN with configuration: {vpn_config_path} and auth file: {auth_file_path}")
    subprocess.run(["sudo", "openvpn", "--config", vpn_config_path, "--auth-user-pass", auth_file_path])

def start_vpn_service():
    logging.debug("Starting VPN service without connecting to a region")
    # Add logic to start the VPN service without connecting to a region
    # This could be a command to start the VPN service in a general way
    subprocess.run(["sudo", "systemctl", "start", "openvpn"])

def fetch_persona_context(persona_id, persona_service_url="http://localhost:5050/api/v1/personas/"):
    """
    Fetch persona details from the database.
    Returns a dict of persona attributes or None if not found.
    """
    try:
        # Import here to avoid circular imports
        import database
        persona = database.get_persona(persona_id)
        if not persona:
            logger.error(f"Persona not found: {persona_id}")
            return None
        return persona
    except Exception as e:
        logger.error(f"Error fetching persona context: {e}")
        return None

def format_persona_system_prompt(persona_data, mode="with"):
    """
    Format persona context as a system prompt for Claude.
    mode: 'with' (Claude is the persona) or 'as' (Claude is the other party, user is persona)
    """
    if not persona_data:
        return "You are a helpful assistant."
    name = persona_data.get("name", "Unknown")
    age = persona_data.get("age", "?")
    occupation = persona_data.get("occupation", "?")
    psychographics = persona_data.get("psychographics", "?")
    behavioral_traits = persona_data.get("behavioral_traits", "?")
    context = persona_data.get("contextual_info", "?")
    if mode == "with":
        return (
            f"You are {name}. Here are your details:\n"
            f"- Age: {age}\n"
            f"- Occupation: {occupation}\n"
            f"- Psychographics: {psychographics}\n"
            f"- Behavioral traits: {behavioral_traits}\n"
            f"- Contextual info: {context}\n"
            "Respond as this persona in all interactions."
        )
    elif mode == "as":
        return (
            f"You are assisting a user who is roleplaying as {name}. Here are their details:\n"
            f"- Age: {age}\n"
            f"- Occupation: {occupation}\n"
            f"- Psychographics: {psychographics}\n"
            f"- Behavioral traits: {behavioral_traits}\n"
            f"- Contextual info: {context}\n"
            "Respond to the user as if they are this persona."
        )
    else:
        return "You are a helpful assistant."

def persona_context_to_system_prompt(persona_context, mode="with"):
    """
    Convert the full persona_context dict (with Demographic, Psychographic, Behavioral, Contextual)
    into a compact, readable system prompt for Claude.
    """
    if not persona_context:
        return "You are a helpful assistant."
    lines = ["Persona Context:"]
    for section, fields in persona_context.items():
        if fields:
            lines.append(f"{section}:")
            for key, value in fields.items():
                if value:
                    lines.append(f"- {key.replace('_', ' ').title()}: {value}")
    if mode == "with":
        lines.append("Respond as this persona in all interactions.")
    elif mode == "as":
        lines.append("You are assisting a user who is roleplaying as this persona. Respond accordingly.")
    return "\n".join(lines)

def flatten_persona_context(raw_context):
    """
    Flatten all persona fields for sidebar/system prompt display.
    Returns a dict with Demographic, Psychographic, Behavioral, Contextual as sub-dicts.
    """
    if not raw_context:
        return {}
    demographic = raw_context.get("demographic", {})
    psychographic = raw_context.get("psychographic", {})
    behavioral = raw_context.get("behavioral", {})
    contextual = raw_context.get("contextual", {})
    # Convert lists to comma-separated strings for compactness
    def compact(d):
        return {k: ", ".join(v) if isinstance(v, list) else v for k, v in d.items()}
    return {
        "Demographic": compact(demographic),
        "Psychographic": compact(psychographic),
        "Behavioral": compact(behavioral),
        "Contextual": compact(contextual)
    }

if __name__ == "__main__":
    start_vpn("de1088")
