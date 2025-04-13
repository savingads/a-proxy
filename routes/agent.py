from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, current_app
import logging
import json
from utils.agent import get_agent_service
import database
import sys
import os

# Add agent_module to the path
sys.path.append(os.path.join(os.getcwd(), 'agent_module'))

agent_bp = Blueprint('agent', __name__)
logger = logging.getLogger(__name__)

@agent_bp.route("/journey/<int:journey_id>/agent")
def journey_agent(journey_id):
    """Show the agent interface for a journey."""
    journey = database.get_journey(journey_id)
    if not journey:
        flash("Journey not found", "danger")
        return redirect(url_for('journey.list_journeys'))
    
    return render_template("agent_waypoint.html", journey=journey)

@agent_bp.route("/journey/<int:journey_id>/agent/message", methods=["POST"])
def agent_message(journey_id):
    """Process a message to the agent."""
    try:
        # Get journey
        journey = database.get_journey(journey_id)
        if not journey:
            return jsonify({"success": False, "error": "Journey not found"}), 404
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        message = data.get('message')
        conversation_id = data.get('conversation_id')
        
        if not message:
            return jsonify({"success": False, "error": "No message provided"}), 400
        
        # Get additional context for the agent
        waypoints = database.get_waypoints(journey_id)
        
        # TODO: In a real implementation, we would process the message through
        # the agent_module and get a response. For now, we'll use a simple mock.
        
        # Mock response for testing
        response = f"I received your message: '{message}'. This is a simulated response from the agent. " \
                  f"Your journey '{journey['name']}' has {len(waypoints)} waypoints."
        
        return jsonify({
            "success": True,
            "response": response,
            "conversation_id": conversation_id
        })
    
    except Exception as e:
        logger.error(f"Error processing agent message: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@agent_bp.route("/journey/<int:journey_id>/agent/save", methods=["POST"])
def save_agent_conversation(journey_id):
    """Save an agent conversation as a waypoint."""
    try:
        # Get journey
        journey = database.get_journey(journey_id)
        if not journey:
            return jsonify({"success": False, "error": "Journey not found"}), 404
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        title = data.get('title', 'Agent Conversation')
        notes = data.get('notes', '')
        conversation_id = data.get('conversation_id')
        conversation_history = data.get('conversation_history', [])
        
        if not conversation_history:
            return jsonify({"success": False, "error": "No conversation history provided"}), 400
        
        # Format conversation data
        conversation_data = {
            'id': conversation_id,
            'history': conversation_history,
            'summary': notes,
            'title': title,
            'timestamp': conversation_history[-1].get('timestamp') if conversation_history else None
        }
        
        # Get agent service
        agent_service = get_agent_service()
        
        # Save conversation as waypoint
        waypoint_id = agent_service.save_conversation(
            journey_id=journey_id,
            conversation_data=conversation_data
        )
        
        return jsonify({
            "success": True,
            "waypoint_id": waypoint_id,
            "message": "Conversation saved successfully"
        })
    
    except Exception as e:
        logger.error(f"Error saving agent conversation: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@agent_bp.route("/agent-blueprint")
def register_blueprint():
    """Register the agent blueprint."""
    try:
        # Get agent service
        agent_service = get_agent_service()
        
        # Create the agent blueprint
        agent_bp = agent_service.create_agent_blueprint()
        
        # Register with current app
        current_app.register_blueprint(agent_bp)
        
        return jsonify({"success": True, "message": "Agent blueprint registered successfully"})
    except Exception as e:
        logger.error(f"Error registering agent blueprint: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
