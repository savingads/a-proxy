"""
Network/proxy management routes.

Replaces the Linux-only VPN routes (routes/vpn.py) with
cross-platform proxy configuration endpoints.
"""
from flask import Blueprint, jsonify, request, session
import logging
from config import REGION_LANGUAGE_MAP
from utils.network import is_proxy_configured, get_proxy_url, get_ip_info

network_bp = Blueprint('network', __name__)


@network_bp.route("/network-status")
def network_status():
    """Get current network/proxy status and IP information."""
    proxy_url = session.get("proxy_url") or get_proxy_url()
    proxy_configured = bool(proxy_url)
    ip_info = get_ip_info(proxy_url) if proxy_configured else get_ip_info()
    return jsonify({
        "proxy_configured": proxy_configured,
        "ip_info": ip_info,
    })


@network_bp.route("/set-proxy", methods=["POST"])
def set_proxy():
    """Set proxy URL in session for geo-IP routing."""
    proxy_url = request.form.get("proxy_url", "").strip()
    if proxy_url:
        session["proxy_url"] = proxy_url
        logging.debug(f"Proxy set to: {proxy_url}")
        return jsonify({"status": "configured", "proxy_url": proxy_url})
    return jsonify({"error": "No proxy URL provided"}), 400


@network_bp.route("/clear-proxy", methods=["POST"])
def clear_proxy():
    """Clear proxy URL from session."""
    session.pop("proxy_url", None)
    logging.debug("Proxy cleared")
    return jsonify({"status": "cleared"})


@network_bp.route("/get-region-geolocation/<region_code>")
def get_region_geolocation(region_code):
    """Get geolocation information for a region code."""
    region_code = region_code.upper()
    region = REGION_LANGUAGE_MAP.get(region_code)
    if region and "geolocation" in region:
        return jsonify({
            "geolocation": region["geolocation"],
            "name": region.get("name", region_code),
            "language": region.get("language"),
            "timezone": region.get("timezone"),
        })
    return jsonify({"error": "Region not found"}), 404
