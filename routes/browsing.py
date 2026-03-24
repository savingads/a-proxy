from flask import Blueprint, request, redirect, url_for, flash, Response, session
import os
import logging
from config import PROXY_URL
from utils.browser import BrowserManager

browsing_bp = Blueprint('browsing', __name__)

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
