import sqlite3
import os
import json
from datetime import datetime

# Define the database path - use data directory for persistence in Docker
DB_PATH = os.path.join('data', 'personas.db')

# Create data directory if it doesn't exist
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_db_connection():
    """Create a connection to the SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign key constraints support
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create archived websites table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS archived_websites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uri_r TEXT NOT NULL,
        persona_id INTEGER,
        archive_type TEXT NOT NULL,
        archive_location TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create mementos table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mementos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        archived_website_id INTEGER NOT NULL,
        memento_datetime TIMESTAMP NOT NULL,
        memento_location TEXT NOT NULL,
        http_status INTEGER,
        content_type TEXT,
        content_length INTEGER,
        headers TEXT,
        screenshot_path TEXT,
        internet_archive_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (archived_website_id) REFERENCES archived_websites (id) ON DELETE CASCADE
    )
    ''')
    
    # Create journeys table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS journeys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        persona_id INTEGER,
        journey_type TEXT DEFAULT 'marketing',
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create waypoints table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS waypoints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        journey_id INTEGER NOT NULL,
        url TEXT NOT NULL,
        title TEXT,
        notes TEXT,
        screenshot_path TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        sequence_number INTEGER,
        metadata TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (journey_id) REFERENCES journeys (id) ON DELETE CASCADE
    )
    ''')
    
    conn.commit()
    conn.close()

def save_archived_website(url, persona_id=None, archive_type='filesystem', archive_location=None):
    """
    Save an archived website to the database
    
    Args:
        url: The URL of the website (URI-R)
        persona_id: The ID of the persona used to visit the website (optional)
        archive_type: The type of archive (filesystem, postgres, internet_archive)
        archive_location: The path or identifier for the archive
    
    Returns:
        The ID of the newly created archived website
    """
    if not archive_location:
        # Create a default archive location based on a hash of the URL
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()
        archive_location = f"archives/{url_hash}"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            INSERT INTO archived_websites 
            (uri_r, persona_id, archive_type, archive_location, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                url,
                persona_id,
                archive_type,
                archive_location,
                datetime.now()
            )
        )
        
        archived_website_id = cursor.lastrowid
        conn.commit()
        return archived_website_id
    
    except Exception as e:
        conn.rollback()
        raise e
    
    finally:
        conn.close()

def save_memento(archived_website_id, memento_location, http_status=None, 
                content_type=None, content_length=None, headers=None, 
                screenshot_path=None, internet_archive_id=None):
    """
    Save a memento for an archived website
    
    Args:
        archived_website_id: The ID of the archived website
        memento_location: The path or identifier for this specific memento
        http_status: The HTTP status code of the response
        content_type: The Content-Type of the response
        content_length: The size of the archived content
        headers: JSON string of response headers
        screenshot_path: Path to the screenshot
        internet_archive_id: ID/URL if submitted to Internet Archive
    
    Returns:
        The ID of the newly created memento
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            INSERT INTO mementos 
            (archived_website_id, memento_datetime, memento_location, http_status, 
             content_type, content_length, headers, screenshot_path, internet_archive_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                archived_website_id,
                datetime.now(),
                memento_location,
                http_status,
                content_type,
                content_length,
                json.dumps(headers) if headers else None,
                screenshot_path,
                internet_archive_id,
                datetime.now()
            )
        )
        
        memento_id = cursor.lastrowid
        conn.commit()
        return memento_id
    
    except Exception as e:
        conn.rollback()
        raise e
    
    finally:
        conn.close()

def get_archived_website(archived_website_id):
    """
    Retrieve a specific archived website with its associated persona
    
    Args:
        archived_website_id: The ID of the archived website
    
    Returns:
        Dictionary containing the archived website data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT aw.*, p.name as persona_name
    FROM archived_websites aw
    LEFT JOIN personas p ON aw.persona_id = p.id
    WHERE aw.id = ?
    """, (archived_website_id,))
    
    archived_website = cursor.fetchone()
    if not archived_website:
        conn.close()
        return None
    
    result = dict(archived_website)
    conn.close()
    return result

def get_all_archived_websites():
    """
    Retrieve all archived websites with their associated personas
    
    Returns:
        List of dictionaries containing archived website data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT aw.*, p.name as persona_name
    FROM archived_websites aw
    LEFT JOIN personas p ON aw.persona_id = p.id
    ORDER BY aw.created_at DESC
    """)
    
    archived_websites = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return archived_websites

def get_mementos_for_website(archived_website_id):
    """
    Retrieve all mementos for a specific archived website
    
    Args:
        archived_website_id: The ID of the archived website
    
    Returns:
        List of dictionaries containing memento data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT *
    FROM mementos
    WHERE archived_website_id = ?
    ORDER BY memento_datetime DESC
    """, (archived_website_id,))
    
    mementos = [dict(row) for row in cursor.fetchall()]
    
    # Parse JSON fields
    for memento in mementos:
        if memento['headers']:
            memento['headers'] = json.loads(memento['headers'])
    
    conn.close()
    return mementos

def get_memento(memento_id):
    """
    Retrieve a specific memento
    
    Args:
        memento_id: The ID of the memento
    
    Returns:
        Dictionary containing the memento data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT m.*, aw.uri_r
    FROM mementos m
    JOIN archived_websites aw ON m.archived_website_id = aw.id
    WHERE m.id = ?
    """, (memento_id,))
    
    memento = cursor.fetchone()
    if not memento:
        conn.close()
        return None
    
    result = dict(memento)
    
    # Parse JSON fields
    if result['headers']:
        result['headers'] = json.loads(result['headers'])
    
    conn.close()
    return result

def delete_archived_website(archived_website_id):
    """
    Delete an archived website and all its associated mementos
    
    Args:
        archived_website_id: The ID of the archived website to delete
        
    Returns:
        True if successful, raises an exception otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get all memento locations before deleting for filesystem cleanup if needed
        cursor.execute("SELECT memento_location, screenshot_path FROM mementos WHERE archived_website_id = ?", 
                     (archived_website_id,))
        mementos = cursor.fetchall()
        
        # Delete the archived website (CASCADE will delete related mementos)
        cursor.execute("DELETE FROM archived_websites WHERE id = ?", (archived_website_id,))
        
        # Optionally handle filesystem cleanup for memento files
        # This part would remove the files on disk if needed
        # for memento in mementos:
        #     location = memento['memento_location']
        #     screenshot = memento['screenshot_path']
        #     # Delete files if they exist
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def create_journey(name, description=None, persona_id=None, journey_type='marketing', status='active'):
    """
    Create a new journey
    
    Args:
        name: The name of the journey
        description: A description of the journey (optional)
        persona_id: The ID of the persona associated with this journey (optional)
        journey_type: The type of journey (e.g., 'marketing', 'research') (default: 'marketing')
        status: The status of the journey (e.g., 'active', 'completed') (default: 'active')
    
    Returns:
        The ID of the newly created journey
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        now = datetime.now()
        cursor.execute(
            """
            INSERT INTO journeys 
            (name, description, persona_id, journey_type, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                description,
                persona_id,
                journey_type,
                status,
                now,
                now
            )
        )
        
        journey_id = cursor.lastrowid
        conn.commit()
        return journey_id
    
    except Exception as e:
        conn.rollback()
        raise e
    
    finally:
        conn.close()

def get_journey(journey_id):
    """
    Retrieve a specific journey with its associated persona
    
    Args:
        journey_id: The ID of the journey
    
    Returns:
        Dictionary containing the journey data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT j.*, p.name as persona_name
    FROM journeys j
    LEFT JOIN personas p ON j.persona_id = p.id
    WHERE j.id = ?
    """, (journey_id,))
    
    journey = cursor.fetchone()
    if not journey:
        conn.close()
        return None
    
    result = dict(journey)
    conn.close()
    return result

def get_all_journeys():
    """
    Retrieve all journeys with their associated personas
    
    Returns:
        List of dictionaries containing journey data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT j.*, p.name as persona_name
    FROM journeys j
    LEFT JOIN personas p ON j.persona_id = p.id
    ORDER BY j.updated_at DESC
    """)
    
    journeys = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return journeys

def update_journey(journey_id, name=None, description=None, persona_id=None, journey_type=None, status=None):
    """
    Update a journey
    
    Args:
        journey_id: The ID of the journey to update
        name: The new name of the journey (optional)
        description: The new description of the journey (optional)
        persona_id: The new persona ID for the journey (optional)
        journey_type: The new journey type (optional)
        status: The new status (optional)
    
    Returns:
        True if successful, raises an exception otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get current journey data
        cursor.execute("SELECT * FROM journeys WHERE id = ?", (journey_id,))
        journey = cursor.fetchone()
        if not journey:
            raise ValueError(f"Journey with ID {journey_id} not found")
        
        # Update only the provided fields
        updates = {}
        if name is not None:
            updates['name'] = name
        if description is not None:
            updates['description'] = description
        if persona_id is not None:
            updates['persona_id'] = persona_id
        if journey_type is not None:
            updates['journey_type'] = journey_type
        if status is not None:
            updates['status'] = status
        
        # Only update if there are changes
        if updates:
            updates['updated_at'] = datetime.now()
            
            # Construct the SQL query
            set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
            query = f"UPDATE journeys SET {set_clause} WHERE id = ?"
            
            # Prepare parameters
            params = list(updates.values()) + [journey_id]
            
            # Execute the update
            cursor.execute(query, params)
            conn.commit()
        
        return True
    
    except Exception as e:
        conn.rollback()
        raise e
    
    finally:
        conn.close()

def delete_journey(journey_id):
    """
    Delete a journey and all its associated waypoints
    
    Args:
        journey_id: The ID of the journey to delete
    
    Returns:
        True if successful, raises an exception otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get waypoint screenshot paths for potential cleanup
        cursor.execute("SELECT screenshot_path FROM waypoints WHERE journey_id = ?", (journey_id,))
        waypoints = cursor.fetchall()
        
        # Delete the journey (CASCADE will delete related waypoints)
        cursor.execute("DELETE FROM journeys WHERE id = ?", (journey_id,))
        
        # Optionally clean up screenshot files
        # for waypoint in waypoints:
        #     if waypoint['screenshot_path'] and os.path.exists(waypoint['screenshot_path']):
        #         os.remove(waypoint['screenshot_path'])
        
        conn.commit()
        return True
    
    except Exception as e:
        conn.rollback()
        raise e
    
    finally:
        conn.close()

def add_waypoint(journey_id, url, title=None, notes=None, screenshot_path=None, metadata=None):
    """
    Add a waypoint to a journey
    
    Args:
        journey_id: The ID of the journey
        url: The URL of the waypoint
        title: The title of the page/waypoint (optional)
        notes: Any notes about this waypoint (optional)
        screenshot_path: Path to a screenshot of the page (optional)
        metadata: JSON string of additional metadata (optional)
    
    Returns:
        The ID of the newly created waypoint
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get the count of existing waypoints to determine sequence number
        cursor.execute("SELECT COUNT(*) as count FROM waypoints WHERE journey_id = ?", (journey_id,))
        count = cursor.fetchone()['count']
        sequence_number = count + 1
        
        cursor.execute(
            """
            INSERT INTO waypoints 
            (journey_id, url, title, notes, screenshot_path, timestamp, sequence_number, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                journey_id,
                url,
                title,
                notes,
                screenshot_path,
                datetime.now(),
                sequence_number,
                json.dumps(metadata) if metadata else None,
                datetime.now()
            )
        )
        
        waypoint_id = cursor.lastrowid
        
        # Update the journey's updated_at timestamp
        cursor.execute(
            "UPDATE journeys SET updated_at = ? WHERE id = ?",
            (datetime.now(), journey_id)
        )
        
        conn.commit()
        return waypoint_id
    
    except Exception as e:
        conn.rollback()
        raise e
    
    finally:
        conn.close()

def get_waypoints(journey_id):
    """
    Get all waypoints for a journey
    
    Args:
        journey_id: The ID of the journey
    
    Returns:
        List of dictionaries containing waypoint data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT *
    FROM waypoints
    WHERE journey_id = ?
    ORDER BY sequence_number ASC
    """, (journey_id,))
    
    waypoints = [dict(row) for row in cursor.fetchall()]
    
    # Parse metadata JSON if present and convert timestamp to datetime
    for waypoint in waypoints:
        if waypoint['metadata']:
            waypoint['metadata'] = json.loads(waypoint['metadata'])
        # Convert the timestamp string to a datetime object
        if waypoint['timestamp'] and isinstance(waypoint['timestamp'], str):
            try:
                waypoint['timestamp'] = datetime.fromisoformat(waypoint['timestamp'].replace('Z', '+00:00'))
            except ValueError:
                # If we can't parse it, leave it as is
                pass
    
    conn.close()
    return waypoints

def get_waypoint(waypoint_id):
    """
    Get a specific waypoint
    
    Args:
        waypoint_id: The ID of the waypoint
    
    Returns:
        Dictionary containing the waypoint data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT w.*, j.name as journey_name
    FROM waypoints w
    JOIN journeys j ON w.journey_id = j.id
    WHERE w.id = ?
    """, (waypoint_id,))
    
    waypoint = cursor.fetchone()
    if not waypoint:
        conn.close()
        return None
    
    result = dict(waypoint)
    
    # Parse metadata JSON if present
    if result['metadata']:
        result['metadata'] = json.loads(result['metadata'])
    
    conn.close()
    return result

def update_waypoint(waypoint_id, title=None, notes=None, sequence_number=None):
    """
    Update a waypoint
    
    Args:
        waypoint_id: The ID of the waypoint to update
        title: The new title (optional)
        notes: The new notes (optional)
        sequence_number: The new sequence number (optional)
    
    Returns:
        True if successful, raises an exception otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get current waypoint data
        cursor.execute("SELECT * FROM waypoints WHERE id = ?", (waypoint_id,))
        waypoint = cursor.fetchone()
        if not waypoint:
            raise ValueError(f"Waypoint with ID {waypoint_id} not found")
        
        # Update only the provided fields
        updates = {}
        if title is not None:
            updates['title'] = title
        if notes is not None:
            updates['notes'] = notes
        if sequence_number is not None:
            updates['sequence_number'] = sequence_number
        
        # Only update if there are changes
        if updates:
            # Construct the SQL query
            set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
            query = f"UPDATE waypoints SET {set_clause} WHERE id = ?"
            
            # Prepare parameters
            params = list(updates.values()) + [waypoint_id]
            
            # Execute the update
            cursor.execute(query, params)
            
            # Update the journey's updated_at timestamp
            cursor.execute(
                """
                UPDATE journeys 
                SET updated_at = ? 
                WHERE id = (SELECT journey_id FROM waypoints WHERE id = ?)
                """,
                (datetime.now(), waypoint_id)
            )
            
            conn.commit()
        
        return True
    
    except Exception as e:
        conn.rollback()
        raise e
    
    finally:
        conn.close()

def delete_waypoint(waypoint_id):
    """
    Delete a waypoint
    
    Args:
        waypoint_id: The ID of the waypoint to delete
    
    Returns:
        True if successful, raises an exception otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get the journey_id and screenshot_path before deleting
        cursor.execute("SELECT journey_id, screenshot_path FROM waypoints WHERE id = ?", (waypoint_id,))
        waypoint = cursor.fetchone()
        if not waypoint:
            raise ValueError(f"Waypoint with ID {waypoint_id} not found")
        
        journey_id = waypoint['journey_id']
        screenshot_path = waypoint['screenshot_path']
        
        # Delete the waypoint
        cursor.execute("DELETE FROM waypoints WHERE id = ?", (waypoint_id,))
        
        # Update sequence numbers for remaining waypoints in this journey
        cursor.execute(
            """
            UPDATE waypoints 
            SET sequence_number = sequence_number - 1 
            WHERE journey_id = ? AND sequence_number > (
                SELECT sequence_number FROM waypoints WHERE id = ?
            )
            """,
            (journey_id, waypoint_id)
        )
        
        # Update the journey's updated_at timestamp
        cursor.execute(
            "UPDATE journeys SET updated_at = ? WHERE id = ?",
            (datetime.now(), journey_id)
        )
        
        # Optionally delete the screenshot file
        # if screenshot_path and os.path.exists(screenshot_path):
        #     os.remove(screenshot_path)
        
        conn.commit()
        return True
    
    except Exception as e:
        conn.rollback()
        raise e
    
    finally:
        conn.close()

# Settings-related functions
def get_setting(key, default=None):
    """
    Get a setting value from the database.
    
    Args:
        key: The setting key
        default: Default value if setting doesn't exist
    
    Returns:
        The setting value or default if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return result['value']
    return default

def set_setting(key, value, description=None):
    """
    Set a setting value in the database.
    
    Args:
        key: The setting key
        value: The setting value
        description: Optional description of the setting
    
    Returns:
        True if successful
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if the setting already exists
        cursor.execute("SELECT key FROM settings WHERE key = ?", (key,))
        exists = cursor.fetchone()
        
        if exists:
            # Update existing setting
            cursor.execute(
                "UPDATE settings SET value = ?, updated_at = ? WHERE key = ?",
                (value, datetime.now(), key)
            )
        else:
            # Insert new setting
            cursor.execute(
                "INSERT INTO settings (key, value, description, updated_at) VALUES (?, ?, ?, ?)",
                (key, value, description, datetime.now())
            )
        
        conn.commit()
        return True
    
    except Exception as e:
        conn.rollback()
        raise e
    
    finally:
        conn.close()

def get_all_settings():
    """
    Get all settings from the database.
    
    Returns:
        List of dictionaries containing setting data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM settings ORDER BY key")
    settings = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return settings

def init_default_settings():
    """Initialize default settings if they don't exist"""
    # Internet Archive settings
    set_setting('internet_archive_enabled', 'true', 'Enable Internet Archive integration')
    set_setting('internet_archive_rate_limit', '10', 'Maximum Internet Archive submissions per day')
    set_setting('internet_archive_submissions_today', '0', 'Number of Internet Archive submissions made today')
    set_setting('internet_archive_last_reset', datetime.now().strftime('%Y-%m-%d'), 'Last date the submission counter was reset')

# Initialize the database when the module is imported
init_db()

# Add settings table if it doesn't exist
def init_settings_table():
    """Initialize the settings table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT,
        description TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

init_settings_table()
init_default_settings()
