from flask import Flask, jsonify, render_template, request, redirect, url_for, Response
import subprocess
import requests
import logging
import os
from services import start_vpn, start_vpn_service
import multiprocessing
from requests.exceptions import ConnectionError
import time

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

REGION_LANGUAGE_MAP = {
    "US": {
        "name": "United States",
        "language": "en-US",
        "geolocation": "37.0902,-95.7129",
        "server": "us123.nordvpn.com.udp"
    },
    "BR": {
        "name": "Brazil",
        "language": "pt-BR",
        "geolocation": "-14.2350,-51.9253",
        "server": "br123.nordvpn.com.udp"
    },
    "DE": {
        "name": "Germany",
        "language": "de-DE",
        "geolocation": "51.1657,10.4515",
        "server": "de123.nordvpn.com.udp"
    },
    "JP": {
        "name": "Japan",
        "language": "ja-JP",
        "geolocation": "36.2048,138.2529",
        "server": "jp123.nordvpn.com.udp"
    },
    "ZA": {
        "name": "South Africa",
        "language": "af-ZA",
        "geolocation": "-30.5595,22.9375",
        "server": "za123.nordvpn.com.udp"
    }
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
    country = ip_info.get("country", "")
    language = REGION_LANGUAGE_MAP.get(country, "en-US") if vpn_running else "en-US"
    return render_template("index.html", vpn_running=vpn_running, ip_info=ip_info, language=language)

@app.route("/visit-page", methods=["POST"])
def visit_page():
    url = request.form.get("url", "https://www.google.com")
    language = request.form.get("language", "en-US")
    geolocation = request.form.get("geolocation", None)
    
    # If geolocation is not provided in the form, try to get it from the Persona section
    if not geolocation:
        geolocation = request.form.get("geolocation", None)
    
    # Build the command with proper argument formatting
    command = f"python3 /home/chris/a-proxy/visit_page.py '{url}' --language '{language}'"
    if geolocation:
        command += f" --geolocation '{geolocation}'"
    
    logging.debug(f"Executing command: {command}")
    os.system(command)
    
    return f"Visited {url} with language {language} and geolocation {geolocation or 'not specified'}. Screenshot saved."

@app.route("/archive_page", methods=["POST"])
def archive_page():
    #language = request.form.get("language", "en-US")
    #os.system(f"python3 /home/chris/a-proxy/archive_page.py {language}")
    return "Archived Page."

def vpn_process(region=None):
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
        start_vpn_service()  # Start the VPN service without connecting to a region

@app.route("/change-region", methods=["POST"])
def change_region():
    region = request.form.get("region")
    logging.debug(f"Changing VPN region to: {region}")
    vpn_proc = multiprocessing.Process(target=vpn_process, args=(region,))
    vpn_proc.start()
    logging.debug("VPN region change process started")
    return jsonify({"status": "changing", "region": region})

@app.route("/get-region-geolocation/<region_code>")
def get_region_geolocation(region_code):
    region_code = region_code.upper()
    if region_code in REGION_LANGUAGE_MAP:
        return jsonify({
            "geolocation": REGION_LANGUAGE_MAP[region_code]["geolocation"],
            "name": REGION_LANGUAGE_MAP[region_code]["name"]
        })
    return jsonify({"error": "Region not found"}), 404

@app.route("/start_vpn", methods=["POST"])
def start_vpn_route():
    if 'region' not in request.form:
        return jsonify({"error": "No region provided"}), 400
    region = request.form['region']
    # Logic to start the VPN with the selected region
    vpn_proc = multiprocessing.Process(target=vpn_process, args=(region,))
    vpn_proc.start()
    return redirect(url_for('index'))

if __name__ == "__main__":
    # Automatically start the VPN service without connecting to a region
    #if not is_vpn_running():
       # logging.debug("Starting VPN service without connecting to a region")
       # vpn_proc = multiprocessing.Process(target=vpn_process)
       # vpn_proc.start()

    
    
    app.run(debug=True, use_reloader=True)
