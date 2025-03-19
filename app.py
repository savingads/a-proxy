from flask import Flask, jsonify, render_template, request, redirect, url_for, Response, flash
import subprocess
import requests
import logging
import os
import json
from services import start_vpn, start_vpn_service
import multiprocessing
from requests.exceptions import ConnectionError
import time
import database

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_testing')

# Configure session to avoid the 'partitioned' keyword issue
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

logging.basicConfig(level=logging.DEBUG)

REGION_LANGUAGE_MAP = {
    "US": {
        "name": "United States",
        "language": "en-US",
        "geolocation": "37.0902,-95.7129",
        "server": "us123.nordvpn.com.udp"
    },
    "BR": {
        "name": "Brazil",
        "language": "pt-BR",
        "geolocation": "-14.2350,-51.9253",
        "server": "br123.nordvpn.com.udp"
    },
    "DE": {
        "name": "Germany",
        "language": "de-DE",
        "geolocation": "51.1657,10.4515",
        "server": "de123.nordvpn.com.udp"
    },
    "JP": {
        "name": "Japan",
        "language": "ja-JP",
        "geolocation": "36.2048,138.2529",
        "server": "jp123.nordvpn.com.udp"
    },
    "ZA": {
        "name": "South Africa",
        "language": "af-ZA",
        "geolocation": "-30.5595,22.9375",
        "server": "za123.nordvpn.com.udp"
    }
}

def is_vpn_running():
    result = subprocess.run(["pgrep", "openvpn"], stdout=subprocess.PIPE)
    return result.returncode == 0

def get_ip_info():
    retries = 3
    backoff_factor = 2
    for attempt in range(retries):
        try:
            response = requests.get("https://ipinfo.io")
            response.raise_for_status()
            return response.json()
        except ConnectionError as e:
            logging.error(f"Failed to get IP info: {e}")
            return {"error": "Failed to get IP info"}
        except requests.exceptions.RequestException as e:
            logging.error(f"Request exception: {e}")
            if response.status_code == 429:  # Too Many Requests
                wait_time = backoff_factor ** attempt
                logging.debug(f"Rate limited. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return {"error": "Request exception"}
    return {"error": "Failed to get IP info after retries"}

def wait_for_vpn_and_get_ip_info():
    retries = 5
    backoff_factor = 2
    for attempt in range(retries):
        if is_vpn_running():
            ip_info = get_ip_info()
            if "error" not in ip_info:
                return ip_info
        wait_time = backoff_factor ** attempt
        logging.debug(f"Waiting for VPN to establish. Retrying in {wait_time} seconds...")
        time.sleep(wait_time)
    return {"error": "Failed to get IP info after retries"}

@app.route("/vpn-status")
def vpn_status():
    vpn_running = is_vpn_running()
    ip_info = get_ip_info() if vpn_running else {}
    return jsonify({
        "vpn_running": vpn_running,
        "ip_info": ip_info
    })

@app.route("/")
@app.route("/home")
def home():
    vpn_running = is_vpn_running()
    ip_info = wait_for_vpn_and_get_ip_info() if vpn_running else {}
    country = ip_info.get("country", "")
    language = REGION_LANGUAGE_MAP.get(country, "en-US") if vpn_running else "en-US"
    return render_template("home.html", vpn_running=vpn_running, ip_info=ip_info, language=language)

@app.route("/dashboard")
@app.route("/index")
def index():
    vpn_running = is_vpn_running()
    ip_info = wait_for_vpn_and_get_ip_info() if vpn_running else {}
    country = ip_info.get("country", "")
    language = REGION_LANGUAGE_MAP.get(country, "en-US") if vpn_running else "en-US"
    return render_template("index.html", vpn_running=vpn_running, ip_info=ip_info, language=language)

@app.route("/visit-page", methods=["POST"])
def visit_page():
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

@app.route("/archive_page", methods=["POST"])
def archive_page():
    #language = request.form.get("language", "en-US")
    #os.system(f"python3 /home/chris/a-proxy/archive_page.py {language}")
    return "Archived Page."

@app.route("/geolocation-test")
def geolocation_test():
    """Render the geolocation test page"""
    # Get query parameters if they exist (these would be passed when accessing directly)
    target_language = request.args.get("language", "Not specified")
    target_geolocation = request.args.get("geolocation", "Not specified")
    return render_template("geolocation_test.html", 
                          target_language=target_language,
                          target_geolocation=target_geolocation)

@app.route("/get-headers")
def get_headers():
    """Return the request headers as JSON"""
    headers = dict(request.headers)
    return jsonify({"accept-language": headers.get("Accept-Language", "Not available")})

@app.route("/test-geolocation", methods=["POST"])
def test_geolocation():
    """Open a browser with the specified geolocation and language settings"""
    language = request.form.get("language", "en-US")
    geolocation = request.form.get("geolocation", None)
    
    # Get the port from the request
    port = request.host.split(':')[-1] if ':' in request.host else '5000'
    
    # Build the command to open the geolocation test page with query parameters
    test_url = f"http://localhost:{port}/geolocation-test?language={language}"
    if geolocation:
        test_url += f"&geolocation={geolocation}"
    
    command = f"python3 /home/chris/a-proxy/visit_page.py '{test_url}' --language '{language}'"
    if geolocation:
        command += f" --geolocation '{geolocation}'"
    
    logging.debug(f"Executing command: {command}")
    os.system(command)
    
    return f"Testing geolocation with language {language} and coordinates {geolocation or 'not specified'}. Screenshot saved."

def vpn_process(region=None):
    if is_vpn_running():
        logging.debug("Stopping current VPN connection")
        subprocess.run(["sudo", "pkill", "openvpn"])
        time.sleep(5)  # Wait for the VPN process to stop
    if region:
        vpn_config_path = f"nordvpn/ovpn_udp/{region}.nordvpn.com.udp.ovpn"
        if not os.path.exists(vpn_config_path):
            logging.error(f"VPN configuration file not found: {vpn_config_path}")
            return
        auth_file_path = "nordvpn/auth.txt"
        if not os.path.exists(auth_file_path):
            logging.error(f"VPN authentication file not found: {auth_file_path}")
            return
        logging.debug(f"Starting VPN with configuration: {vpn_config_path} and auth file: {auth_file_path}")
        subprocess.run(["sudo", "openvpn", "--config", vpn_config_path, "--auth-user-pass", auth_file_path])
    else:
        start_vpn_service()  # Start the VPN service without connecting to a region

@app.route("/change-region", methods=["POST"])
def change_region():
    region = request.form.get("region")
    logging.debug(f"Changing VPN region to: {region}")
    vpn_proc = multiprocessing.Process(target=vpn_process, args=(region,))
    vpn_proc.start()
    logging.debug("VPN region change process started")
    return jsonify({"status": "changing", "region": region})

@app.route("/get-region-geolocation/<region_code>")
def get_region_geolocation(region_code):
    region_code = region_code.upper()
    if region_code in REGION_LANGUAGE_MAP:
        return jsonify({
            "geolocation": REGION_LANGUAGE_MAP[region_code]["geolocation"],
            "name": REGION_LANGUAGE_MAP[region_code]["name"]
        })
    return jsonify({"error": "Region not found"}), 404

@app.route("/start_vpn", methods=["POST"])
def start_vpn_route():
    if 'region' not in request.form:
        return jsonify({"error": "No region provided"}), 400
    region = request.form['region']
    # Logic to start the VPN with the selected region
    vpn_proc = multiprocessing.Process(target=vpn_process, args=(region,))
    vpn_proc.start()
    return redirect(url_for('index'))

@app.route("/save-persona", methods=["POST"])
def save_persona():
    """Save persona data to the database"""
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
        response = redirect(url_for('index'))
        response.set_cookie('flash_message', f"Persona '{name}' saved successfully!")
        return response
    
    except Exception as e:
        logging.error(f"Error saving persona: {e}")
        # Use a response object to avoid session issues
        response = redirect(url_for('index'))
        response.set_cookie('flash_message', f"Error saving persona: {str(e)}")
        return response

@app.route("/save_psychographic_data", methods=["POST"])
def save_psychographic_data():
    """Save psychographic data for a persona"""
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
            
            # Use a response object to avoid session issues
            response = redirect(url_for('index'))
            response.set_cookie('flash_message', f"New persona created with psychographic data!")
            return response
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
            
            # Use a response object to avoid session issues
            response = redirect(url_for('index'))
            response.set_cookie('flash_message', f"Psychographic data updated for persona {persona_id}!")
            return response
    
    except Exception as e:
        logging.error(f"Error saving psychographic data: {e}")
        # Use a response object to avoid session issues
        response = redirect(url_for('index'))
        response.set_cookie('flash_message', f"Error saving psychographic data: {str(e)}")
        return response

@app.route("/save_behavioral_data", methods=["POST"])
def save_behavioral_data():
    """Save behavioral data for a persona"""
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
            
            # Use a response object to avoid session issues
            response = redirect(url_for('index'))
            response.set_cookie('flash_message', f"New persona created with behavioral data!")
            return response
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
            
            # Use a response object to avoid session issues
            response = redirect(url_for('index'))
            response.set_cookie('flash_message', f"Behavioral data updated for persona {persona_id}!")
            return response
    
    except Exception as e:
        logging.error(f"Error saving behavioral data: {e}")
        # Use a response object to avoid session issues
        response = redirect(url_for('index'))
        response.set_cookie('flash_message', f"Error saving behavioral data: {str(e)}")
        return response

@app.route("/save_contextual_data", methods=["POST"])
def save_contextual_data():
    """Save contextual data for a persona"""
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
            
            # Use a response object to avoid session issues
            response = redirect(url_for('index'))
            response.set_cookie('flash_message', f"New persona created with contextual data!")
            return response
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
            
            # Use a response object to avoid session issues
            response = redirect(url_for('index'))
            response.set_cookie('flash_message', f"Contextual data updated for persona {persona_id}!")
            return response
    
    except Exception as e:
        logging.error(f"Error saving contextual data: {e}")
        # Use a response object to avoid session issues
        response = redirect(url_for('index'))
        response.set_cookie('flash_message', f"Error saving contextual data: {str(e)}")
        return response

@app.route("/delete-persona/<int:persona_id>", methods=["POST"])
def delete_persona(persona_id):
    """Delete a persona from the database"""
    try:
        # Delete the persona
        database.delete_persona(persona_id)
        
        # Use a response object to avoid session issues
        response = redirect(url_for('list_personas'))
        response.set_cookie('flash_message', f"Persona {persona_id} deleted successfully!")
        return response
    
    except Exception as e:
        logging.error(f"Error deleting persona: {e}")
        # Use a response object to avoid session issues
        response = redirect(url_for('list_personas'))
        response.set_cookie('flash_message', f"Error deleting persona: {str(e)}")
        return response

@app.route("/personas", methods=["GET"])
def list_personas():
    """List all saved personas"""
    personas = database.get_all_personas()
    return render_template("personas.html", personas=personas)

if __name__ == "__main__":
    # Automatically start the VPN service without connecting to a region
    #if not is_vpn_running():
       # logging.debug("Starting VPN service without connecting to a region")
       # vpn_proc = multiprocessing.Process(target=vpn_process)
       # vpn_proc.start()
    
    import argparse
    parser = argparse.ArgumentParser(description='Run the Flask application')
    parser.add_argument('--port', type=int, default=5001, help='Port to run the application on')
    args = parser.parse_args()
    
    app.run(debug=True, use_reloader=True, port=args.port)
