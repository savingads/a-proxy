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
    return render_template("journey_list.html", journeys=journeys)

@journey_bp.route("/journey/create", methods=["GET", "POST"])
def create_journey():
    """Create a new journey."""
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
            
            flash(f"Journey '{name}' created successfully!", "success")
            return redirect(url_for('journey.view_journey', journey_id=journey_id))
        
        except Exception as e:
            logging.error(f"Error creating journey: {e}")
            flash(f"Error creating journey: {str(e)}", "danger")
    
    # Get all personas for the persona selection dropdown
    personas = database.get_all_personas()
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
    
    # Get all personas for the persona selection dropdown
    personas = database.get_all_personas()
    return render_template("journey_edit.html", journey=journey, personas=personas)

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
        persona = database.get_persona(journey['persona_id'])
    
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

@journey_bp.route("/browse-as")
def browse_as():
    """Browse as a persona by selecting a persona and journey."""
    personas = database.get_all_personas()
    journeys = database.get_all_journeys()
    return render_template("browse_as.html", personas=personas, journeys=journeys)
