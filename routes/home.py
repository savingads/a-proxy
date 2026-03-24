from flask import Blueprint, render_template, request, session
from utils.network import is_proxy_configured, get_proxy_url, get_ip_info
from config import REGION_LANGUAGE_MAP

home_bp = Blueprint('home', __name__)


def _get_version():
    """Read version from VERSION.txt."""
    try:
        with open('VERSION.txt', 'r') as f:
            return f.read().strip()
    except Exception:
        return "Unknown"


@home_bp.route("/")
@home_bp.route("/home")
def index():
    """Render the home page."""
    proxy_url = session.get("proxy_url") or get_proxy_url()
    proxy_configured = bool(proxy_url)
    ip_info = get_ip_info(proxy_url) if proxy_configured else get_ip_info()
    country = ip_info.get("country", "")
    language = REGION_LANGUAGE_MAP.get(country, {}).get("language", "en-US")

    return render_template("home.html",
                           proxy_configured=proxy_configured,
                           ip_info=ip_info,
                           language=language,
                           version=_get_version())


@home_bp.route("/dashboard")
def dashboard():
    """Render the dashboard page."""
    proxy_url = session.get("proxy_url") or get_proxy_url()
    proxy_configured = bool(proxy_url)
    ip_info = get_ip_info(proxy_url) if proxy_configured else get_ip_info()

    return render_template("dashboard.html",
                           proxy_configured=proxy_configured,
                           ip_info=ip_info,
                           version=_get_version())

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
