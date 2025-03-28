from flask import Blueprint, jsonify, request, redirect, url_for
from utils.vpn import is_vpn_running, get_ip_info, wait_for_vpn_and_get_ip_info, vpn_process
import multiprocessing
import logging
from config import REGION_LANGUAGE_MAP

vpn_bp = Blueprint('vpn', __name__)

@vpn_bp.route("/vpn-status")
def vpn_status():
    """Get current VPN status and IP information."""
    vpn_running = is_vpn_running()
    ip_info = get_ip_info() if vpn_running else {}
    return jsonify({
        "vpn_running": vpn_running,
        "ip_info": ip_info
    })

@vpn_bp.route("/change-region", methods=["POST"])
def change_region():
    """Change VPN region."""
    region = request.form.get("region")
    logging.debug(f"Changing VPN region to: {region}")
    vpn_proc = multiprocessing.Process(target=vpn_process, args=(region,))
    vpn_proc.start()
    logging.debug("VPN region change process started")
    return jsonify({"status": "changing", "region": region})

@vpn_bp.route("/get-region-geolocation/<region_code>")
def get_region_geolocation(region_code):
    """Get geolocation information for a region."""
    region_code = region_code.upper()
    if region_code in REGION_LANGUAGE_MAP:
        return jsonify({
            "geolocation": REGION_LANGUAGE_MAP[region_code]["geolocation"],
            "name": REGION_LANGUAGE_MAP[region_code]["name"]
        })
    return jsonify({"error": "Region not found"}), 404

@vpn_bp.route("/start_vpn", methods=["POST"])
def start_vpn_route():
    """Start VPN with specified region."""
    if 'region' not in request.form:
        return jsonify({"error": "No region provided"}), 400
    
    region = request.form['region']
    vpn_proc = multiprocessing.Process(target=vpn_process, args=(region,))
    vpn_proc.start()
    return redirect(url_for('home.index'))
