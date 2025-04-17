from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, current_app
import logging
import json
import database
import sys
import os
import time
from datetime import datetime
from flask_login import login_required

# Add agent_module to the path
sys.path.append(os.path.join(os.getcwd(), 'agent_module'))

# Create blueprint
agent_bp = Blueprint('agent', __name__)
logger = logging.getLogger(__name__)

@agent_bp.route("/agent")
@login_required
def agent_chat():
    """Show the standalone Claude agent interface."""
    return render_template("agent_chat.html")

from services import fetch_persona_context, flatten_persona_context, persona_context_to_system_prompt

@agent_bp.route("/agent/message", methods=["POST"])
@login_required
def standalone_agent_message():
    """Process a message to the standalone Claude agent."""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            logger.error("No JSON data provided in request")
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        logger.info(f"Received agent message request: {json.dumps(data)[:200]}...")
        
        message = data.get('message')
        conversation_id = data.get('conversation_id')
        model = data.get('model', 'claude-3-opus-20240229')
        system_prompt = data.get('system_prompt')
        
        if not message:
            logger.error("No message provided in request data")
            return jsonify({"success": False, "error": "No message provided"}), 400
        
        # Check for API key
        from config import ANTHROPIC_API_KEY
        if not ANTHROPIC_API_KEY:
            logger.error("ANTHROPIC_API_KEY is not set. Please set it in the environment or config.py")
            return jsonify({
                "success": False, 
                "error": "Claude API key is not configured. Please set ANTHROPIC_API_KEY in your environment or config.py."
            }), 500
        
        # Get persona_id and chat_mode if provided (for direct chat)
        persona_id = data.get('persona_id')
        chat_mode = data.get('chat_mode', 'with')
        
        # If persona_id is provided, generate system prompt from persona context
        if persona_id and not system_prompt:
            raw_context = fetch_persona_context(persona_id)
            persona_context = flatten_persona_context(raw_context)
            system_prompt = persona_context_to_system_prompt(persona_context, mode=chat_mode)
        
        # Fallback if still not set
        if not system_prompt:
            system_prompt = 'You are a helpful assistant. Answer questions concisely and accurately.'
        
        # DIRECT IMPLEMENTATION: Use Anthropic client directly instead of agent_module
        try:
            import anthropic
            
            # Create Anthropic client
            logger.info(f"Creating Anthropic client with API key: {'*' * len(ANTHROPIC_API_KEY)}")
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            
            # Send message to Claude
            logger.info(f"Sending message to Claude with model: {model}")
            response = client.messages.create(
                model=model,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": message}
                ],
                max_tokens=4096
            )
            
            # Extract content from response
            logger.info(f"Received response from Claude")
            response_content = response.content[0].text
            
            logger.info(f"Response content: {response_content[:200]}...")
            
            return jsonify({
                "success": True,
                "response": response_content,
                "conversation_id": conversation_id
            })
        except Exception as e:
            logger.error(f"Error calling Claude API directly: {e}", exc_info=True)
            raise
    
    except Exception as e:
        logger.error(f"Error processing agent message: {e}", exc_info=True)
        import traceback
        trace = traceback.format_exc()
        logger.error(f"Traceback: {trace}")
        return jsonify({"success": False, "error": str(e)}), 500

from services import fetch_persona_context

def flatten_persona_context(raw_context):
    """
    Flatten all persona fields for sidebar/system prompt display.
    Returns a dict with Demographic, Psychographic, Behavioral, Contextual as sub-dicts.
    """
    if not raw_context:
        return {}
    demographic = raw_context.get("demographic", {})
    psychographic = raw_context.get("psychographic", {})
    behavioral = raw_context.get("behavioral", {})
    contextual = raw_context.get("contextual", {})
    # Convert lists to comma-separated strings for compactness
    def compact(d):
        return {k: ", ".join(v) if isinstance(v, list) else v for k, v in d.items()}
    return {
        "Demographic": compact(demographic),
        "Psychographic": compact(psychographic),
        "Behavioral": compact(behavioral),
        "Contextual": compact(contextual)
    }

@agent_bp.route("/direct-chat/<int:persona_id>")
@login_required
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
    
    # Fetch persona context for sidebar display
    persona_context = None
    try:
        raw_context = fetch_persona_context(persona_id)
        persona_context = flatten_persona_context(raw_context)
    except Exception as e:
        logging.error(f"Error fetching persona context for sidebar: {e}")
    
    # Render the simple chat template
    return render_template(
        "simple_chat.html", 
        persona=persona, 
        target_persona=target_persona,
        available_personas=available_personas,
        chat_mode=chat_mode,
        persona_context=persona_context
    )

@agent_bp.route("/direct-chat/<int:persona_id>/save", methods=["POST"])
@login_required
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
@login_required
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
@login_required
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
        
        # Get persona data if available
        persona = None
        if journey['persona_id']:
            # Import inside function to avoid circular imports
            from utils.persona_client import get_client
            try:
                client = get_client()
                persona = client.get_persona(journey['persona_id'])
            except Exception as e:
                logging.error(f"Error getting persona {journey['persona_id']}: {e}")
        
        # Prepare context for Claude
        claude_context = {
            'journey': journey,
            'waypoints': waypoints,
            'persona': persona
        }
        
        # Get agent service
        from utils.agent import get_agent_service
        agent_service = get_agent_service()
        
        # Send message to Claude
        claude_response = agent_service.send_message(message, claude_context)
        
        # Extract content from response
        response_content = claude_response.get('content', 'I apologize, but I wasn\'t able to process your request.')
        
        return jsonify({
            "success": True,
            "response": response_content,
            "conversation_id": conversation_id
        })
    
    except Exception as e:
        logger.error(f"Error processing agent message: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@agent_bp.route("/journey/<int:journey_id>/agent/save", methods=["POST"])
@login_required
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
