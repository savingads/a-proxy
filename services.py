import subprocess
import logging
import os
import requests

logging.basicConfig(level=logging.DEBUG)

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
    Fetch persona details from the persona-service REST API.
    Returns a dict of persona attributes or None if not found.
    """
    url = f"{persona_service_url}{persona_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching persona context: {e}")
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

if __name__ == "__main__":
    start_vpn("de1088")



