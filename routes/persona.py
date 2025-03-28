from flask import Blueprint, request, redirect, url_for, flash, session, jsonify, render_template
from forms import PersonaForm
import database
import json
import logging
from utils.persona import prepare_form_object
from utils.vpn import is_vpn_running, wait_for_vpn_and_get_ip_info
from config import REGION_LANGUAGE_MAP

persona_bp = Blueprint('persona', __name__)

@persona_bp.route("/dashboard")
@persona_bp.route("/index")
def dashboard():
    """Render the dashboard with persona information."""
    # Get persona_id from URL parameter (if provided by use_persona route)
    persona_id = request.args.get('persona_id')
    form = None
    
    if persona_id:
        try:
            # Get persona data from database
            persona = database.get_persona(persona_id)
            
            # Create a form object to populate form fields
            form_obj = prepare_form_object(persona)
            
            # Create form with obj parameter to populate fields
            form = PersonaForm(obj=form_obj)
            
            # Prepare page data
            vpn_running = is_vpn_running()
            ip_info = wait_for_vpn_and_get_ip_info() if vpn_running else {}
            
            # Use language from persona if available
            language = form_obj.language
            
            # Get latitude and longitude from demographic data
            demographic = persona.get('demographic', {})
            latitude = demographic.get('latitude')
            longitude = demographic.get('longitude')
            geolocation = None
            
            # Create a geolocation string if latitude and longitude exist
            if latitude is not None and longitude is not None:
                geolocation = f"{latitude}, {longitude}"
                
                # Add latitude and longitude to ip_info to populate target fields
                if 'loc' not in ip_info:
                    ip_info = ip_info or {}
                    ip_info['loc'] = geolocation
            
            # Set fields at top of page
            flash(f"Using persona: {persona['name']}", "success")
            
            # Get language from the persona
            persona_language = demographic.get('language', 'en-US')
            
            # Set additional template variables for JavaScript to use
            extra_script = f"""
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    // Update target latitude and longitude fields
                    const targetLatitudeInput = document.getElementById('target-latitude');
                    const targetLongitudeInput = document.getElementById('target-longitude');
                    const latitudeInput = document.getElementById('latitude');
                    const longitudeInput = document.getElementById('longitude');
                    const targetLanguageSelect = document.getElementById('target-language');
                    
                    if (targetLatitudeInput && targetLongitudeInput) {{
                        targetLatitudeInput.value = "{latitude or ''}";
                        targetLongitudeInput.value = "{longitude or ''}";
                    }}
                    
                    if (latitudeInput && longitudeInput) {{
                        latitudeInput.value = "{latitude or ''}";
                        longitudeInput.value = "{longitude or ''}";
                    }}
                    
                    // Set the language dropdown to match the persona's language
                    if (targetLanguageSelect) {{
                        // Try to find the option with the matching value
                        const languageValue = "{persona_language}";
                        const options = targetLanguageSelect.options;
                        
                        let found = false;
                        for (let i = 0; i < options.length; i++) {{
                            if (options[i].value === languageValue) {{
                                targetLanguageSelect.selectedIndex = i;
                                found = true;
                                break;
                            }}
                        }}
                        
                        // If not found, dynamically add the option
                        if (!found && languageValue) {{
                            const newOption = document.createElement('option');
                            newOption.value = languageValue;
                            newOption.text = languageValue;
                            targetLanguageSelect.add(newOption);
                            targetLanguageSelect.value = languageValue;
                        }}
                        
                        // Trigger the language change event
                        const setLanguageButton = document.getElementById('set-language');
                        if (setLanguageButton) {{
                            setTimeout(function() {{
                                setLanguageButton.click();
                            }}, 700);
                        }}
                    }}
                    
                    // Trigger the geolocation update to update the map
                    const setGeoButton = document.getElementById('set-geolocation');
                    if (setGeoButton) {{
                        setTimeout(function() {{
                            setGeoButton.click();
                        }}, 500);
                    }}
                }});
            </script>
            """
            
            return render_template("index.html", 
                              form=form,
                              vpn_running=vpn_running, 
                              ip_info=ip_info, 
                              language=language,
                              persona_name=persona['name'],
                              geolocation=geolocation,
                              country=form_obj.country,
                              city=form_obj.city,
                              region=form_obj.region,
                              extra_script=extra_script)
        except Exception as e:
            logging.error(f"Error using persona: {e}")
            flash(f"Error loading persona: {str(e)}", "danger")
            
    # If no persona_id or error occurred, initialize empty form
    if form is None:
        form = PersonaForm()
    
    # Get default values
    vpn_running = is_vpn_running()
    ip_info = wait_for_vpn_and_get_ip_info() if vpn_running else {}
    country = ip_info.get("country", "")
    language = request.args.get('language') or REGION_LANGUAGE_MAP.get(country, {}).get("language", "en-US") if vpn_running else "en-US"
    
    # Handle other URL parameters for backward compatibility    
    persona_name = request.args.get("persona_name")
    geolocation = request.args.get("geolocation") or (ip_info.get("loc") if vpn_running else None)
    country = request.args.get("country") or ip_info.get("country", "")
    city = request.args.get("city") or ip_info.get("city", "")
    region = request.args.get("region") or ip_info.get("region", "")
    
    return render_template("index.html", 
                          form=form,
                          vpn_running=vpn_running, 
                          ip_info=ip_info, 
                          language=language,
                          persona_name=persona_name,
                          geolocation=geolocation,
                          country=country,
                          city=city,
                          region=region)

@persona_bp.route("/use-persona/<int:persona_id>", methods=["GET"])
def use_persona(persona_id):
    """Retrieve persona data and redirect to index page with persona_id parameter."""
    # Simply redirect to index with persona_id as a parameter
    return redirect(url_for('persona.dashboard', persona_id=persona_id))

@persona_bp.route("/personas", methods=["GET"])
def list_personas():
    """List all saved personas."""
    personas = database.get_all_personas()
    return render_template("personas.html", personas=personas)

@persona_bp.route("/save-persona", methods=["POST"])
def save_persona():
    """Save persona data to the database."""
    try:
        # Get form data
        name = request.form.get("persona_name", "Unnamed Persona")
        
        # Log form data for debugging
        logging.debug(f"Form data: {dict(request.form)}")
        
        # Create persona data structure
        persona_data = {
            "name": name,
            "demographic": {
                "geolocation": request.form.get("geolocation", ""),
                "language": request.form.get("language", "en-US"),
                "country": request.form.get("country", ""),
                "city": request.form.get("city", ""),
                "region": request.form.get("region", "")
            }
        }
        
        # Save to database
        persona_id = database.save_persona(persona_data)
        
        # Use a response object to avoid session issues
        flash(f"Persona '{name}' saved successfully!", "success")
        return redirect(url_for('persona.dashboard'))
    
    except Exception as e:
        logging.error(f"Error saving persona: {e}")
        flash(f"Error saving persona: {str(e)}", "danger")
        return redirect(url_for('persona.dashboard'))

@persona_bp.route("/delete-persona/<int:persona_id>", methods=["POST"])
def delete_persona(persona_id):
    """Delete a persona from the database."""
    try:
        # Delete the persona
        database.delete_persona(persona_id)
        
        flash(f"Persona {persona_id} deleted successfully!", "success")
        return redirect(url_for('persona.list_personas'))
    
    except Exception as e:
        logging.error(f"Error deleting persona: {e}")
        flash(f"Error deleting persona: {str(e)}", "danger")
        return redirect(url_for('persona.list_personas'))

@persona_bp.route("/save_psychographic_data", methods=["POST"])
def save_psychographic_data():
    """Save psychographic data for a persona."""
    try:
        # Get form data
        persona_id = request.form.get("persona_id")
        
        # If no persona_id is provided, create a new persona
        if not persona_id:
            # Create a new persona with a default name
            persona_data = {
                "name": "New Persona",
                "demographic": {
                    "geolocation": request.form.get("geolocation", ""),
                    "language": request.form.get("language", "en-US"),
                    "country": request.form.get("country", ""),
                    "city": request.form.get("city", ""),
                    "region": request.form.get("region", "")
                },
                "psychographic": {
                    "interests": request.form.get("interests", "").split(",") if request.form.get("interests") else [],
                    "personal_values": request.form.get("personal_values", "").split(",") if request.form.get("personal_values") else [],
                    "attitudes": request.form.get("attitudes", "").split(",") if request.form.get("attitudes") else [],
                    "lifestyle": request.form.get("lifestyle", ""),
                    "personality": request.form.get("personality", ""),
                    "opinions": request.form.get("opinions", "").split(",") if request.form.get("opinions") else []
                }
            }
            
            # Save to database
            persona_id = database.save_persona(persona_data)
            
            flash(f"New persona created with psychographic data!", "success")
            return redirect(url_for('persona.dashboard'))
        else:
            # Get the existing persona
            persona = database.get_persona(persona_id)
            
            # Update with psychographic data
            conn = database.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE psychographic_data 
                SET interests = ?, personal_values = ?, attitudes = ?, lifestyle = ?, personality = ?, opinions = ?
                WHERE persona_id = ?
                """,
                (
                    json.dumps(request.form.get("interests", "").split(",") if request.form.get("interests") else []),
                    json.dumps(request.form.get("personal_values", "").split(",") if request.form.get("personal_values") else []),
                    json.dumps(request.form.get("attitudes", "").split(",") if request.form.get("attitudes") else []),
                    request.form.get("lifestyle", ""),
                    request.form.get("personality", ""),
                    json.dumps(request.form.get("opinions", "").split(",") if request.form.get("opinions") else []),
                    persona_id
                )
            )
            
            conn.commit()
            conn.close()
            
            flash(f"Psychographic data updated for persona {persona_id}!", "success")
            return redirect(url_for('persona.dashboard'))
    
    except Exception as e:
        logging.error(f"Error saving psychographic data: {e}")
        flash(f"Error saving psychographic data: {str(e)}", "danger")
        return redirect(url_for('persona.dashboard'))

@persona_bp.route("/save_behavioral_data", methods=["POST"])
def save_behavioral_data():
    """Save behavioral data for a persona."""
    try:
        # Get form data
        persona_id = request.form.get("persona_id")
        
        # If no persona_id is provided, create a new persona
        if not persona_id:
            # Create a new persona with a default name
            persona_data = {
                "name": "New Persona",
                "demographic": {
                    "geolocation": request.form.get("geolocation", ""),
                    "language": request.form.get("language", "en-US"),
                    "country": request.form.get("country", ""),
                    "city": request.form.get("city", ""),
                    "region": request.form.get("region", "")
                },
                "behavioral": {
                    "browsing_habits": request.form.get("browsing_habits", "").split(",") if request.form.get("browsing_habits") else [],
                    "purchase_history": request.form.get("purchase_history", "").split(",") if request.form.get("purchase_history") else [],
                    "brand_interactions": request.form.get("brand_interactions", "").split(",") if request.form.get("brand_interactions") else [],
                    "device_usage": json.loads(request.form.get("device_usage", "{}")) if request.form.get("device_usage") else {},
                    "social_media_activity": json.loads(request.form.get("social_media_activity", "{}")) if request.form.get("social_media_activity") else {},
                    "content_consumption": json.loads(request.form.get("content_consumption", "{}")) if request.form.get("content_consumption") else {}
                }
            }
            
            # Save to database
            persona_id = database.save_persona(persona_data)
            
            flash(f"New persona created with behavioral data!", "success")
            return redirect(url_for('persona.dashboard'))
        else:
            # Get the existing persona
            persona = database.get_persona(persona_id)
            
            # Update with behavioral data
            conn = database.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE behavioral_data 
                SET browsing_habits = ?, purchase_history = ?, brand_interactions = ?, 
                    device_usage = ?, social_media_activity = ?, content_consumption = ?
                WHERE persona_id = ?
                """,
                (
                    json.dumps(request.form.get("browsing_habits", "").split(",") if request.form.get("browsing_habits") else []),
                    json.dumps(request.form.get("purchase_history", "").split(",") if request.form.get("purchase_history") else []),
                    json.dumps(request.form.get("brand_interactions", "").split(",") if request.form.get("brand_interactions") else []),
                    request.form.get("device_usage", "{}"),
                    request.form.get("social_media_activity", "{}"),
                    request.form.get("content_consumption", "{}"),
                    persona_id
                )
            )
            
            conn.commit()
            conn.close()
            
            flash(f"Behavioral data updated for persona {persona_id}!", "success")
            return redirect(url_for('persona.dashboard'))
    
    except Exception as e:
        logging.error(f"Error saving behavioral data: {e}")
        flash(f"Error saving behavioral data: {str(e)}", "danger")
        return redirect(url_for('persona.dashboard'))

@persona_bp.route("/save_contextual_data", methods=["POST"])
def save_contextual_data():
    """Save contextual data for a persona."""
    try:
        # Get form data
        persona_id = request.form.get("persona_id")
        
        # If no persona_id is provided, create a new persona
        if not persona_id:
            # Create a new persona with a default name
            persona_data = {
                "name": "New Persona",
                "demographic": {
                    "geolocation": request.form.get("geolocation", ""),
                    "language": request.form.get("language", "en-US"),
                    "country": request.form.get("country", ""),
                    "city": request.form.get("city", ""),
                    "region": request.form.get("region", "")
                },
                "contextual": {
                    "time_of_day": request.form.get("time_of_day", ""),
                    "day_of_week": request.form.get("day_of_week", ""),
                    "season": request.form.get("season", ""),
                    "weather": request.form.get("weather", ""),
                    "device_type": request.form.get("device_type", ""),
                    "browser_type": request.form.get("browser_type", ""),
                    "screen_size": request.form.get("screen_size", ""),
                    "connection_type": request.form.get("connection_type", "")
                }
            }
            
            # Save to database
            persona_id = database.save_persona(persona_data)
            
            flash(f"New persona created with contextual data!", "success")
            return redirect(url_for('persona.dashboard'))
        else:
            # Get the existing persona
            persona = database.get_persona(persona_id)
            
            # Update with contextual data
            conn = database.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE contextual_data 
                SET time_of_day = ?, day_of_week = ?, season = ?, weather = ?, 
                    device_type = ?, browser_type = ?, screen_size = ?, connection_type = ?
                WHERE persona_id = ?
                """,
                (
                    request.form.get("time_of_day", ""),
                    request.form.get("day_of_week", ""),
                    request.form.get("season", ""),
                    request.form.get("weather", ""),
                    request.form.get("device_type", ""),
                    request.form.get("browser_type", ""),
                    request.form.get("screen_size", ""),
                    request.form.get("connection_type", ""),
                    persona_id
                )
            )
            
            conn.commit()
            conn.close()
            
            flash(f"Contextual data updated for persona {persona_id}!", "success")
            return redirect(url_for('persona.dashboard'))
    
    except Exception as e:
        logging.error(f"Error saving contextual data: {e}")
        flash(f"Error saving contextual data: {str(e)}", "danger")
        return redirect(url_for('persona.dashboard'))
