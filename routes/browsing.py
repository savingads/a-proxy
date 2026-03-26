from flask import Blueprint, request, redirect, url_for, flash, Response, session, jsonify
import logging
from config import PROXY_URL, REGION_LANGUAGE_MAP
from utils.browser import BrowserManager
from utils.persona_client_db import get_db_persona_client

browsing_bp = Blueprint('browsing', __name__)


def _get_persona_browser_settings(persona):
    """Extract browser context settings from a persona dict."""
    demo = persona.get("demographic", {})
    locale = demo.get("language", "en-US")

    lat = demo.get("latitude")
    lng = demo.get("longitude")
    geolocation = f"{lat},{lng}" if lat and lng else None

    country = demo.get("country", "")
    region_info = REGION_LANGUAGE_MAP.get(country, {})
    timezone_id = region_info.get("timezone")

    proxy = session.get("proxy_url") or PROXY_URL

    return {
        "locale": locale,
        "geolocation": geolocation,
        "timezone_id": timezone_id,
        "proxy": proxy,
    }

@browsing_bp.route("/visit-page", methods=["POST"])
def visit_page():
    """Visit a webpage with specified language and geolocation settings."""
    url = request.form.get("url", "https://www.google.com")
    language = request.form.get("language", "en-US")
    geolocation = request.form.get("geolocation", None)
    take_screenshot = request.form.get("take_screenshot", "false").lower() == "true"
    proxy = session.get("proxy_url") or PROXY_URL

    logging.debug(f"Visiting {url} with language={language}, geolocation={geolocation}")

    manager = BrowserManager.get_instance()
    result = manager.visit_page(
        url=url,
        locale=language,
        geolocation=geolocation,
        proxy=proxy,
        screenshot=take_screenshot,
    )

    msg = f"Visited {url} with language {language} and geolocation {geolocation or 'not specified'}."
    if take_screenshot and result.get("screenshot_path"):
        msg += f" Screenshot saved to {result['screenshot_path']}."
    return msg

@browsing_bp.route("/archive_page", methods=["POST"])
def archive_page():
    """Archive a webpage with specified language, geolocation, and persona settings."""
    url = request.form.get("url", "https://www.google.com")
    language = request.form.get("language", "en-US")
    geolocation = request.form.get("geolocation")
    persona_id = request.form.get("persona_id")
    proxy = session.get("proxy_url") or PROXY_URL

    if persona_id:
        try:
            persona_id = int(persona_id)
        except ValueError:
            persona_id = None

    logging.debug(f"Archiving {url} with language={language}, geolocation={geolocation}")

    manager = BrowserManager.get_instance()
    result = manager.archive_page(
        url=url,
        locale=language,
        geolocation=geolocation,
        proxy=proxy,
        persona_id=persona_id,
    )

    if result:
        flash(f"Archived {url} with language {language} and geolocation {geolocation or 'not specified'}.", "success")
    else:
        flash(f"Failed to archive {url}.", "danger")
    return redirect(url_for('persona.dashboard'))

@browsing_bp.route("/test-geolocation", methods=["POST"])
def test_geolocation():
    """Redirect to the geolocation test page with the specified settings."""
    language = request.form.get("language", "en-US")
    geolocation = request.form.get("geolocation", None)
    
    # Fix geolocation format if missing comma
    if geolocation and '-' in geolocation and ',' not in geolocation:
        # Extract coordinates and add a comma
        parts = geolocation.split('-', 1)
        if len(parts) == 2:
            geolocation = f"{parts[0]},{'-' + parts[1]}"
            logging.debug(f"Fixed geolocation format from {request.form.get('geolocation')} to {geolocation}")
    
    # Store the language and geolocation in the session so we can access them in the test page
    session['test_language'] = language
    session['test_geolocation'] = geolocation
    
    # Directly redirect to the geolocation test page with parameters
    return redirect(url_for('home.geolocation_test', language=language, geolocation=geolocation))


# ── Headful browsing session endpoints ──────────────────────────────

@browsing_bp.route("/start-session", methods=["POST"])
def start_session():
    """Launch a headful browsing session for a persona."""
    data = request.get_json() or request.form
    persona_id = data.get("persona_id")
    start_url = data.get("start_url", "https://www.google.com")

    if not persona_id:
        return jsonify({"success": False, "error": "persona_id is required"}), 400

    try:
        persona_id = int(persona_id)
        client = get_db_persona_client()
        persona = client.get_persona(persona_id)
        if not persona:
            return jsonify({"success": False, "error": "Persona not found"}), 404

        settings = _get_persona_browser_settings(persona)
        manager = BrowserManager.get_instance()
        manager.start_session(
            persona_id=persona_id,
            start_url=start_url,
            **settings,
        )
        return jsonify({"success": True, "persona_id": persona_id})
    except Exception as e:
        logging.error(f"Error starting session: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@browsing_bp.route("/session-status")
def session_status():
    """Return the current browsing session status."""
    manager = BrowserManager.get_instance()
    return jsonify(manager.get_session_status())


@browsing_bp.route("/capture-page", methods=["POST"])
def capture_page():
    """Take a screenshot of the active session page."""
    manager = BrowserManager.get_instance()
    result = manager.capture_page()
    if result:
        return jsonify({"success": True, **result})
    return jsonify({"success": False, "error": "No active session"}), 400


@browsing_bp.route("/archive-page-from-session", methods=["POST"])
def archive_page_from_session():
    """Archive the current page from the active browsing session."""
    manager = BrowserManager.get_instance()
    result = manager.archive_session_page()
    if result:
        return jsonify({"success": True, **result})
    return jsonify({"success": False, "error": "No active session or archive failed"}), 400


@browsing_bp.route("/stop-session", methods=["POST"])
def stop_session():
    """Stop the active browsing session."""
    manager = BrowserManager.get_instance()
    manager.stop_session()
    return jsonify({"success": True})
