import subprocess
import requests
import logging
import time
import os
import multiprocessing
from config import REGION_LANGUAGE_MAP

logging.basicConfig(level=logging.DEBUG)

def is_vpn_running():
    """Check if OpenVPN process is running."""
    result = subprocess.run(["pgrep", "openvpn"], stdout=subprocess.PIPE)
    return result.returncode == 0

def get_ip_info():
    """Get current IP information from ipinfo.io."""
    retries = 3
    backoff_factor = 2
    for attempt in range(retries):
        try:
            response = requests.get("https://ipinfo.io")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as e:
            logging.error(f"Failed to get IP info: {e}")
            return {"error": "Failed to get IP info"}
        except requests.exceptions.RequestException as e:
            logging.error(f"Request exception: {e}")
            if response.status_code == 429:  # Too Many Requests
                wait_time = backoff_factor ** attempt
                logging.debug(f"Rate limited. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return {"error": "Request exception"}
    return {"error": "Failed to get IP info after retries"}

def wait_for_vpn_and_get_ip_info():
    """Wait for VPN to establish and get IP info."""
    retries = 5
    backoff_factor = 2
    for attempt in range(retries):
        if is_vpn_running():
            ip_info = get_ip_info()
            if "error" not in ip_info:
                return ip_info
        wait_time = backoff_factor ** attempt
        logging.debug(f"Waiting for VPN to establish. Retrying in {wait_time} seconds...")
        time.sleep(wait_time)
    return {"error": "Failed to get IP info after retries"}

def vpn_process(region=None):
    """Start or change VPN connection."""
    if is_vpn_running():
        logging.debug("Stopping current VPN connection")
        subprocess.run(["sudo", "pkill", "openvpn"])
        time.sleep(5)  # Wait for the VPN process to stop
    
    if region:
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
    else:
        # Import here to avoid circular imports
        from services import start_vpn_service
        start_vpn_service()  # Start the VPN service without connecting to a region
