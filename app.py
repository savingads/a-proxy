from flask import Flask, jsonify, render_template, request, redirect, url_for, Response
import subprocess
import requests
import logging
import os
from services import start_vpn
import multiprocessing
from requests.exceptions import ConnectionError
import time

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

REGION_LANGUAGE_MAP = {
    "us5725": "en-US",
    "br53": "pt-BR",
    "de1088": "de-DE",
    "jp514": "ja-JP",
    "za147": "af-ZA"
}

def is_vpn_running():
    result = subprocess.run(["pgrep", "openvpn"], stdout=subprocess.PIPE)
    return result.returncode == 0

def get_ip_info():
    retries = 3
    backoff_factor = 2
    for attempt in range(retries):
        try:
            response = requests.get("https://ipinfo.io")
            response.raise_for_status()
            return response.json()
        except ConnectionError as e:
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

@app.route("/vpn-status")
def vpn_status():
    vpn_running = is_vpn_running()
    ip_info = get_ip_info() if vpn_running else {}
    return jsonify({
        "vpn_running": vpn_running,
        "ip_info": ip_info
    })

@app.route("/")
def index():
    vpn_running = is_vpn_running()
    ip_info = wait_for_vpn_and_get_ip_info() if vpn_running else {}
    language = REGION_LANGUAGE_MAP.get(ip_info.get("region"), "en-US") if vpn_running else "en-US"
    return render_template("index.html", vpn_running=vpn_running, ip_info=ip_info, language=language)

@app.route("/visit-page", methods=["POST"])
def visit_page():
    language = request.form.get("language", "en-US")
    os.system(f"python3 /home/chris/a-proxy/visit_page.py {language}")
    return "Visited Google and took a screenshot."

def vpn_process(region):
    if is_vpn_running():
        logging.debug("Stopping current VPN connection")
        subprocess.run(["sudo", "pkill", "openvpn"])
    vpn_config_path = f"nordvpn/ovpn_udp/{region}.nordvpn.com.udp.ovpn"
    if not os.path.exists(vpn_config_path):
        logging.error(f"VPN configuration file not found: {vpn_config_path}")
        return
    start_vpn(region)

@app.route("/change-region", methods=["POST"])
def change_region():
    region = request.form.get("region")
    logging.debug(f"Changing VPN region to: {region}")
    vpn_proc = multiprocessing.Process(target=vpn_process, args=(region,))
    vpn_proc.start()
    logging.debug("VPN region change process started")
    return redirect(url_for("index"))

if __name__ == "__main__":
    # Automatically start the VPN service with a default region
    default_region = "de1088"  # Change this to your desired default region
    if not is_vpn_running():
        logging.debug(f"Starting VPN with default region: {default_region}")
        vpn_proc = multiprocessing.Process(target=vpn_process, args=(default_region,))
        vpn_proc.start()
    app.run(host="0.0.0.0", port=5000)