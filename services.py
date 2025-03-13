import subprocess
import logging
import os

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

if __name__ == "__main__":
    start_vpn("de1088")



