import subprocess
import logging

logging.basicConfig(level=logging.DEBUG)

def start_vpn(region):
    config_file = f"nordvpn/ovpn_udp/{region}.nordvpn.com.udp.ovpn"
    command = f"sudo openvpn --config {config_file} --auth-user-pass auth.txt"
    logging.debug(f"Starting VPN with command: {command}")
    result = subprocess.run(command, shell=True)
    logging.debug(f"VPN start result: {result}")

if __name__ == "__main__":
    start_vpn("de1088")



