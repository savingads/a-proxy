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
        
        # Get persona_id, journey_id and chat_mode
        persona_id = data.get('persona_id')
        journey_id = data.get('journey_id')
        chat_mode = data.get('chat_mode', 'with')
        chat_history = data.get('chat_history', [])
        
        # If user provided a system prompt, use it directly
        if not system_prompt:
            # Use the new context management system
            from services import ContextManager, PersonaContextProvider, JourneyContextProvider
            
            # Initialize context manager
            ctx_manager = ContextManager(max_tokens=8000)
            
            # Add providers
            ctx_manager.add_provider(PersonaContextProvider())
            ctx_manager.add_provider(JourneyContextProvider())
            
            # Generate the full system prompt with all context
            system_prompt = ctx_manager.get_combined_context(
                persona_id=persona_id,
                journey_id=journey_id,
                mode=chat_mode
            )
        
        # Fallback if still not set
        if not system_prompt:
            system_prompt = 'You are a helpful assistant. Answer questions concisely and accurately.'
        
        # DIRECT IMPLEMENTATION: Use Anthropic client directly instead of agent_module
        try:
            import anthropic
            
            # Create Anthropic client
            logger.info(f"Creating Anthropic client with API key: {'*' * len(ANTHROPIC_API_KEY)}")
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            
            # Prepare messages array 
            messages = []
            
            # First add any chat history if provided
            if chat_history and isinstance(chat_history, list):
                # Limit history to prevent token overflow
                max_history_messages = 10  # Adjust based on typical message length
                
                # Only use the most recent messages if history is too long
                history_to_use = chat_history[-max_history_messages:] if len(chat_history) > max_history_messages else chat_history
                
                for msg in history_to_use:
                    role = msg.get('role', '')
                    content = msg.get('content', '')
                    
                    # Map roles to Claude's expected format
                    claude_role = 'user'  # Default
                    if role == 'agent' or role == 'target':
                        claude_role = 'assistant'
                    elif role in ['user', 'persona']:
                        claude_role = 'user'
                        
                    if content and role:
                        messages.append({"role": claude_role, "content": content})
            
            # Then add the current message
            messages.append({"role": "user", "content": message})
            
            # Send message to Claude
            logger.info(f"Sending message to Claude with model: {model} and {len(messages)} messages")
            
            # Add context depth info to logs
            context_tokens = len(system_prompt.split()) * 1.3  # Rough estimate
            logger.info(f"System prompt size estimate: ~{int(context_tokens)} tokens")
            
            response = client.messages.create(
                model=model,
                system=system_prompt,
                messages=messages,
                max_tokens=4096
            )
            
            # Extract content from response
            logger.info(f"Received response from Claude")
            response_content = response.content[0].text
            
            logger.info(f"Response content: {response_content[:200]}...")
            
            # Calculate context depth for returning to client
            context_depth = {}
            if persona_id:
                context_depth["persona"] = True
            if journey_id:
                context_depth["journey"] = True
            if chat_history and len(chat_history) > 0:
                context_depth["history"] = len(chat_history)
            
            return jsonify({
                "success": True,
                "response": response_content,
                "conversation_id": conversation_id,
                "context_depth": context_depth
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
    from utils.persona_client_db import get_db_persona_client
    import database
    import json
    
    # Get URL parameters
    chat_mode = request.args.get('mode', 'with')  # 'with' or 'as'
    target_persona_id = request.args.get('target_persona_id')
    journey_id = request.args.get('journey_id')  # Get journey_id from query parameters
    waypoint_id = request.args.get('waypoint_id')  # Get waypoint_id from query parameters
    
    # Initialize chat history variables
    preloaded_chat_with_history = None
    preloaded_chat_as_history = None
    
    # If waypoint_id is provided, get the chat history from the waypoint
    if waypoint_id:
        try:
            waypoint = database.get_waypoint(waypoint_id)
            if waypoint and waypoint.get('agent_data'):
                agent_data = json.loads(waypoint.get('agent_data'))
                
                # Check if it has both modes
                if agent_data.get('has_both_modes'):
                    # Get both histories
                    preloaded_chat_with_history = agent_data.get('with_history', [])
                    preloaded_chat_as_history = agent_data.get('as_history', [])
                else:
                    # Get the history from the single mode
                    mode = agent_data.get('mode')
                    history = agent_data.get('history', [])
                    
                    if mode == 'with':
                        preloaded_chat_with_history = history
                    else:
                        preloaded_chat_as_history = history
        except Exception as e:
            logging.error(f"Error loading waypoint chat history: {e}")
            # Continue without history if there's an error
    
    # Get persona data
    persona = None
    try:
        client = get_db_persona_client()
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
    
    # Get journey info if a journey ID was provided
    journey = None
    if journey_id:
        try:
            journey = database.get_journey(journey_id)
        except Exception as e:
            logging.error(f"Error getting journey {journey_id}: {e}")
            # Continue without journey if this fails
    
    # Determine the initial chat mode based on available history
    initial_mode = chat_mode  # Use the URL parameter as default
    if preloaded_chat_with_history and not preloaded_chat_as_history:
        initial_mode = 'with'
    elif preloaded_chat_as_history and not preloaded_chat_with_history:
        initial_mode = 'as'
    # If both are present, use the URL parameter, or default to 'with'
    
    # Render the simple chat template
    return render_template(
        "simple_chat.html", 
        persona=persona, 
        target_persona=target_persona,
        available_personas=available_personas,
        chat_mode=initial_mode,  # Use determined initial mode
        persona_context=persona_context,
        journey=journey,  # Pass journey to the template
        preloaded_chat_with_history=preloaded_chat_with_history,
        preloaded_chat_as_history=preloaded_chat_as_history,
        waypoint_id=waypoint_id  # Pass the waypoint_id for reference
    )

@agent_bp.route("/direct-chat/<int:persona_id>/save", methods=["POST"])
@login_required
def save_direct_chat(persona_id):
    """Save a direct chat as a waypoint, optionally creating a journey."""
    # Always set JSON content type for consistency with AJAX requests
    response_headers = {'Content-Type': 'application/json'}
    
    try:
        # Get data from form
        title = request.form.get("title")
        notes = request.form.get("notes", "")
        chat_history = request.form.get("chat_history", "[]")
        chat_mode = request.form.get("chat_mode", "with")
        journey_option = request.form.get("journey_option")
        
        logger.info(f"Saving chat for persona {persona_id}, mode: {chat_mode}, journey option: {journey_option}")
        
        # Parse chat history
        try:
            chat_history = json.loads(chat_history)
        except Exception as parse_error:
            logger.error(f"Error parsing chat history JSON: {parse_error}")
            logger.error(f"Raw chat_history: {chat_history[:200]}...")
            # Always return JSON for consistent handling
            return jsonify({
                'success': False,
                'error': f"Invalid chat history format: {str(parse_error)}"
            }), 400, response_headers
        
        # Get or create journey
        journey_id = None
        
        if journey_option == "existing":
            # Use existing journey
            journey_id = request.form.get("journey_id")
            if not journey_id:
                error_msg = "Please select a journey"
                # For non-AJAX requests, set flash message before redirect
                if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    flash(error_msg, "danger")
                    return redirect(url_for('agent.direct_chat', persona_id=persona_id))
                # For AJAX, return JSON error
                return jsonify({'success': False, 'error': error_msg}), 400, response_headers
        else:
            # Create new journey
            journey_name = request.form.get("journey_name")
            journey_description = request.form.get("journey_description", "")
            journey_type = request.form.get("journey_type", "research")
            
            if not journey_name:
                error_msg = "Please enter a journey name"
                # For non-AJAX requests, set flash message before redirect
                if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    flash(error_msg, "danger")
                    return redirect(url_for('agent.direct_chat', persona_id=persona_id))
                # For AJAX, return JSON error
                return jsonify({'success': False, 'error': error_msg}), 400, response_headers
            
            # Create the journey
            try:
                journey_id = database.create_journey(
                    name=journey_name,
                    description=journey_description,
                    persona_id=persona_id,
                    journey_type=journey_type
                )
                logger.info(f"Created new journey: {journey_id}")
                success_msg = f"Journey '{journey_name}' created successfully!"
                if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    flash(success_msg, "success")
            except Exception as journey_error:
                logger.error(f"Error creating journey: {journey_error}")
                error_msg = f"Error creating journey: {str(journey_error)}"
                # For non-AJAX requests, set flash message before redirect
                if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    flash(error_msg, "danger")
                    return redirect(url_for('agent.direct_chat', persona_id=persona_id))
                # For AJAX, return JSON error
                return jsonify({'success': False, 'error': error_msg}), 500, response_headers
        
        # Check if we already have a waypoint for this journey with the other chat mode
        existing_waypoint = None
        if journey_id:
            # Get waypoints for this journey
            waypoints = database.get_waypoints(journey_id)
            
            # Check if any existing waypoint has a matching title but different mode
            # This handles both "Chat with X" and "Chat as X" cases
            other_mode = 'with' if chat_mode == 'as' else 'as'
            other_mode_query = f"agent://conversation/{other_mode}"
            
            for wp in waypoints:
                # Check if this is a chat waypoint with the other perspective
                if (wp.get('url', '').startswith('agent://conversation/') and 
                    wp.get('url') != f"agent://conversation/{chat_mode}"):
                    
                    # If agent_data exists, parse it to check if it's for the same conversation
                    agent_data_str = wp.get('agent_data')
                    if agent_data_str:
                        try:
                            existing_data = json.loads(agent_data_str)
                            # Consider it the same conversation if titles match (ignoring the mode part)
                            existing_title = existing_data.get('title', '')
                            if title.replace(f"Chat {chat_mode} ", "") == existing_title.replace(f"Chat {other_mode} ", ""):
                                existing_waypoint = wp
                                break
                        except:
                            # If parsing fails, continue to next waypoint
                            pass
        
        # Format current chat history into agent data format
        new_agent_data = {
            'id': str(int(time.time())),
            'title': title,
            'summary': notes,
            'history': chat_history,
            'mode': chat_mode,
            'timestamp': datetime.now().isoformat()
        }
        
        # Get appropriate waypoint type based on chat mode
        waypoint_type = 'agent' if chat_mode == 'with' else 'persona'
        
        # Create URL representation
        url = "agent://conversation/" + chat_mode
        
        try:
            if existing_waypoint:
                # We already have a waypoint for the other perspective
                waypoint_id = existing_waypoint['id']
                
                # Get existing agent data
                try:
                    existing_data = json.loads(existing_waypoint.get('agent_data', '{}'))
                    
                    # Combine the data - keep both histories
                    combined_data = {
                        'id': existing_data.get('id', str(int(time.time()))),
                        'title': title,  # Use the latest title
                        'summary': notes,  # Use the latest notes
                        'with_history': existing_data.get('history') if existing_data.get('mode') == 'with' else chat_history,
                        'as_history': existing_data.get('history') if existing_data.get('mode') == 'as' else chat_history,
                        'timestamp': datetime.now().isoformat(),
                        'has_both_modes': True  # Flag indicating this waypoint has both perspectives
                    }
                    
                    # Update the existing waypoint
                    database.update_waypoint(
                        waypoint_id=waypoint_id,
                        title=title,
                        notes=notes,
                        agent_data=json.dumps(combined_data)
                    )
                    
                    logger.info(f"Updated existing waypoint {waypoint_id} with combined chat data")
                    
                except Exception as e:
                    logger.error(f"Error parsing existing agent data: {e}")
                    # Fall back to creating a new waypoint
                    waypoint_id = database.add_waypoint(
                        journey_id=journey_id,
                        url=url,
                        title=title,
                        notes=notes,
                        type=waypoint_type,
                        agent_data=json.dumps(new_agent_data)
                    )
            else:
                # Create a new waypoint
                waypoint_id = database.add_waypoint(
                    journey_id=journey_id,
                    url=url,
                    title=title,
                    notes=notes,
                    type=waypoint_type,
                    agent_data=json.dumps(new_agent_data)
                )
            
            logger.info(f"Successfully added waypoint {waypoint_id} to journey {journey_id}")
            
            # Success response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True,
                    'waypoint_id': waypoint_id,
                    'journey_id': journey_id
                }), 200, response_headers
            
            # For non-AJAX requests
            flash("Chat saved successfully!", "success")
            return redirect(url_for('agent.direct_chat', persona_id=persona_id))
            
        except Exception as waypoint_error:
            logger.error(f"Error adding waypoint: {waypoint_error}")
            error_msg = f"Error saving chat waypoint: {str(waypoint_error)}"
            # For non-AJAX requests, set flash message before redirect
            if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                flash(error_msg, "danger")
                return redirect(url_for('agent.direct_chat', persona_id=persona_id))
            # For AJAX, return JSON error
            return jsonify({'success': False, 'error': error_msg}), 500, response_headers
    
    except Exception as e:
        logger.error(f"Error saving chat: {e}", exc_info=True)
        logger.error(f"Request form data: {request.form}")
        
        # Always return JSON for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500, response_headers
        
        # For non-AJAX requests
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
        from utils.persona_client_db import get_db_persona_client
        try:
            client = get_db_persona_client()
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
            from utils.persona_client_db import get_db_persona_client
            try:
                client = get_db_persona_client()
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
