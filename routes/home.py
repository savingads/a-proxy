from flask import Blueprint, render_template, request
from utils.vpn import is_vpn_running, wait_for_vpn_and_get_ip_info
from config import REGION_LANGUAGE_MAP

home_bp = Blueprint('home', __name__)

@home_bp.route("/")
@home_bp.route("/home")
def index():
    """Render the home page."""
    vpn_running = is_vpn_running()
    ip_info = wait_for_vpn_and_get_ip_info() if vpn_running else {}
    country = ip_info.get("country", "")
    language = REGION_LANGUAGE_MAP.get(country, {}).get("language", "en-US") if vpn_running else "en-US"
    
    # Get the version from VERSION.txt
    try:
        with open('VERSION.txt', 'r') as f:
            version = f.read().strip()
    except:
        version = "Unknown"
        
    return render_template("home.html", 
                          vpn_running=vpn_running, 
                          ip_info=ip_info, 
                          language=language,
                          version=version)

@home_bp.route("/dashboard")
def dashboard():
    """Render the dashboard page."""
    vpn_running = is_vpn_running()
    ip_info = wait_for_vpn_and_get_ip_info() if vpn_running else {}
    
    # Get the version from VERSION.txt
    try:
        with open('VERSION.txt', 'r') as f:
            version = f.read().strip()
    except:
        version = "Unknown"
        
    return render_template("dashboard.html", 
                          vpn_running=vpn_running, 
                          ip_info=ip_info,
                          version=version)

@home_bp.route("/geolocation-test")
def geolocation_test():
    """Render the geolocation test page."""
    target_language = request.args.get("language", "Not specified")
    target_geolocation = request.args.get("geolocation", "Not specified")
    return render_template("geolocation_test.html", 
                          target_language=target_language,
                          target_geolocation=target_geolocation)

@home_bp.route("/get-headers")
def get_headers():
    """Return the request headers as JSON."""
    headers = dict(request.headers)
    return {"accept-language": headers.get("Accept-Language", "Not available")}
