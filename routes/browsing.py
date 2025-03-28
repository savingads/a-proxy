from flask import Blueprint, request, redirect, url_for, flash, Response, session
import os
import logging
import subprocess
from utils.vpn import is_vpn_running

browsing_bp = Blueprint('browsing', __name__)

@browsing_bp.route("/visit-page", methods=["POST"])
def visit_page():
    """Visit a webpage with specified language and geolocation settings."""
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

@browsing_bp.route("/archive_page", methods=["POST"])
def archive_page():
    """Archive a webpage with specified language, geolocation, and persona settings."""
    url = request.form.get("url", "https://www.google.com")
    language = request.form.get("language", "en-US")
    geolocation = request.form.get("geolocation")
    persona_id = request.form.get("persona_id")
    
    # Convert persona_id to int if it's not None
    if persona_id:
        try:
            persona_id = int(persona_id)
        except ValueError:
            persona_id = None
    
    # Build the command with proper argument formatting
    command = f"python3 /home/chris/a-proxy/archive_page.py '{url}' --language '{language}'"
    if geolocation:
        command += f" --geolocation '{geolocation}'"
    if persona_id:
        command += f" --persona-id {persona_id}"
    
    logging.debug(f"Executing command: {command}")
    os.system(command)
    
    flash(f"Archived {url} with language {language} and geolocation {geolocation or 'not specified'}.", "success")
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
