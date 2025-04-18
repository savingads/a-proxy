from flask import Blueprint, request, redirect, url_for, flash, render_template, jsonify
import database
import json
import logging
import os
from datetime import datetime
from PIL import Image
from io import BytesIO
import base64

journey_bp = Blueprint('journey', __name__)

@journey_bp.route("/journeys")
def list_journeys():
    """List all journeys."""
    journeys = database.get_all_journeys()
    
    # Add waypoint count for each journey
    for journey in journeys:
        waypoints = database.get_waypoints(journey['id'])
        journey['waypoint_count'] = len(waypoints) if waypoints else 0
        
    return render_template("journey_list.html", journeys=journeys)

@journey_bp.route("/journey/create", methods=["GET", "POST"])
def create_journey():
    """Create a new journey."""
    # Check if this is an AJAX request
    is_ajax_request = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == "POST":
        try:
            # Get form data
            name = request.form.get("name")
            description = request.form.get("description", "")
            persona_id = request.form.get("persona_id")
            journey_type = request.form.get("journey_type", "marketing")
            
            # Convert empty string to None for foreign key
            if not persona_id:
                persona_id = None
            
            # Create the journey
            journey_id = database.create_journey(
                name=name,
                description=description,
                persona_id=persona_id,
                journey_type=journey_type
            )
            
            # Handle AJAX request
            if is_ajax_request:
                return jsonify({
                    'success': True,
                    'journey_id': journey_id,
                    'message': f"Journey '{name}' created successfully!"
                })
            
            # Handle regular form submission
            flash(f"Journey '{name}' created successfully!", "success")
            return redirect(url_for('journey.view_journey', journey_id=journey_id))
        
        except Exception as e:
            logging.error(f"Error creating journey: {e}")
            
            # Handle AJAX request error
            if is_ajax_request:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
            
            # Handle regular form submission error
            flash(f"Error creating journey: {str(e)}", "danger")
    
    # Import inside function to avoid circular imports
    from utils.persona_client import get_client
    
    try:
        # Get personas from the API
        client = get_client()
        result = client.get_personas(page=1, per_page=100)
        personas = result.get('personas', [])
    except Exception as e:
        logging.error(f"Error getting personas from API: {e}")
        personas = []
        flash(f"Error loading personas: {str(e)}", "danger")
        
    return render_template("journey_create.html", personas=personas)

@journey_bp.route("/journey/<int:journey_id>")
def view_journey(journey_id):
    """View a specific journey and its waypoints."""
    journey = database.get_journey(journey_id)
    if not journey:
        flash("Journey not found", "danger")
        return redirect(url_for('journey.list_journeys'))
    
    waypoints = database.get_waypoints(journey_id)
    return render_template("journey_view.html", journey=journey, waypoints=waypoints)

@journey_bp.route("/journey/<int:journey_id>/edit", methods=["GET", "POST"])
def edit_journey(journey_id):
    """Edit a journey's details."""
    journey = database.get_journey(journey_id)
    if not journey:
        flash("Journey not found", "danger")
        return redirect(url_for('journey.list_journeys'))
    
    if request.method == "POST":
        try:
            # Get form data
            name = request.form.get("name")
            description = request.form.get("description")
            persona_id = request.form.get("persona_id") or None
            journey_type = request.form.get("journey_type")
            status = request.form.get("status")
            
            # Update the journey
            database.update_journey(
                journey_id=journey_id,
                name=name,
                description=description,
                persona_id=persona_id,
                journey_type=journey_type,
                status=status
            )
            
            flash(f"Journey updated successfully!", "success")
            return redirect(url_for('journey.view_journey', journey_id=journey_id))
        
        except Exception as e:
            logging.error(f"Error updating journey: {e}")
            flash(f"Error updating journey: {str(e)}", "danger")
    
    # Import inside function to avoid circular imports
    from utils.persona_client import get_client
    
    try:
        # Get personas from the API
        client = get_client()
        result = client.get_personas(page=1, per_page=100)
        personas = result.get('personas', [])
    except Exception as e:
        logging.error(f"Error getting personas from API: {e}")
        personas = []
        flash(f"Error loading personas: {str(e)}", "danger")
        
    # Get waypoints for the journey
    waypoints = database.get_waypoints(journey_id)
    
    return render_template("journey_edit.html", journey=journey, personas=personas, waypoints=waypoints)

@journey_bp.route("/journey/<int:journey_id>/delete", methods=["POST"])
def delete_journey(journey_id):
    """Delete a journey and all its waypoints."""
    try:
        database.delete_journey(journey_id)
        flash("Journey deleted successfully!", "success")
        return redirect(url_for('journey.list_journeys'))
    
    except Exception as e:
        logging.error(f"Error deleting journey: {e}")
        flash(f"Error deleting journey: {str(e)}", "danger")
        return redirect(url_for('journey.view_journey', journey_id=journey_id))

@journey_bp.route("/journey/<int:journey_id>/browse")
def browse_journey(journey_id):
    """Start a browsing session for this journey."""
    journey = database.get_journey(journey_id)
    if not journey:
        flash("Journey not found", "danger")
        return redirect(url_for('journey.list_journeys'))
    
    # Get persona data if a persona is associated with this journey
    persona = None
    if journey['persona_id']:
        # Import inside function to avoid circular imports
        from utils.persona_client import get_client
        try:
            client = get_client()
            persona = client.get_persona(journey['persona_id'])
        except Exception as e:
            logging.error(f"Error getting persona {journey['persona_id']}: {e}")
            flash(f"Error loading persona: {str(e)}", "danger")
    
    # Get existing waypoints
    waypoints = database.get_waypoints(journey_id)
    
    return render_template("journey_browse.html", journey=journey, persona=persona, waypoints=waypoints)

@journey_bp.route("/journey/<int:journey_id>/add-waypoint", methods=["POST"])
def add_waypoint(journey_id):
    """Add a waypoint to a journey."""
    try:
        # Get form data
        url = request.form.get("url")
        title = request.form.get("title")
        notes = request.form.get("notes", "")
        
        # Handle screenshot if provided
        screenshot_path = None
        if 'screenshot' in request.form and request.form.get('screenshot'):
            # Decode base64 screenshot
            screenshot_data = request.form.get('screenshot').split(',')[1]
            screenshot_bytes = base64.b64decode(screenshot_data)
            
            # Create screenshots directory if it doesn't exist
            screenshots_dir = os.path.join(os.getcwd(), 'screenshots')
            if not os.path.exists(screenshots_dir):
                os.makedirs(screenshots_dir)
            
            # Generate filename based on timestamp
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            screenshot_path = os.path.join('screenshots', f'journey-{journey_id}-waypoint-{timestamp}.png')
            
            # Save the screenshot
            with open(screenshot_path, 'wb') as f:
                f.write(screenshot_bytes)
        
        # Collect additional metadata
        metadata = {
            "browser_timestamp": datetime.now().isoformat(),
            "user_agent": request.headers.get('User-Agent'),
        }
        
        # Add the waypoint
        waypoint_id = database.add_waypoint(
            journey_id=journey_id,
            url=url,
            title=title,
            notes=notes,
            screenshot_path=screenshot_path,
            metadata=metadata
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "success": True, 
                "waypoint_id": waypoint_id,
                "message": "Waypoint added successfully!"
            })
        else:
            flash("Waypoint added successfully!", "success")
            return redirect(url_for('journey.browse_journey', journey_id=journey_id))
    
    except Exception as e:
        logging.error(f"Error adding waypoint: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "error": str(e)}), 500
        else:
            flash(f"Error adding waypoint: {str(e)}", "danger")
            return redirect(url_for('journey.browse_journey', journey_id=journey_id))

@journey_bp.route("/journey/waypoint/<int:waypoint_id>/edit", methods=["POST"])
def edit_waypoint(waypoint_id):
    """Edit a waypoint's details."""
    try:
        # Get waypoint to determine journey_id
        waypoint = database.get_waypoint(waypoint_id)
        if not waypoint:
            return jsonify({"success": False, "error": "Waypoint not found"}), 404
        
        journey_id = waypoint['journey_id']
        
        # Get form data
        title = request.form.get("title")
        notes = request.form.get("notes")
        
        # Update the waypoint
        database.update_waypoint(
            waypoint_id=waypoint_id,
            title=title,
            notes=notes
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "success": True, 
                "message": "Waypoint updated successfully!"
            })
        else:
            flash("Waypoint updated successfully!", "success")
            return redirect(url_for('journey.view_journey', journey_id=journey_id))
    
    except Exception as e:
        logging.error(f"Error updating waypoint: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "error": str(e)}), 500
        else:
            flash(f"Error updating waypoint: {str(e)}", "danger")
            return redirect(url_for('journey.view_journey', journey_id=journey_id))

@journey_bp.route("/journey/waypoint/<int:waypoint_id>/delete", methods=["POST"])
def delete_waypoint(waypoint_id):
    """Delete a waypoint."""
    try:
        # Get waypoint to determine journey_id
        waypoint = database.get_waypoint(waypoint_id)
        if not waypoint:
            return jsonify({"success": False, "error": "Waypoint not found"}), 404
        
        journey_id = waypoint['journey_id']
        
        # Delete the waypoint
        database.delete_waypoint(waypoint_id)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "success": True, 
                "message": "Waypoint deleted successfully!"
            })
        else:
            flash("Waypoint deleted successfully!", "success")
            return redirect(url_for('journey.view_journey', journey_id=journey_id))
    
    except Exception as e:
        logging.error(f"Error deleting waypoint: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "error": str(e)}), 500
        else:
            flash(f"Error deleting waypoint: {str(e)}", "danger")
            return redirect(url_for('journey.view_journey', journey_id=journey_id))

@journey_bp.route("/journey/<int:journey_id>/visualize")
def visualize_journey(journey_id):
    """Visualize a journey's waypoints as a timeline."""
    journey = database.get_journey(journey_id)
    if not journey:
        flash("Journey not found", "danger")
        return redirect(url_for('journey.list_journeys'))
    
    waypoints = database.get_waypoints(journey_id)
    return render_template("journey_visualize.html", journey=journey, waypoints=waypoints)

@journey_bp.route("/journey/<int:journey_id>/complete", methods=["POST"])
def complete_journey(journey_id):
    """Mark a journey as completed."""
    try:
        database.update_journey(journey_id=journey_id, status='completed')
        flash("Journey marked as completed!", "success")
        return redirect(url_for('journey.view_journey', journey_id=journey_id))
    
    except Exception as e:
        logging.error(f"Error completing journey: {e}")
        flash(f"Error completing journey: {str(e)}", "danger")
        return redirect(url_for('journey.view_journey', journey_id=journey_id))

@journey_bp.route("/direct-browse/<int:persona_id>", methods=["GET", "POST"])
def direct_browse(persona_id):
    """Start a lightweight browsing session with a persona."""
    # Import inside function to avoid circular imports
    from utils.persona_client import get_client
    
    # Get persona data
    persona = None
    try:
        client = get_client()
        persona = client.get_persona(persona_id)
        if not persona:
            flash("Persona not found", "danger")
            return redirect(url_for('journey.browse_as'))
    except Exception as e:
        logging.error(f"Error getting persona {persona_id}: {e}")
        flash(f"Error loading persona: {str(e)}", "danger")
        return redirect(url_for('journey.browse_as'))
    
    # Get existing journeys for this persona to show in the waypoint form
    try:
        existing_journeys = [j for j in database.get_all_journeys() if j['persona_id'] == persona_id]
    except Exception as e:
        logging.error(f"Error getting journeys for persona {persona_id}: {e}")
        existing_journeys = []
    
    # Handle URL submission
    url_content = None
    visited_url = None
    
    if request.method == "POST":
        url = request.form.get("url", "")
        if url:
            visited_url = url
            # For now, just display the URL that was entered
            url_content = f"You entered: {url}"
            
            # Record that we're using this persona's language and location
            language = persona.get('demographic', {}).get('language', 'en-US')
            
            # Get geolocation from persona if available
            lat = persona.get('demographic', {}).get('latitude')
            lng = persona.get('demographic', {}).get('longitude')
            geolocation = f"{lat},{lng}" if lat and lng else None
            
            # Log the browsing for debugging purposes
            logging.info(f"Browsing as {persona['name']} to {url} with language {language} and geolocation {geolocation}")

    # Render the direct browsing template
    return render_template("direct_browse.html", 
                          persona=persona, 
                          existing_journeys=existing_journeys,
                          url_content=url_content,
                          visited_url=visited_url)

@journey_bp.route("/save-waypoint/<int:persona_id>", methods=["POST"])
def save_page_as_waypoint(persona_id):
    """Save a page as a waypoint from a direct browsing session."""
    try:
        # Get form data
        url = request.form.get("url")
        title = request.form.get("title")
        notes = request.form.get("notes", "")
        journey_option = request.form.get("journey_option")
        
        # Get or create journey
        journey_id = None
        
        if journey_option == "existing":
            # Use existing journey
            journey_id = request.form.get("journey_id")
            if not journey_id:
                flash("Please select a journey", "danger")
                return redirect(url_for('journey.direct_browse', persona_id=persona_id))
        else:
            # Create new journey
            journey_name = request.form.get("journey_name")
            journey_description = request.form.get("journey_description", "")
            journey_type = request.form.get("journey_type", "research")
            
            if not journey_name:
                flash("Please enter a journey name", "danger")
                return redirect(url_for('journey.direct_browse', persona_id=persona_id))
            
            # Create the journey
            journey_id = database.create_journey(
                name=journey_name,
                description=journey_description,
                persona_id=persona_id,
                journey_type=journey_type
            )
            
            flash(f"Journey '{journey_name}' created successfully!", "success")
        
        # Handle screenshot if provided
        screenshot_path = None
        if 'screenshot' in request.form and request.form.get('screenshot'):
            # Decode base64 screenshot
            screenshot_data = request.form.get('screenshot').split(',')[1]
            screenshot_bytes = base64.b64decode(screenshot_data)
            
            # Create screenshots directory if it doesn't exist
            screenshots_dir = os.path.join(os.getcwd(), 'screenshots')
            if not os.path.exists(screenshots_dir):
                os.makedirs(screenshots_dir)
            
            # Generate filename based on timestamp
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            screenshot_path = os.path.join('screenshots', f'journey-{journey_id}-waypoint-{timestamp}.png')
            
            # Save the screenshot
            with open(screenshot_path, 'wb') as f:
                f.write(screenshot_bytes)
        
        # Collect additional metadata
        metadata = {
            "browser_timestamp": datetime.now().isoformat(),
            "user_agent": request.headers.get('User-Agent'),
            "source": "direct_browse"
        }
        
        # Add the waypoint
        waypoint_id = database.add_waypoint(
            journey_id=journey_id,
            url=url,
            title=title,
            notes=notes,
            screenshot_path=screenshot_path,
            metadata=metadata
        )
        
        flash("Waypoint added successfully!", "success")
        
        # Redirect based on user choice
        if journey_option == "existing" or request.form.get("go_to_journey", "0") == "1":
            # Go to the journey page
            return redirect(url_for('journey.browse_journey', journey_id=journey_id))
        else:
            # Continue browsing
            return redirect(url_for('journey.direct_browse', persona_id=persona_id))
        
    except Exception as e:
        logging.error(f"Error saving waypoint: {e}")
        flash(f"Error saving waypoint: {str(e)}", "danger")
        return redirect(url_for('journey.direct_browse', persona_id=persona_id))

@journey_bp.route("/create-journey-from-browse/<int:persona_id>", methods=["POST"])
def create_journey_from_browse(persona_id):
    """Create a journey from a direct browsing session."""
    try:
        # Get form data
        name = request.form.get("name")
        description = request.form.get("description", "")
        journey_type = request.form.get("journey_type", "research")
        
        # Get URLs from the form
        visited_urls = request.form.get("visited_urls", "[]")
        current_url = request.form.get("current_url", "")
        
        try:
            # Parse the visited URLs from JSON
            visited_urls = json.loads(visited_urls)
        except Exception as e:
            logging.error(f"Error parsing visited URLs: {e}")
            visited_urls = []
        
        # Create the journey
        journey_id = database.create_journey(
            name=name,
            description=description,
            persona_id=persona_id,
            journey_type=journey_type
        )
        
        # Add waypoints for each visited URL
        for url in visited_urls:
            if url and url != "about:blank":
                # Create basic metadata
                metadata = {
                    "browser_timestamp": datetime.now().isoformat(),
                    "user_agent": request.headers.get('User-Agent'),
                }
                
                # Add the waypoint with a generic title
                database.add_waypoint(
                    journey_id=journey_id,
                    url=url,
                    title=f"Visit to {url}",
                    notes="",
                    screenshot_path=None,
                    metadata=metadata
                )
        
        # If current URL isn't in the visited URLs, add it too
        if current_url and current_url != "about:blank" and current_url not in visited_urls:
            metadata = {
                "browser_timestamp": datetime.now().isoformat(),
                "user_agent": request.headers.get('User-Agent'),
            }
            
            database.add_waypoint(
                journey_id=journey_id,
                url=current_url,
                title=f"Visit to {current_url}",
                notes="",
                screenshot_path=None,
                metadata=metadata
            )
        
        flash(f"Journey '{name}' created successfully!", "success")
        return redirect(url_for('journey.browse_journey', journey_id=journey_id))
        
    except Exception as e:
        logging.error(f"Error creating journey from browse: {e}")
        flash(f"Error creating journey: {str(e)}", "danger")
        return redirect(url_for('journey.direct_browse', persona_id=persona_id))

@journey_bp.route("/interact-as")
def interact_as():
    """Choose a persona to interact with (browse or chat)."""
    # Import inside function to avoid circular imports
    from utils.persona_client import get_client
    
    try:
        # Get personas from the API
        client = get_client()
        result = client.get_personas(page=1, per_page=100)
        personas = result.get('personas', [])
    except Exception as e:
        logging.error(f"Error getting personas from API: {e}")
        personas = []
        flash(f"Error loading personas: {str(e)}", "danger")
    
    # Get journeys from the database
    journeys = database.get_all_journeys()
    
    # Add waypoint count for each journey
    for journey in journeys:
        waypoints = database.get_waypoints(journey['id'])
        journey['waypoint_count'] = len(waypoints) if waypoints else 0
    
    # Sort journeys by most recent first
    journeys = sorted(journeys, key=lambda j: j.get('created_at', 0), reverse=True)
    
    return render_template("interact_as.html", personas=personas, journeys=journeys)

@journey_bp.route("/browse-as")
def browse_as():
    """Legacy route - redirects to interact-as."""
    return redirect(url_for('journey.interact_as'))
