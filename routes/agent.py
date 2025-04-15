from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, current_app
import logging
import json
import database
import sys
import os
import time
from datetime import datetime

# Add agent_module to the path
sys.path.append(os.path.join(os.getcwd(), 'agent_module'))

# Create blueprint
agent_bp = Blueprint('agent', __name__)
logger = logging.getLogger(__name__)

@agent_bp.route("/direct-chat/<int:persona_id>")
def direct_chat(persona_id):
    """Start a direct chat session with or as a persona without creating a journey."""
    # Import inside function to avoid circular imports
    from utils.persona_client import get_client
    
    # Get URL parameters
    chat_mode = request.args.get('mode', 'with')  # 'with' or 'as'
    target_persona_id = request.args.get('target_persona_id')
    
    # Get persona data
    persona = None
    try:
        client = get_client()
        persona = client.get_persona(persona_id)
        if not persona:
            flash("Persona not found", "danger")
            return redirect(url_for('journey.interact_as'))
    except Exception as e:
        logging.error(f"Error getting persona {persona_id}: {e}")
        flash(f"Error loading persona: {str(e)}", "danger")
        return redirect(url_for('journey.interact_as'))
    
    # Get target persona if specified
    target_persona = None
    if target_persona_id:
        try:
            target_persona = client.get_persona(target_persona_id)
        except Exception as e:
            logging.error(f"Error getting target persona {target_persona_id}: {e}")
            # We'll continue without target persona if it fails
    
    # Get available personas for target selector (excluding current persona)
    available_personas = []
    try:
        result = client.get_personas(page=1, per_page=100)
        personas_list = result.get('personas', [])
        # Filter out current persona
        available_personas = [p for p in personas_list if p['id'] != persona_id]
    except Exception as e:
        logging.error(f"Error getting personas: {e}")
        # Continue with empty list if this fails
    
    # Render the simple chat template
    return render_template(
        "simple_chat.html", 
        persona=persona, 
        target_persona=target_persona,
        available_personas=available_personas,
        chat_mode=chat_mode
    )

@agent_bp.route("/direct-chat/<int:persona_id>/save", methods=["POST"])
def save_direct_chat(persona_id):
    """Save a direct chat as a waypoint, optionally creating a journey."""
    try:
        # Get data from form
        title = request.form.get("title")
        notes = request.form.get("notes", "")
        chat_history = request.form.get("chat_history", "[]")
        chat_mode = request.form.get("chat_mode", "with")
        journey_option = request.form.get("journey_option")
        
        # Parse chat history
        try:
            chat_history = json.loads(chat_history)
        except:
            chat_history = []
        
        # Get or create journey
        journey_id = None
        
        if journey_option == "existing":
            # Use existing journey
            journey_id = request.form.get("journey_id")
            if not journey_id:
                flash("Please select a journey", "danger")
                return redirect(url_for('agent.direct_chat', persona_id=persona_id))
        else:
            # Create new journey
            journey_name = request.form.get("journey_name")
            journey_description = request.form.get("journey_description", "")
            journey_type = request.form.get("journey_type", "research")
            
            if not journey_name:
                flash("Please enter a journey name", "danger")
                return redirect(url_for('agent.direct_chat', persona_id=persona_id))
            
            # Create the journey
            journey_id = database.create_journey(
                name=journey_name,
                description=journey_description,
                persona_id=persona_id,
                journey_type=journey_type
            )
            
            flash(f"Journey '{journey_name}' created successfully!", "success")
        
        # Format chat history into agent data format
        agent_data = {
            'id': str(int(time.time())),
            'title': title,
            'summary': notes,
            'history': chat_history,
            'mode': chat_mode,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add the waypoint with type 'agent' or 'persona' based on chat mode
        waypoint_type = 'agent' if chat_mode == 'with' else 'persona'
        
        # Create URL representation
        url = "agent://conversation/" + (chat_mode or 'with')
        
        waypoint_id = database.add_waypoint(
            journey_id=journey_id,
            url=url,
            title=title,
            notes=notes,
            type=waypoint_type,
            agent_data=json.dumps(agent_data)
        )
        
        flash("Chat saved successfully!", "success")
        
        # JSON response for AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'waypoint_id': waypoint_id,
                'journey_id': journey_id
            })
        
        # Normal redirect response
        return redirect(url_for('agent.direct_chat', persona_id=persona_id))
    
    except Exception as e:
        logging.error(f"Error saving chat: {e}")
        
        # JSON response for AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
        
        flash(f"Error saving chat: {str(e)}", "danger")
        return redirect(url_for('agent.direct_chat', persona_id=persona_id))

@agent_bp.route("/journey/<int:journey_id>/agent")
def journey_agent(journey_id):
    """Show the agent interface for a journey."""
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
            flash(f"Error loading persona: {str(e)}", "warning")
    
    return render_template("agent_waypoint.html", journey=journey, persona=persona)

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
        
        # Import here to avoid circular imports
        from utils.agent import get_agent_service
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
        # Import here to avoid circular imports
        from utils.agent import get_agent_service
        
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
